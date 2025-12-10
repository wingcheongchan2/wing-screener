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

# 定義 TSLA 背景圖 URL (Cyberpunk 風格/全系列)
TSLA_BG_URL = "https://wallpaperaccess.com/full/11831828.jpg" 
# 備用圖源: "https://images.hdqwalls.com/wallpapers/tesla-cybertruck-neon-4k-yu.jpg"

# 高級 CSS 注入函數 (動態背景用)
def inject_css(bg_image=None):
    # 預設背景 (深空灰)
    app_bg = "radial-gradient(circle at center, #1b2735 0%, #090a0f 100%)"
    overlay = ""
    
    if bg_image:
        # 如果有圖片，設定圖片背景 + 黑色遮罩以防文字看不清
        app_bg = f"url('{bg_image}')"
        overlay = """
        .stApp::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.75); /* 75% 黑色遮罩 */
            z-index: -1;
        }
        """

    st.markdown(f"""
    <style>
        /* 全局背景設定 */
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
            background-color: rgba(5, 5, 5, 0.9);
            border-right: 1px solid #333;
        }}

        /* 按鈕特效 */
        div.stButton > button:first-child {{
            background: linear-gradient(45deg, #00C853, #69F0AE);
            color: #000;
            border: none;
            padding: 10px 20px;
            font-weight: 800;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 200, 83, 0.4);
            transition: 0.3s;
            width: 100%;
        }}
        div.stButton > button:first-child:hover {{
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 200, 83, 0.7);
        }}

        /* 輸入框 */
        .stTextInput > div > div > input {{
            background-color: rgba(17, 17, 17, 0.8);
            color: #fff;
            border: 1px solid #333;
            border-radius: 8px;
        }}

        /* 卡片共用樣式 */
        .stock-card {{
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        /* TSLA 新聞卡片特效 */
        .news-card {{
            background: rgba(20, 20, 20, 0.8);
            border-left: 4px solid #FF3D00; /* TSLA Red */
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 10px 10px 0;
            transition: 0.3s;
            backdrop-filter: blur(5px);
        }}
        .news-card:hover {{
            background: rgba(40, 40, 40, 0.9);
            transform: translateX(5px);
            box-shadow: -5px 5px 15px rgba(255, 61, 0, 0.2);
        }}
        .news-link {{ text-decoration: none; color: #fff; font-weight: bold; font-size: 18px; display: block; }}
        .news-link:hover {{ color: #FF3D00; }}
        .news-meta {{ font-size: 12px; color: #aaa; margin-top: 8px; }}

        /* 數據格子 */
        .stat-box {{ background: rgba(17, 17, 17, 0.8); border-radius: 8px; padding: 10px; text-align: center; border-top: 3px solid #333; }}
        .stat-box.green {{ border-top-color: #00E676; }}
        .stat-box.red {{ border-top-color: #FF1744; }}
        .stat-box.blue {{ border-top-color: #2979FF; }}
        .stat-label {{ font-size: 12px; color: #888; letter-spacing: 1px; }}
        .stat-value {{ font-size: 18px; font-weight: bold; color: #fff; margin-top: 5px; }}

        h1, h2, h3 {{ font-family: 'Helvetica Neue', sans-serif; font-weight: 700; text-shadow: 2px 2px 4px #000; }}
        .highlight {{ color: #00E676; text-shadow: 0 0 10px rgba(0, 230, 118, 0.5); }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 核心大腦邏輯
# ==========================================

@st.cache_data
def get_core_tickers():
    return [
        "NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "HOOD", 
        "AAPL", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AVGO", "MU", "QCOM", 
        "CRWD", "PANW", "SNPS", "UBER", "ABNB", "DASH", "DKNG", "RIVN", "CVNA"
    ]

def analyze_stock_logic(ticker, df):
    try:
        if len(df) < 200: return None
        curr = df.iloc[-1]
        close, open_p, high, low, vol = curr['Close'], curr['Open'], curr['High'], curr['Low'], curr['Volume']
        
        # 指標
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        vol_ratio = vol / avg_vol
        
        if close < ma200: return None 
        
        pattern, pattern_score, analysis_text = "", 0, []
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        dist_50 = (low - ma50) / ma50
        
        if abs(dist_20) <= 0.03 and close > ma20: 
            pattern = "🎾 Tennis Ball (20MA)"
            pattern_score = 90
            analysis_text.append(f"股價回測 20MA (${ma20:.2f})。")
        elif abs(dist_10) <= 0.02 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            pattern_score = 95
            analysis_text.append(f"沿 10MA 強勢整理 (${ma10:.2f})。")
        elif abs(dist_50) <= 0.03 and close > ma50:
            pattern = "🛡️ Defense (50MA)"
            pattern_score = 80
            analysis_text.append(f"回測 50MA 機構防線 (${ma50:.2f})。")
        else:
            return None 
            
        if vol_ratio < 1.0:
            analysis_text.append(f"量縮至 {int(vol_ratio*100)}%。")
            pattern_score += 5
        elif vol_ratio > 1.5 and close < open_p:
            return None 
            
        entry_price = high + (atr * 0.1)
        stop_price = low - (atr * 0.1)
        if entry_price <= stop_price: return None
        risk = entry_price - stop_price
        target = entry_price + (risk * 3.0)
        
        return {
            "Symbol": ticker, "Pattern": pattern, "Score": pattern_score,
            "Close": close, "Entry": round(entry_price, 2), "Stop": round(stop_price, 2),
            "Target": round(target, 2), "Analysis": " ".join(analysis_text)
        }
    except: return None

def display_analysis_detail(row):
    st.markdown(f"## {row['Symbol']} 戰術分析")
    st.markdown(f"""
    <div class="stock-card" style="border-left: 5px solid #00E676;">
        <h4 style="margin:0; color:#00E676;">🤖 AI 分析：</h4>
        <p style="font-size:16px; margin-top:5px;">{row['Analysis']}</p>
        <p style="font-size:14px; color:#aaa;">信心分數：<b>{row['Score']} / 100</b></p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="stat-box blue"><div class="stat-label">現價</div><div class="stat-value">${row["Close"]:.2f}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="stat-box green"><div class="stat-label">買入 (Entry)</div><div class="stat-value">${row["Entry"]}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="stat-box red"><div class="stat-label">止蝕 (Stop)</div><div class="stat-value">${row["Stop"]}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="stat-box green"><div class="stat-label">目標 (3R)</div><div class="stat-value">${row["Target"]}</div></div>', unsafe_allow_html=True)
    st.write("")
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:450px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1", "locale": "zh_TW",
        "hide_side_toolbar": false, "allow_symbol_change": true, "container_id": "tv_{row['Symbol']}",
        "studies": ["MASimple@tv-basicstudies","MASimple@tv-basicstudies","MASimple@tv-basicstudies"],
        "studies_overrides": {{ "MASimple@tv-basicstudies.length": 10, "MASimple@tv-basicstudies.length": 20, "MASimple@tv-basicstudies.length": 50 }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=460)

# ==========================================
# 3. 頁面導航
# ==========================================

if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "COIN"]
if 'scan_results' not in st.session_state: st.session_state['scan_results'] = None
if 'watchlist_results' not in st.session_state: st.session_state['watchlist_results'] = None

