import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ==========================================
# 1. 系統設置 (J Law 戰情室風格)
# ==========================================
st.set_page_config(page_title="J Law Auto Screener", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    /* 按鈕優化 */
    div.stButton > button:first-child {
        background-color: #2962FF; color: white; border: none; 
        font-weight: bold; padding: 12px; font-size: 16px; border-radius: 8px;
    }
    div.stButton > button:first-child:hover {
        background-color: #0039CB;
    }
    /* 數據卡片 */
    .metric-card {
        background-color: #1e1e1e; padding: 15px; border-radius: 8px;
        border-left: 5px solid #2962FF; text-align: center; margin-bottom: 10px;
    }
    .metric-val { font-size: 24px; font-weight: bold; color: #fff; }
    .metric-lbl { font-size: 12px; color: #aaa; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 J Law 自動股票搜尋器 (TradingView 版)")

# ==========================================
# 2. 自動搜尋核心 (AI 掃描)
# ==========================================
@st.cache_data
def get_tickers():
    # 這裡放 J Law 關注的強勢動能股 (60+ 檔)
    return [
        "NVDA", "TSLA", "AMD", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "NFLX",
        "COIN", "MSTR", "MARA", "RIOT", "HOOD", "PLTR", "SOFI", "UPST", "AFRM",
        "SMCI", "ARM", "AVGO", "MU", "QCOM", "TSM", "MRVL", "LRCX", "AMAT",
        "CRWD", "PANW", "SNPS", "NOW", "UBER", "DASH", "ABNB", "SQ", "PYPL",
        "JPM", "GS", "V", "MA", "CAT", "DE", "BA", "LULU", "CELH", "DKNG",
        "SHOP", "NET", "DDOG", "TTD", "APP", "CVNA", "RIVN", "ON"
    ]

def scan_market(ticker, df):
    """
    J Law 核心演算法：找出 Setup
    """
    try:
        if len(df) < 200: return None
        
        curr = df.iloc[-1]
        close = curr['Close']
        vol = curr['Volume']
        
        # 均線計算
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        
        # 1. 趨勢濾網：只做多頭 (200MA 之上)
        if close < ma200: return None

        # 2. 網球行為：回測 20MA 或 50MA
        dist_20 = (close - ma20) / ma20
        dist_50 = (close - ma50) / ma50
        
        setup_type = ""
        score = 0
        
        # 判定 Setup
        if abs(dist_20) <= 0.035: # 距離 20MA 3.5% 以內
            setup_type = "Tennis Ball (20MA)"
            score = 90
        elif abs(dist_50) <= 0.035: # 距離 50MA 3.5% 以內
            setup_type = "Defense Line (50MA)"
            score = 80
        else:
            return None # 沒踩到線，跳過

        # 3. 量能分析
        vol_ratio = vol / avg_vol
        if vol_ratio > 1.5: return None # 爆量下跌不接
        
        # 4. 交易計劃
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        entry = curr['High'] + (atr * 0.1) # 突破高點買進
        stop = curr['Low'] - (atr * 0.1)   # 跌破低點止損
        
        if entry <= stop: return None
        
        return {
            "Symbol": ticker,
            "Setup": setup_type,
            "Price": round(close, 2),
            "Entry": round(entry, 2),
            "Stop": round(stop, 2),
            "Vol_Ratio": round(vol_ratio, 2),
            "Score": score
        }
    except:
        return None

# ==========================================
# 3. 介面控制
# ==========================================
with st.sidebar:
    st.header("🔍 自動掃描設定")
    st.info("系統將掃描 60+ 檔熱門美股，找出符合 J Law 技術分析 (均線回測+縮量) 的股票。")
    run_btn = st.button("🚀 開始自動搜尋 (Auto Search)", type="primary")

# 初始化
if 'results' not in st.session_state:
    st.session_state['results'] = None

# 執行掃描邏輯
if run_btn:
    tickers = get_tickers()
    status = st.empty()
    status.write("⏳ 正在連線市場數據，AI 分析中...")
    bar = st.progress(0)
    
    data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
    
    valid_stocks = []
    
    for i, t in enumerate(tickers):
        bar.progress((i+1)/len(tickers))
        try:
            if len(tickers) == 1: df = data
            else:
                if t not in data.columns.levels[0]: continue
                df = data[t].dropna()
            
            res = scan_market(t, df)
            if res: valid_stocks.append(res)
        except: continue
        
    bar.empty()
    status.empty()
    
    if valid_stocks:
        # 按分數排序
        st.session_state['results'] = pd.DataFrame(valid_stocks).sort_values('Score', ascending=False)
        st.success(f"✅ 搜尋完成！找到 {len(valid_stocks)} 檔潛在獲利機會。")
    else:
        st.warning("⚠️ 目前市場沒有符合標準的機會 (空手也是一種策略)。")

# ==========================================
# 4. 顯示結果 (TradingView 整合)
# ==========================================
if st.session_state['results'] is not None:
    df = st.session_state['results']
    
    # 左側列表，右側圖表
    col_list, col_chart = st.columns([1, 2])
    
    with col_list:
        st.subheader("📋 機會清單")
        # 讓使用者點選股票
        selected_ticker = st.radio(
            "點擊查看圖表：",
            df['Symbol'].tolist(),
            format_func=lambda x: f"{x} - {df[df['Symbol']==x]['Setup'].values[0]}"
        )
        
        # 顯示選中股票的數據
        if selected_ticker:
            row = df[df['Symbol'] == selected_ticker].iloc[0]
            st.markdown("---")
            st.markdown(f"### 📊 {row['Symbol']} 交易計劃")
            st.markdown(f"**策略：** `{row['Setup']}`")
            
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">🔵 買入觸發價 (Entry)</div><div class="metric-val">${row["Entry"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">🔴 止損防守價 (Stop)</div><div class="metric-val" style="color:#ff4b4b">${row["Stop"]}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-card"><div class="metric-lbl">量能狀態</div><div class="metric-val">{row["Vol_Ratio"]}x</div></div>', unsafe_allow_html=True)

    with col_chart:
        if selected_ticker:
            st.subheader(f"📈 {selected_ticker} TradingView 分析")
            
            # 這是最完整的 TradingView Widget 代碼
            # 它會自動帶入上面搜尋到的 selected_ticker
            tv_html = f"""
            <div class="tradingview-widget-container" style="height:600px;width:100%">
              <div id="tradingview_widget" style="height:calc(100% - 32px);width:100%"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
                "autosize": true,
                "symbol": "{selected_ticker}",
                "interval": "D",
                "timezone": "Exchange",
                "theme": "dark",
                "style": "1",
                "locale": "zh_TW",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_widget",
                "studies": [
                  "MASimple@tv-basicstudies", 
                  "MASimple@tv-basicstudies"
                ],
                "studies_overrides": {{
                    "MASimple@tv-basicstudies.length": 20,
                    "MASimple@tv-basicstudies.length": 200
                }}
              }}
              );
              </script>
            </div>
            """
            components.html(tv_html, height=600)

else:
    st.info("👈 請點擊左側按鈕開始搜尋股票。")
