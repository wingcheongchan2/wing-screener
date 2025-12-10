import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 旗艦級 UI 設定
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 更換為極其穩定的 Tesla Cybertruck / Lineup 圖片 (Wikimedia Source)
# 這是一張 Cybertruck 的公開展示圖，非常有科技感
TSLA_BG_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Tesla_Cybertruck_Franz_von_Holzhausen_Mondlicht_2.jpg/1920px-Tesla_Cybertruck_Franz_von_Holzhausen_Mondlicht_2.jpg"

def inject_css(bg_image=None):
    # 預設背景 (深空灰)
    app_bg = "radial-gradient(circle at center, #1b2735 0%, #090a0f 100%)"
    overlay = ""
    
    if bg_image:
        # 加上黑色半透明遮罩 (0.85) 確保文字清晰讀取
        app_bg = f"url('{bg_image}')"
        overlay = """
        .stApp::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.85);
            z-index: -1;
        }
        """

    st.markdown(f"""
    <style>
        .stApp {{
            background: {app_bg};
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #E0E0E0;
        }}
        {overlay}
        
        /* 側邊欄 */
        section[data-testid="stSidebar"] {{
            background-color: rgba(5, 5, 5, 0.95);
            border-right: 1px solid #333;
        }}

        /* 按鈕優化 */
        div.stButton > button:first-child {{
            background: linear-gradient(45deg, #00C853, #69F0AE);
            color: #000;
            font-weight: 800;
            border-radius: 8px;
            border: none;
            transition: 0.3s;
        }}
        div.stButton > button:first-child:hover {{
            box-shadow: 0 0 15px rgba(0, 200, 83, 0.6);
            transform: scale(1.02);
        }}

        /* 標題優化 */
        h1, h2, h3 {{ font-family: 'Helvetica Neue', sans-serif; font-weight: 700; text-shadow: 2px 2px 4px #000; }}
        .highlight {{ color: #00E676; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯區
# ==========================================
@st.cache_data
def get_core_tickers():
    return ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "HOOD", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AVGO", "MU", "QCOM", "CRWD", "PANW", "SNPS", "UBER", "RIVN", "CVNA"]

def analyze_stock_logic(ticker, df):
    try:
        if len(df) < 200: return None
        curr = df.iloc[-1]
        close, open_p, high, low, vol = curr['Close'], curr['Open'], curr['High'], curr['Low'], curr['Volume']
        
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        if close < ma200: return None 
        
        pattern, pattern_score, analysis_text = "", 0, []
        
        # 簡易型態判定
        if abs((low - ma20) / ma20) <= 0.03 and close > ma20: 
            pattern = "🎾 Tennis Ball (20MA)"
            pattern_score = 90
            analysis_text.append(f"回測 20MA (${ma20:.2f})。")
        elif abs((low - ma10) / ma10) <= 0.02 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            pattern_score = 95
            analysis_text.append(f"沿 10MA 強勢整理 (${ma10:.2f})。")
        elif abs((low - ma50) / ma50) <= 0.03 and close > ma50:
            pattern = "🛡️ Defense (50MA)"
            pattern_score = 80
            analysis_text.append(f"回測 50MA 機構防線 (${ma50:.2f})。")
        else: return None
            
        vol_ratio = vol / avg_vol
        if vol_ratio < 1.0: 
            pattern_score += 5
            analysis_text.append(f"量縮 ({int(vol_ratio*100)}%)。")
            
        entry_price = high + (atr * 0.1)
        stop_price = low - (atr * 0.1)
        if entry_price <= stop_price: return None
        target = entry_price + ((entry_price - stop_price) * 3.0)
        
        return {
            "Symbol": ticker, "Pattern": pattern, "Score": pattern_score,
            "Close": close, "Entry": round(entry_price, 2), "Stop": round(stop_price, 2),
            "Target": round(target, 2), "Analysis": " ".join(analysis_text)
        }
    except: return None

# 顯示分析詳情 (共用)
def display_detail(row):
    st.markdown(f"### {row['Symbol']} - {row['Pattern']}")
    st.info(f"💡 分析：{row['Analysis']}")
    
    # 使用原生 Metric 顯示數據 (更穩定)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("現價", f"${row['Close']:.2f}")
    c2.metric("買入 (Entry)", f"${row['Entry']:.2f}")
    c3.metric("止損 (Stop)", f"${row['Stop']:.2f}")
    c4.metric("目標 (3R)", f"${row['Target']:.2f}")
    
    st.write("")
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:450px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1", 
        "container_id": "tv_{row['Symbol']}",
        "studies": ["MASimple@tv-basicstudies","MASimple@tv-basicstudies","MASimple@tv-basicstudies"],
        "studies_overrides": {{ "MASimple@tv-basicstudies.length": 10, "MASimple@tv-basicstudies.length": 20, "MASimple@tv-basicstudies.length": 50 }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=460)

# ==========================================
# 3. 頁面導航與狀態
# ==========================================
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "COIN"]
if 'scan_results' not in st.session_state: st.session_state['scan_results'] = None
if 'watchlist_results' not in st.session_state: st.session_state['watchlist_results'] = None

with st.sidebar:
    st.markdown("## 🦅 COMMAND CENTER")
    page = st.radio("模式選擇：", ["🚀 自動掃描 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    st.markdown("---")
    
    if page == "🚀 自動掃描 (Scanner)":
        if st.button("啟動掃描"):
            with st.spinner("掃描中..."):
                tickers = get_core_tickers()
                data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
                results = []
                for t in tickers:
                    try:
                        df = data[t].dropna() if len(tickers) > 1 else data
                        res = analyze_stock_logic(t, df)
                        if res: results.append(res)
                    except: continue
                st.session_state['scan_results'] = pd.DataFrame(results).sort_values('Score', ascending=False) if results else pd.DataFrame()

    elif page == "👀 觀察名單 (Watchlist)":
        new_t = st.text_input("新增代碼:", "").upper()
        if st.button("➕ 加入") and new_t:
            if new_t not in st.session_state['watchlist']: st.session_state['watchlist'].append(new_t)
        st.caption(", ".join(st.session_state['watchlist']))
        if st.button("🔍 更新數據"):
            with st.spinner("更新中..."):
                ts = st.session_state['watchlist']
                if ts:
                    data = yf.download(ts, period="1y", group_by='ticker', threads=True, progress=False)
                    res = []
                    for t in ts:
                        try:
                            df = data[t].dropna() if len(ts) > 1 else data
                            r = analyze_stock_logic(t, df)
                            if not r: r = {"Symbol": t, "Pattern": "⚠️ 觀望", "Score": 0, "Close": df['Close'].iloc[-1], "Entry":0,"Stop":0,"Target":0, "Analysis": "暫無 Setup"}
                            res.append(r)
                        except: continue
                    st.session_state['watchlist_results'] = pd.DataFrame(res)

# ==========================================
# 4. 主畫面內容
# ==========================================

# 切換背景
if page == "⚡ TSLA 戰情室 (Intel)":
    inject_css(TSLA_BG_URL)
else:
    inject_css(None)

st.title("🦅 J Law Alpha Station")

if page == "🚀 自動掃描 (Scanner)":
    df = st.session_state['scan_results']
    if df is None: st.info("👈 請點擊左側啟動掃描")
    elif df.empty: st.warning("未發現符合條件標的")
    else:
        sel = st.selectbox("選擇標的:", df['Symbol'].tolist(), format_func=lambda x: f"{x} - {df[df['Symbol']==x]['Score'].values[0]}分")
        display_detail(df[df['Symbol'] == sel].iloc[0])

elif page == "👀 觀察名單 (Watchlist)":
    df = st.session_state['watchlist_results']
    if df is None: st.info("👈 請更新觀察名單數據")
    else:
        sel = st.selectbox("我的清單:", df['Symbol'].tolist())
        display_detail(df[df['Symbol'] == sel].iloc[0])

elif page == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h2 style='text-align:center; text-shadow: 0 0 10px #FF0000;'>⚡ TESLA INTELLIGENCE HUB</h2>", unsafe_allow_html=True)
    
    # 外部連結按鈕 (最可靠)
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    col_btn1.link_button("🌐 Google News (Latest)", "https://www.google.com/search?q=Tesla+stock+news&tbm=nws&tbs=qdr:d", use_container_width=True)
    col_btn2.link_button("🐦 X (Elon Musk)", "https://twitter.com/elonmusk", use_container_width=True)
    col_btn3.link_button("📈 TradingView Chart", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)

    st.write("---")

    # 即時報價
    try:
        tsla = yf.Ticker("TSLA")
        hist = tsla.history(period="1d")
        if not hist.empty:
            curr = hist['Close'].iloc[-1]
            chg = curr - hist['Open'].iloc[0]
            color = "normal" if chg >= 0 else "inverse"
            st.metric("TSLA Live Price", f"${curr:.2f}", f"{chg:.2f}", delta_color=color)
    except: pass

    st.subheader("📰 最新消息流")
    
    try:
        # 重新獲取新聞
        news_data = tsla.news
        
        if not news_data:
            st.warning("⚠️ 目前數據源暫時無法讀取詳細新聞，請點擊上方按鈕查看 Google News。")
        else:
            # 改用原生 Streamlit 元件迴圈顯示，徹底解決 HTML 顯示原始碼的問題
            for item in news_data[:10]:
                with st.container(border=True):
                    # 嘗試獲取標題、連結、縮圖
                    title = item.get('title', 'No Title')
                    link = item.get('link', '#')
                    publisher = item.get('publisher', 'Unknown Source')
                    
                    # 處理時間戳
                    try:
                        pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                    except: 
                        pub_time = "Recent"

                    # 嘗試獲取圖片
                    img_url = None
                    if 'thumbnail' in item and 'resolutions' in item['thumbnail']:
                        try:
                            img_url = item['thumbnail']['resolutions'][0]['url']
                        except: pass
                    
                    # 佈局：左圖右文
                    nc1, nc2 = st.columns([1, 4])
                    with nc1:
                        if img_url:
                            st.image(img_url, use_container_width=True)
                        else:
                            # 如果沒圖，顯示一個 Tesla Icon 佔位
                            st.markdown("⚡", unsafe_allow_html=True)
                    
                    with nc2:
                        st.markdown(f"**[{title}]({link})**")
                        st.caption(f"{pub_time} | {publisher}")
                        
    except Exception as e:
        st.error(f"新聞載入錯誤: {str(e)}")
        st.info("請直接使用上方的 Google News 按鈕。")

# Footer
st.markdown("---")
st.caption("Alpha Station v2.3 Fix | System Operational")