with st.sidebar:
    st.markdown("## 🦅 COMMAND CENTER")
    page = st.radio("系統模式選擇：", ["🚀 自動掃描 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"], index=0)
    st.markdown("---")
    
    # 側邊欄邏輯
    if page == "🚀 自動掃描 (Scanner)":
        if st.button("啟動全市場掃描"):
            with st.spinner("分析運算中..."):
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
        new_ticker = st.text_input("新增 (如: PLTR)", "").upper()
        if st.button("➕ 加入"):
            if new_ticker and new_ticker not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(new_ticker)
        st.write(", ".join(st.session_state['watchlist']))
        if st.button("🔍 分析名單"):
             with st.spinner("分析中..."):
                my_tickers = st.session_state['watchlist']
                if my_tickers:
                    data = yf.download(my_tickers, period="1y", group_by='ticker', threads=True, progress=False)
                    w_results = []
                    for t in my_tickers:
                        try:
                            if len(my_tickers) == 1: df = data
                            else: 
                                if t not in data.columns.levels[0]: continue
                                df = data[t].dropna()
                            res = analyze_stock_logic(t, df)
                            if res: w_results.append(res)
                            else: w_results.append({"Symbol": t, "Pattern": "⚠️ 暫無 Setup", "Score": 0, "Close": df['Close'].iloc[-1], "Entry": 0, "Stop": 0, "Target": 0, "Analysis": "等待機會。"})
                        except: continue
                    st.session_state['watchlist_results'] = pd.DataFrame(w_results)

# ==========================================
# 4. 主畫面內容渲染
# ==========================================

# 根據頁面切換背景
if page == "⚡ TSLA 戰情室 (Intel)":
    inject_css(TSLA_BG_URL)
else:
    inject_css(None) # 恢復預設背景

st.markdown("# 🦅 J Law <span class='highlight'>Alpha Station</span>", unsafe_allow_html=True)

