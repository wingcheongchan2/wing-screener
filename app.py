import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 旗艦級 UI 設定 (Cyber-FinTech 風格)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 高級 CSS 注入
st.markdown("""
<style>
    /* 全局背景：深空灰黑 */
    .stApp {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        color: #E0E0E0;
    }

    /* 側邊欄優化 */
    section[data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #333;
    }

    /* 按鈕：霓虹光效 */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #00C853, #69F0AE);
        color: #000;
        border: none;
        padding: 10px 20px;
        font-weight: 800;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 200, 83, 0.4);
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 200, 83, 0.7);
    }

    /* 輸入框優化 */
    .stTextInput > div > div > input {
        background-color: #111;
        color: #fff;
        border: 1px solid #333;
        border-radius: 8px;
    }

    /* 結果卡片：玻璃擬態 */
    .stock-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        transition: 0.3s;
    }
    
    /* 新聞卡片 */
    .news-card {
        background: #111;
        border-left: 4px solid #FF3D00; /* TSLA Red */
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
    }
    .news-link { text-decoration: none; color: #E0E0E0; font-weight: bold; font-size: 18px; }
    .news-link:hover { color: #FF3D00; }
    .news-meta { font-size: 12px; color: #666; margin-top: 5px; }

    /* 數據格子 */
    .stat-box { background: #111; border-radius: 8px; padding: 10px; text-align: center; border-top: 3px solid #333; }
    .stat-box.green { border-top-color: #00E676; }
    .stat-box.red { border-top-color: #FF1744; }
    .stat-box.blue { border-top-color: #2979FF; }
    .stat-label { font-size: 12px; color: #888; letter-spacing: 1px; }
    .stat-value { font-size: 18px; font-weight: bold; color: #fff; margin-top: 5px; }

    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    .highlight { color: #00E676; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心大腦邏輯 (共用函數)
# ==========================================

@st.cache_data
def get_core_tickers():
    return [
        "NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "HOOD", 
        "AAPL", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AVGO", "MU", "QCOM", 
        "CRWD", "PANW", "SNPS", "UBER", "ABNB", "DASH", "DKNG", "RIVN", "CVNA"
    ]

def analyze_stock_logic(ticker, df):
    """ J Law 完整技術分析邏輯 """
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
        
        # 核心過濾 (The Filter)
        if close < ma200: return None 
        
        # 型態識別
        pattern, pattern_score, analysis_text = "", 0, []
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        dist_50 = (low - ma50) / ma50
        
        if abs(dist_20) <= 0.03 and close > ma20: 
            pattern = "🎾 Tennis Ball (20MA)"
            pattern_score = 90
            analysis_text.append(f"股價回測 20MA (支撐價 ${ma20:.2f})，符合網球行為。")
        elif abs(dist_10) <= 0.02 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            pattern_score = 95
            analysis_text.append(f"股價沿著 10MA 強勢整理 (支撐價 ${ma10:.2f})，動能極強。")
        elif abs(dist_50) <= 0.03 and close > ma50:
            pattern = "🛡️ Institutional Line (50MA)"
            pattern_score = 80
            analysis_text.append(f"股價回測 50MA 機構成本區 (支撐價 ${ma50:.2f})。")
        else:
            return None 
            
        if vol_ratio < 1.0:
            analysis_text.append(f"量縮至均量 {int(vol_ratio*100)}% (VCP)。")
            pattern_score += 5
        elif vol_ratio > 1.5 and close < open_p:
            return None 
            
        # 交易計劃
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
    """ 顯示單一股票的詳細分析介面 (共用於掃描與觀察區) """
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
    
    # TradingView Widget
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
# 3. 頁面導航與狀態管理
# ==========================================

# 初始化 Session State
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = ["TSLA", "NVDA", "COIN"] # 預設觀察
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None
if 'watchlist_results' not in st.session_state:
    st.session_state['watchlist_results'] = None

with st.sidebar:
    st.markdown("## 🦅 COMMAND CENTER")
    
    # 導航選單
    page = st.radio(
        "系統模式選擇：",
        ["🚀 自動掃描 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"],
        index=0
    )
    
    st.markdown("---")
    
    if page == "🚀 自動掃描 (Scanner)":
        st.markdown("掃描核心動能股清單")
        if st.button("啟動全市場掃描"):
            with st.spinner("正在連線華爾街... 分析技術型態中..."):
                tickers = get_core_tickers()
                data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
                results = []
                for t in tickers:
                    try:
                        df = data[t].dropna() if len(tickers) > 1 else data
                        res = analyze_stock_logic(t, df)
                        if res: results.append(res)
                    except: continue
                
                if results:
                    st.session_state['scan_results'] = pd.DataFrame(results).sort_values('Score', ascending=False)
                else:
                    st.session_state['scan_results'] = pd.DataFrame() # Empty
                    
    elif page == "👀 觀察名單 (Watchlist)":
        st.markdown("管理自選股")
        new_ticker = st.text_input("新增股票 (如: AMD)", "").upper()
        if st.button("➕ 加入觀察"):
            if new_ticker and new_ticker not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(new_ticker)
                st.success(f"已加入 {new_ticker}")
        
        st.markdown("目前清單:")
        st.write(", ".join(st.session_state['watchlist']))
        
        if st.button("🔍 分析觀察名單"):
             with st.spinner("分析自選股..."):
                my_tickers = st.session_state['watchlist']
                if not my_tickers:
                    st.warning("清單是空的！")
                else:
                    data = yf.download(my_tickers, period="1y", group_by='ticker', threads=True, progress=False)
                    w_results = []
                    for t in my_tickers:
                        try:
                            # 處理單一或多個股票的數據結構差異
                            if len(my_tickers) == 1: df = data
                            else: 
                                if t not in data.columns.levels[0]: continue
                                df = data[t].dropna()
                                
                            res = analyze_stock_logic(t, df)
                            if res: 
                                w_results.append(res)
                            else:
                                # 即使沒有完美 Setup，也顯示一條基本資訊以便觀察
                                curr_close = df['Close'].iloc[-1]
                                w_results.append({
                                    "Symbol": t, "Pattern": "⚠️ 暫無 Setup", "Score": 0,
                                    "Close": curr_close, "Entry": 0, "Stop": 0, "Target": 0,
                                    "Analysis": "目前未出現 J Law 定義的標準買點 (Trend/Support/Vol)。"
                                })
                        except: continue
                    
                    st.session_state['watchlist_results'] = pd.DataFrame(w_results)

# ==========================================
# 4. 主畫面內容渲染
# ==========================================

st.markdown("# 🦅 J Law <span class='highlight'>Alpha Station</span>", unsafe_allow_html=True)

if page == "🚀 自動掃描 (Scanner)":
    st.subheader("全自動市場掃描")
    df = st.session_state['scan_results']
    
    if df is None:
        st.info("請點擊左側「啟動全市場掃描」開始尋找機會。")
    elif df.empty:
        st.warning("目前市場無符合 J Law 標準的完美標的。")
    else:
        col_list, col_detail = st.columns([1, 2.5])
        with col_list:
            selected = st.radio("掃描結果", df['Symbol'].tolist(), 
                              format_func=lambda x: f"{x} ({df[df['Symbol']==x]['Score'].values[0]}分)")
        with col_detail:
            row = df[df['Symbol'] == selected].iloc[0]
            display_analysis_detail(row)

elif page == "👀 觀察名單 (Watchlist)":
    st.subheader("自選股監控")
    df = st.session_state['watchlist_results']
    
    if df is None:
        st.info("請點擊左側「分析觀察名單」查看自選股狀態。")
    else:
        col_list, col_detail = st.columns([1, 2.5])
        with col_list:
            # 顏色標記：有分數的顯示綠色，沒分數的普通顯示
            selected = st.radio("我的觀察股", df['Symbol'].tolist(), 
                              format_func=lambda x: f"{'🟢' if df[df['Symbol']==x]['Score'].values[0] > 0 else '⚪'} {x}")
        with col_detail:
            row = df[df['Symbol'] == selected].iloc[0]
            if row['Score'] > 0:
                display_analysis_detail(row)
            else:
                st.markdown(f"## {row['Symbol']} - 觀望中")
                st.info(row['Analysis'])
                # 即使沒有 Setup 也顯示圖表方便看盤
                tv_html = f"""
                <div class="tradingview-widget-container" style="height:400px;width:100%">
                  <div id="tv_watch_{row['Symbol']}" style="height:100%;width:100%"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{ "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1", "container_id": "tv_watch_{row['Symbol']}" }});
                  </script>
                </div>
                """
                components.html(tv_html, height=410)

elif page == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("### ⚡ TSLA & Elon Musk 全球情報網")
    
    # 搜尋功能
    search_query = st.text_input("搜尋關鍵字 (預設: Tesla Elon Musk)", "Tesla Elon Musk")
    
    if search_query:
        try:
            # 使用 yfinance 的 Ticker 抓取新聞 (比 Search 更穩定)
            tsla_ticker = yf.Ticker("TSLA")
            news_list = tsla_ticker.news
            
            # 如果是特定關鍵字，可以嘗試過濾，但 yfinance 主要回傳該股票相關
            # 這裡我們直接展示 TSLA 相關新聞，因為 API 限制較多
            
            st.markdown(f"最新關於 **{search_query}** 的市場消息：")
            st.write("")
            
            # 使用 Grid 佈局顯示新聞
            for news in news_list:
                # 處理時間戳記
                try:
                    pub_time = datetime.fromtimestamp(news.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M')
                except:
                    pub_time = "Recently"
                
                title = news.get('title', 'No Title')
                publisher = news.get('publisher', 'Unknown')
                link = news.get('link', '#')
                
                # 顯示新聞卡片
                st.markdown(f"""
                <div class="news-card">
                    <a href="{link}" target="_blank" class="news-link">{title}</a>
                    <div class="news-meta">
                        🕒 {pub_time} | 📰 {publisher}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            # 額外：顯示 TSLA 即時報價
            tsla_curr = tsla_ticker.history(period='1d')
            if not tsla_curr.empty:
                last_price = tsla_curr['Close'].iloc[-1]
                st.sidebar.markdown("---")
                st.sidebar.markdown(f"**TSLA 即時報價**")
                st.sidebar.markdown(f"<h2 style='color:#FF3D00'>${last_price:.2f}</h2>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"連線新聞伺服器失敗: {e}")

# Footer
st.markdown("---")
st.caption("J Law Alpha Station v2.1 | Data provided by Yahoo Finance")
