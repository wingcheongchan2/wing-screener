import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ==========================================
# 1. 系統設置 & CSS (黑金極致風格)
# ==========================================
st.set_page_config(page_title="J Law Alpha Trader", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    div.stButton > button:first-child {
        background-color: #00D084; color: #000; border-radius: 4px; font-weight: 800; border: none;
    }
    .metric-box {
        background-color: #1A1C24; padding: 15px; border-radius: 8px; border-left: 4px solid #00D084;
        text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 10px;
    }
    .metric-value { font-size: 22px; font-weight: bold; color: #fff; }
    .metric-label { font-size: 13px; color: #888; text-transform: uppercase; letter-spacing: 1px;}
    .badge-bull { background-color: #006400; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
    .badge-bear { background-color: #8B0000; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
    .badge-warn { background-color: #B8860B; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 J Law Alpha Trader：實戰獲利系統")
st.markdown("---")

# ==========================================
# 2. 核心邏輯升級
# ==========================================

# 獲取股票池
@st.cache_data
def get_tickers(mode):
    # 這裡只放真正的強勢股池，垃圾股不要看
    tech_leaders = ["NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "TSLA", "AMD", "AVGO", "COST", "NFLX", "SMCI", "ARM", "PLTR", "COIN", "MSTR"]
    semi_leaders = ["AMAT", "LRCX", "KLAC", "MU", "QCOM", "TXN", "ADI", "MRVL"]
    software_leaders = ["CRWD", "PANW", "SNPS", "CDNS", "ADBE", "CRM", "INTU", "NOW", "UBER", "ABNB", "DASH"]
    
    if mode == "Tech Leaders (精選)":
        return list(set(tech_leaders + semi_leaders + software_leaders))
    else:
        # 可自行擴充
        return tech_leaders

# 計算 RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 判斷 K 線型態 (簡單版)
def check_candle_pattern(open_p, high, low, close):
    body = abs(close - open_p)
    range_len = high - low
    lower_shadow = min(open_p, close) - low
    
    # 槌子線 (Hammer): 下影線長，實體小
    if range_len > 0 and lower_shadow > (body * 2) and lower_shadow > (range_len * 0.5):
        return "🔨 Hammer (止跌訊號)"
    # 實體大紅棒
    if close > open_p and body > (range_len * 0.7):
        return "🔥 Strong Bullish (強勢)"
    return "Normal"

# 大盤紅綠燈 (Market Context)
def get_market_status():
    try:
        spy = yf.download("SPY", period="6mo", progress=False)['Close']
        ma20 = spy.rolling(20).mean().iloc[-1]
        ma50 = spy.rolling(50).mean().iloc[-1]
        curr = spy.iloc[-1]
        
        status = "🟢 多頭順風 (Bull Market)"
        if curr < ma20 and curr > ma50:
            status = "🟡 震盪整理 (Caution)"
        elif curr < ma50:
            status = "🔴 空頭逆風 (Bear Market - 減少部位)"
            
        return status, round(curr, 2)
    except:
        return "⚪ 無法獲取大盤數據", 0

# 策略主邏輯
def analyze_stock(ticker, df, spy_df):
    try:
        if len(df) < 200: return None
        curr = df.iloc[-1]
        close = curr['Close']
        low = curr['Low']
        high = curr['High']
        open_p = curr['Open']
        
        # 基礎均線
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 1. 趨勢過濾 (Trend Filter)
        if close < ma200: return None # 200MA 以下不做多

        # 2. 相對強弱度 (Relative Strength) - 核心賺錢邏輯
        # 計算過去 20 天，個股漲幅 vs SPY 漲幅
        stock_ret = (close - df['Close'].iloc[-21]) / df['Close'].iloc[-21]
        # 注意：這裡 spy_df 需要對齊日期，簡單起見我們取最後一筆近似
        spy_curr = spy_df.iloc[-1]
        spy_prev = spy_df.iloc[-21] if len(spy_df) > 21 else spy_df.iloc[0]
        spy_ret = (spy_curr - spy_prev) / spy_prev
        
        rs_rating = "弱於大盤"
        if stock_ret > spy_ret: rs_rating = "🚀 強於大盤 (Leader)"
        
        # 3. Setup 偵測
        dist_20 = (low - ma20) / ma20
        setup_type = ""
        
        # 網球行為：回測 20MA 附近 (上下 2.5%) 且收盤價有撐
        if -0.025 <= dist_20 <= 0.025 and close > ma20:
            setup_type = "Tennis Ball (20MA)"
        # 強力支撐：回測 50MA (機構防線)
        elif abs((low - ma50) / ma50) <= 0.02 and close > ma50:
            setup_type = "Institution Defense (50MA)"
            
        if not setup_type: return None
        
        # 4. K線與量能
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = curr['Volume'] / avg_vol
        candle_signal = check_candle_pattern(open_p, high, low, close)
        
        # 如果爆量下跌，視為失敗
        if vol_ratio > 1.5 and close < open_p: return None 
        
        # 5. 交易計畫
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        entry = high + (atr * 0.1) # 突破高點一點點
        stop = low - (atr * 0.1)   # 跌破低點一點點
        risk = entry - stop
        if risk == 0: return None
        target = entry + (risk * 2.5) # 2.5R 獲利
        
        return {
            "Symbol": ticker,
            "Setup": setup_type,
            "RS": rs_rating,
            "Vol_Stat": f"{round(vol_ratio, 1)}x",
            "Candle": candle_signal,
            "Price": close,
            "Entry": round(entry, 2),
            "Stop": round(stop, 2),
            "Target": round(target, 2),
            "MA20": round(ma20, 2),
            "Risk_Per_Share": round(risk, 2)
        }
    except:
        return None

# ==========================================
# 3. 側邊欄：資金控管 (Money Management)
# ==========================================
with st.sidebar:
    st.header("💰 資金控管中心")
    account_size = st.number_input("總資金 (USD)", value=10000, step=1000)
    risk_per_trade_pct = st.slider("單筆風險 (%)", 0.5, 5.0, 1.0)
    
    risk_amount = account_size * (risk_per_trade_pct / 100)
    st.success(f"單筆最大虧損額度: **${risk_amount:.1f}**")
    st.info("💡 這是職業操盤手最重要的數字。無論多好的 setup，虧損絕不能超過此金額。")
    
    st.divider()
    scan_btn = st.button("🚀 掃描市場機會", use_container_width=True)

# ==========================================
# 4. 主畫面與結果
# ==========================================

# A. 大盤儀表板
spy_data = yf.download("SPY", period="3mo", progress=False)['Close']
mkt_status, spy_price = get_market_status()

c1, c2 = st.columns([2, 1])
with c1:
    st.subheader(f"目前市場環境： {mkt_status}")
with c2:
    st.metric("SPY Price", f"${spy_price}")

if scan_btn:
    tickers = get_tickers("Tech Leaders (精選)")
    data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
    
    valid_setups = []
    
    # 進度條
    bar = st.progress(0)
    for i, t in enumerate(tickers):
        bar.progress((i+1)/len(tickers))
        try:
            if len(tickers) == 1: df = data
            else: df = data[t].dropna()
            
            res = analyze_stock(t, df, spy_data)
            if res: valid_setups.append(res)
        except: continue
    bar.empty()
    
    if valid_setups:
        st.session_state['results'] = pd.DataFrame(valid_setups)
    else:
        st.warning("目前沒有符合高勝率標準的 Setup，建議空手觀望。")
        st.session_state['results'] = None

# B. 顯示分析結果
if st.session_state.get('results') is not None:
    df = st.session_state['results']
    
    # 按照 RS 強度排序 (強者恆強)
    df['Sort_Key'] = df['RS'].apply(lambda x: 1 if "Leader" in x else 0)
    df = df.sort_values(by=['Sort_Key', 'Vol_Stat'], ascending=False)
    
    st.write(f"### 🔍 發現 {len(df)} 個潛在機會 (依強度排序)")
    
    # 使用 Tabs 分類展示
    tab1, tab2 = st.tabs(["📊 戰術看板 (Dashboard)", "📝 詳細清單"])
    
    with tab1:
        # 重點展示第一名
        top_pick = df.iloc[0]
        
        st.markdown(f"## ⭐ 今日首選：{top_pick['Symbol']}")
        
        # 計算部位規模
        shares_to_buy = int(risk_amount / top_pick['Risk_Per_Share'])
        position_value = shares_to_buy * top_pick['Entry']
        
        # 核心數據區
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Entry (Buy Stop)</div><div class="metric-value">${top_pick["Entry"]}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Stop Loss</div><div class="metric-value" style="color:#ff4b4b">${top_pick["Stop"]}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><div class="metric-label">建議股數</div><div class="metric-value" style="color:#00d084">{shares_to_buy} 股</div><div style="font-size:10px; color:#666">倉位: ${int(position_value)}</div></div>', unsafe_allow_html=True)
        with col4:
            # 強度標籤
            rs_color = "green" if "Leader" in top_pick['RS'] else "orange"
            st.markdown(f'<div class="metric-box"><div class="metric-label">相對強度 (RS)</div><div class="metric-value" style="color:{rs_color}">{top_pick["RS"]}</div></div>', unsafe_allow_html=True)

        # 原因與檢核
        c_left, c_right = st.columns([1, 2])
        with c_left:
            st.markdown("#### ✅ 進場檢查表")
            st.write(f"- **型態**: {top_pick['Setup']}")
            st.write(f"- **K線**: {top_pick['Candle']}")
            st.write(f"- **量能**: {top_pick['Vol_Stat']} (需 < 1.0x 較佳)")
            st.write(f"- **風報比**: 1 : 2.5")
            
            if position_value > account_size:
                st.error("⚠️ 警告：建議倉位超過總資金，請縮小風險比例或放棄此交易！")
            
        with c_right:
            # TradingView
            tv_script = f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_{top_pick['Symbol']}"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
                "width": "100%", "height": 400, "symbol": "{top_pick['Symbol']}",
                "interval": "D", "timezone": "Exchange", "theme": "dark",
                "style": "1", "locale": "zh_TW", "toolbar_bg": "#f1f3f6",
                "enable_publishing": false, "hide_side_toolbar": false,
                "allow_symbol_change": true, "container_id": "tradingview_{top_pick['Symbol']}",
                "studies": ["MASimple@tv-basicstudies","RSI@tv-basicstudies"]
              }});
              </script>
            </div>
            """
            components.html(tv_script, height=410)

    with tab2:
        # 表格顯示所有機會
        st.dataframe(df[['Symbol', 'Setup', 'RS', 'Candle', 'Entry', 'Stop', 'Risk_Per_Share']], use_container_width=True)

else:
    st.info("👈 請設定左側資金參數，並點擊掃描按鈕。")