if page == "🚀 自動掃描 (Scanner)":
    st.subheader("全自動市場掃描")
    df = st.session_state['scan_results']
    if df is None: st.info("請點擊左側「啟動全市場掃描」。")
    elif df.empty: st.warning("無符合標準標的。")
    else:
        col_list, col_detail = st.columns([1, 2.5])
        with col_list:
            selected = st.radio("結果", df['Symbol'].tolist(), format_func=lambda x: f"{x} ({df[df['Symbol']==x]['Score'].values[0]}分)")
        with col_detail:
            display_analysis_detail(df[df['Symbol'] == selected].iloc[0])

elif page == "👀 觀察名單 (Watchlist)":
    st.subheader("自選股監控")
    df = st.session_state['watchlist_results']
    if df is None: st.info("請點擊左側「分析名單」。")
    else:
        col_list, col_detail = st.columns([1, 2.5])
        with col_list:
            selected = st.radio("清單", df['Symbol'].tolist(), format_func=lambda x: f"{'🟢' if df[df['Symbol']==x]['Score'].values[0] > 0 else '⚪'} {x}")
        with col_detail:
            row = df[df['Symbol'] == selected].iloc[0]
            if row['Score'] > 0: display_analysis_detail(row)
            else:
                st.markdown(f"## {row['Symbol']} - 觀望中")
                st.info(row['Analysis'])
                tv_html = f"""<div class="tradingview-widget-container" style="height:400px;width:100%"><div id="tv_w_{row['Symbol']}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_w_{row['Symbol']}" }});</script></div>"""
                components.html(tv_html, height=410)

elif page == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h2 style='text-align: center; color: white; text-shadow: 0 0 20px #FF3D00;'>⚡ TSLA 全球情報網</h2>", unsafe_allow_html=True)
    
    # 頂部戰術按鈕 (直接跳轉外部，解決 API 延遲問題)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("🌐 Google News (最新)", "https://www.google.com/search?q=Tesla+Elon+Musk+stock&tbm=nws&tbs=qdr:d", use_container_width=True)
    with c2:
        st.link_button("🐦 X (Elon Musk Search)", "https://twitter.com/search?q=(from%3Aelonmusk)%20OR%20(Tesla)%20min_faves%3A1000&src=typed_query&f=live", use_container_width=True)
    with c3:
        if st.button("🔄 強制刷新數據", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.write("")
    
    # 新聞抓取
    try:
        tsla_ticker = yf.Ticker("TSLA")
        news_list = tsla_ticker.news
        
        # 顯示即時報價
        hist = tsla_ticker.history(period="1d")
        if not hist.empty:
            curr_price = hist['Close'].iloc[-1]
            diff = curr_price - hist['Open'].iloc[0]
            color = "#00E676" if diff >= 0 else "#FF1744"
            st.markdown(f"""
            <div style="text-align:center; background:rgba(0,0,0,0.6); padding:10px; border-radius:10px; border:1px solid {color}; margin-bottom:20px;">
                <span style="font-size:16px; color:#aaa;">TSLA LIVE PRICE</span><br>
                <span style="font-size:36px; font-weight:bold; color:{color};">${curr_price:.2f}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📰 最新市場快訊 (News Feed)")
        
        if not news_list:
            st.warning("目前 API 未回傳新聞，請使用上方按鈕查看 Google/X 最新消息。")
        else:
            for news in news_list[:8]: # 顯示前8則
                # 嘗試獲取縮圖
                img_html = ""
                if 'thumbnail' in news and 'resolutions' in news['thumbnail']:
                    try:
                        img_url = news['thumbnail']['resolutions'][0]['url']
                        img_html = f'<img src="{img_url}" style="width:100px; height:70px; object-fit:cover; border-radius:5px; margin-right:15px; float:left;">'
                    except: pass

                # 處理時間
                try:
                    pub_time = datetime.fromtimestamp(news.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                except: pub_time = "剛剛"
                
                title = news.get('title', 'No Title')
                link = news.get('link', '#')
                publisher = news.get('publisher', 'Unknown')
                
                st.markdown(f"""
                <div class="news-card">
                    {img_html}
                    <div style="overflow:hidden;">
                        <a href="{link}" target="_blank" class="news-link">{title}</a>
                        <div class="news-meta">
                            🕒 {pub_time} | 📰 {publisher}
                        </div>
                    </div>
                    <div style="clear:both;"></div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"連線失敗: {e}")

# Footer
st.markdown("---")
st.caption("J Law Alpha Station v2.2 | Powered by Python, Streamlit & Yahoo Finance")
