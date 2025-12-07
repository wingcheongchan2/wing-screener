import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 系統設置
# ==========================================
st.set_page_config(page_title="J Law 冠軍操盤室 (Auto-Scan)", layout="wide", page_icon="⚔️")

st.markdown("""
<style>
    .reportview-container { margin-top: -2em; }
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ J Law 冠軍操盤室：全自動戰術掃描系統")
st.markdown("""
**系統邏輯**：自動遍歷 **Nasdaq 100** 及 **S&P 500** 成分股，尋找符合 J Law **「網球行為」** 的設置。
**輸出內容**：自動計算 **買入觸發價**、**止損價** 及 **戰術理由**。
""")

# ==========================================
# 2. 股票池定義 (S&P 500 & Nasdaq 100)
# ==========================================
@st.cache_data
def get_stock_universe(market_type):
    # 這裡為了演示速度，列出了流動性最好的頭部股票
    # 實際運作時，你可以擴充這個列表到完整的 500 隻
    nasdaq_100 = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", 
        "AMD", "NFLX", "PEP", "LIN", "ADBE", "CSCO", "TMUS", "QCOM", "TXN", "INTU", 
        "AMGN", "INTC", "ISRG", "HON", "AMAT", "BKNG", "SBUX", "MDLZ", "ADP", "GILD", 
        "LRCX", "ADI", "VRTX", "REGN", "PANW", "MU", "SNPS", "KLAC", "CDNS", "CHTR", 
        "CSX", "MAR", "PYPL", "ASML", "MNST", "ORLY", "ODFL", "LULU", "MSTR", "COIN", 
        "PLTR", "ARM", "SMCI", "UBER", "CRWD", "ZS", "NET", "DDOG", "TTD", "APP"
    ]
    
    sp_500_select = [
        "JPM", "V", "JNJ", "WMT", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "KO", 
        "PEP", "BAC", "COST", "MCD", "DIS", "CSCO", "ABT", "DHR", "NEE", "VZ", 
        "WFC", "PM", "CMCSA", "NKE", "UPS", "RTX", "BMY", "PFE", "LOW", "UNP", 
        "CAT", "GS", "GE", "IBM", "HON", "AMGN", "DE", "CAT", "BA", "MMM"
    ]
    
    if market_type == "Nasdaq 100":
        return list(set(nasdaq_100)) # 去重
    elif market_type == "S&P 500 (精選)":
        return list(set(sp_500_select))
    else:
        return list(set(nasdaq_100 + sp_500_select))

# ==========================================
# 3. J Law 核心策略運算 (Logic Core)
# ==========================================
def analyze_market_structure(ticker, df):
    try:
        if len(df) < 200: return None
        
        # 取得最新數據 (Latest Candle)
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        close = curr['Close']
        low = curr['Low']
        high = curr['High']
        volume = curr['Volume']
        
        # 計算均線
        sma10 = df['Close'].rolling(10).mean().iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 計算 50日均量
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = volume / avg_vol
        
        # --- 策略條件 (Conditionals) ---
        
        # 1. 趨勢過濾 (Trend Filter)
        # J Law 只做上升趨勢：股價 > 200MA 且 50MA > 200MA
        if not (close > sma200 and sma50 > sma200):
            return None
            
        setup_found = False
        strategy_name = ""
        support_level = 0.0
        
        # 2. 尋找回調 (Pullback Setup)
        # 股價必須回落到 10MA 或 20MA 附近 (Price Action)
        dist_10 = abs(low - sma10) / sma10
        dist_20 = abs(low - sma20) / sma20
        
        # 容錯率設定為 1.5%
        tolerance = 0.015 
        
        if dist_10 <= tolerance and close >= sma10 * 0.99:
            setup_found = True
            strategy_name = "🔥 10MA 超級強勢回調"
            support_level = sma10
        elif dist_20 <= tolerance and close >= sma20 * 0.99:
            setup_found = True
            strategy_name = "🟡 20MA 標準網球行為"
            support_level = sma20
            
        # 3. 量能分析 (Volume Analysis)
        # 必須縮量 (Volume Dry Up)
        if setup_found:
            is_dry_up = vol_ratio < 0.9 # 今日量小於均量
            
            if is_dry_up:
                # --- 計算交易計劃 (Trading Plan) ---
                
                # 買入點：突破今日高點 (Confirmation)
                entry_price = round(high + 0.05, 2) 
                
                # 止損點：今日低點下方 (Risk Management)
                stop_loss = round(low - 0.05, 2)
                
                # 如果止損太近(少於2%)，建議用 ATR 或稍微拉大，這裡簡單用 20MA 或 10MA 保護
                if (entry_price - stop_loss) / entry_price < 0.02:
                    stop_loss = round(min(low, support_level) * 0.99, 2)
                
                risk = entry_price - stop_loss
                target_price = round(entry_price + (risk * 3), 2) # 3R 回報
                
                reasoning = f"""
                1. **趨勢確認**：股價位於 200MA 之上，長期趨勢向上。
                2. **支撐測試**：股價回調至 **{strategy_name}** 位置 (${support_level:.2f})。
                3. **量能訊號**：今日成交量僅為平均的 {int(vol_ratio*100)}%，顯示**賣壓枯竭 (Dry Up)**。
                4. **執行**：等待股價突破 **${entry_price}** 確認買盤進場。
                """
                
                return {
                    "Ticker": ticker,
                    "Strategy": strategy_name,
                    "Close": round(close, 2),
                    "Entry": entry_price,
                    "Stop": stop_loss,
                    "Target": target_price,
                    "Volume": f"{int(vol_ratio*100)}%",
                    "Reason": reasoning
                }
    except:
        return None
    return None

# ==========================================
# 4. 前端互動介面
# ==========================================

# 側邊欄
st.sidebar.header("🎯 掃描控制台")
market = st.sidebar.selectbox("選擇掃描市場", ["Nasdaq 100", "S&P 500 (精選)", "全部"])
run_btn = st.sidebar.button("開始掃描", type="primary")

# 初始化 Session State
if 'results' not in st.session_state:
    st.session_state['results'] = []

# 掃描邏輯
if run_btn:
    tickers = get_stock_universe(market)
    st.session_state['results'] = [] # 清空舊結果
    
    with st.status(f"正在掃描 {len(tickers)} 隻股票...", expanded=True) as status:
        # 批量下載數據加速
        data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
        
        progress_bar = st.progress(0)
        found_count = 0
        
        for i, ticker in enumerate(tickers):
            progress_bar.progress((i + 1) / len(tickers))
            try:
                # 處理 yfinance 數據結構
                if len(tickers) > 1:
                    df = data[ticker].dropna()
                else:
                    df = data.dropna()
                
                if not df.empty:
                    res = analyze_market_structure(ticker, df)
                    if res:
                        st.session_state['results'].append(res)
                        found_count += 1
            except Exception as e:
                continue
        
        status.update(label=f"掃描完成！發現 {found_count} 個潛在機會", state="complete", expanded=False)

# 顯示結果
if st.session_state['results']:
    results_df = pd.DataFrame(st.session_state['results'])
    
    # 佈局：左側列表，右側詳情
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 候選名單")
        # 簡單表格展示
        display_df = results_df[['Ticker', 'Strategy', 'Entry']]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # 選擇股票
        selected_ticker = st.selectbox("👇 點擊選擇股票查看戰術板：", results_df['Ticker'].tolist())
    
    with col2:
        if selected_ticker:
            # 獲取選中股票的詳細數據
            item = next((x for x in st.session_state['results'] if x['Ticker'] == selected_ticker), None)
            
            st.subheader(f"🦅 {item['Ticker']} 戰術執行板")
            st.caption(f"策略模式：{item['Strategy']}")
            
            # 關鍵數據 Metics
            m1, m2, m3 = st.columns(3)
            m1.metric("🔵 買入觸發 (Entry)", f"${item['Entry']}")
            m2.metric("🔴 止損防守 (Stop)", f"${item['Stop']}")
            m3.metric("🟢 獲利目標 (3R)", f"${item['Target']}")
            
            st.markdown("### 📝 J Law 戰術分析")
            st.info(item['Reason'])
            
            st.markdown("### 📈 TradingView 圖表確認")
            # 嵌入 TradingView Widget
            tv_widget = f"""
            <div class="tradingview-widget-container">
              <div id="tradingview_chart"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
                "width": "100%",
                "height": 500,
                "symbol": "{item['Ticker']}",
                "interval": "D",
                "timezone": "Exchange",
                "theme": "dark",
                "style": "1",
                "locale": "zh_TW",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_chart",
                "studies": [
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 10 }}, "title": "10 MA" }},
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 20 }}, "title": "20 MA" }},
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 50 }}, "title": "50 MA" }},
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 200 }}, "title": "200 MA" }}
                ]
              }}
              );
              </script>
            </div>
            """
            components.html(tv_widget, height=500)

else:
    if run_btn:
        st.warning("沒有發現符合條件的股票。市場可能處於調整期，建議空倉觀望。")
    else:
        st.info("👈 請在左側點擊「開始掃描」")
