import streamlit as st
import yfinance as yf
import pandas as pd
import requests 
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 系統配置 & Cyber-UI CSS
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 新背景：Tesla Model S Plaid Dark Mode (高清暗黑系)
TSLA_BG = "https://w0.peakpx.com/wallpaper/312/82/HD-wallpaper-tesla-model-s-plaid-2021-tesla-model-s-tesla-car-black-car.jpg"

def inject_css(mode):
    # 基礎樣式 (適用全域)
    common_css = """
    <style>
        /* 全局背景與字體 */
        .stApp {
            background: #0e0e0e;
            color: #E0E0E0;
            font-family: 'SF Pro Display', sans-serif;
        }
        
        /* 側邊欄優化 */
        section[data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #222;
        }

        /* --- 列表按鈕大整形 (把 Radio 變成按鈕) --- */
        /* 隱藏原本醜醜的圓圈 */
        div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        /* 按鈕本體樣式 */
        div[role="radiogroup"] > label {
            background: #161616;
            border: 1px solid #333;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
        }
        /* 滑鼠懸停 */
        div[role="radiogroup"] > label:hover {
            border-color: #00E676;
            background: #1f1f1f;
            transform: translateX(5px);
        }
        /* 選中狀態 (發光綠色) */
        div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(90deg, #00C853, #00692c) !important;
            color: white !important;
            border: none;
            box-shadow: 0 0 15px rgba(0, 200, 83, 0.3);
        }
        
        /* 數據卡片 */
        .metric-card {
            background: #111;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        /* StockTwits 卡片 */
        .twit-card {
            background: rgba(30,30,30,0.9);
            border-left: 3px solid #304FFE;
            padding: 12px; 
            margin-bottom: 12px; 
            border-radius: 6px;
            font-size: 14px;
        }
    </style>
    """
    
    # TSLA 專屬背景 CSS (疊加黑色遮罩確保文字清晰)
    tsla_css = f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{TSLA_BG}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp {{ background: transparent !important; }}
    </style>
    """
    
    if mode == "⚡ TSLA 戰情室 (Intel)":
        st.markdown(common_css + tsla_css, unsafe_allow_html=True)
    else:
        st.markdown(common_css, unsafe_allow_html=True)

# ==========================================
# 2. 核心分析邏輯
# ==========================================
@st.cache_data
def get_tickers():
    return ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "AAPL", "MSFT", "AMZN", "GOOGL"]

def analyze_stock_logic(ticker, df):
    try:
        # 資料長度檢查
        if df.empty or len(df) < 60: return None
        
        curr = df.iloc[-1]
        close = float(curr['Close']) # 強制轉 float 防止報錯
        high = float(curr['High'])
        low = float(curr['Low'])
        
        # 均線計算
        series = df['Close']
        ma10 = series.rolling(10).mean().iloc[-1]
        ma20 = series.rolling(20).mean().iloc[-1]
        ma50 = series.rolling(50).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        pattern = ""
        score = 0
        reasons = []
        
        # 1. 型態判斷
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        
        if abs(dist_20) <= 0.03 and close > ma20:
            pattern = "🎾 Tennis Ball (20MA)"
            score = 90
            reasons.append(f"回測 20MA (${ma20:.2f}) 獲得支撐。")
        elif abs(dist_10) <= 0.02 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            score = 95
            reasons.append(f"沿 10MA (${ma10:.2f}) 強勢整理。")
        elif abs((low - ma50)/ma50) <= 0.03 and close > ma50:
            pattern = "🛡️ Defense (50MA)"
            score = 80
            reasons.append(f"回測 50MA 機構防線 (${ma50:.2f})。")
        else:
            return None 
            
        # 2. 交易計劃
        entry = high + (atr * 0.1)
        stop = low - (atr * 0.1)
        if entry <= stop: return None
        
        risk = entry - stop
        target = entry + (risk * 3)
        
        return {
            "Symbol": ticker,
            "Pattern": pattern,
            "Score": score,
            "Close": close,
            "Entry": round(entry, 2),
            "Stop": round(stop, 2),
            "Target": round(target, 2),
            "Analysis": " ".join(reasons)
        }
    except Exception as e:
        # print(e) # Debug use
        return None

def get_stocktwits(symbol):
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=2)
        if r.status_code == 200:
            return r.json().get('messages', [])
    except: pass
    return []

# ==========================================
# 3. 顯示邏輯 (修復崩潰與美化)
# ==========================================

def display_full_analysis(row):
    """顯示完整的分析介面"""
    st.markdown(f"## {row['Symbol']} <span style='font-size:18px; color:#aaa'>| {row['Pattern']}</span>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background:rgba(0,230,118,0.1); border-left:4px solid #00E676; padding:15px; border-radius:5px; margin-bottom:20px;">
        <b>🤖 AI Analysis:</b> {row['Analysis']}
    </div>
    """, unsafe_allow_html=True)
    
    # 數據格
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("現價 Price", f"${row['Close']:.2f}")
    c2.metric("買入 Entry", f"${row['Entry']:.2f}", delta="Breakout")
    c3.metric("止損 Stop", f"${row['Stop']:.2f}", delta_color="inverse")
    c4.metric("目標 Target (3R)", f"${row['Target']:.2f}")
    
    st.write("---")
    
    # TradingView
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:500px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
        "locale": "zh_TW", "toolbar_bg": "#f1f3f6", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
        "container_id": "tv_{row['Symbol']}",
        "studies": [ "MASimple@tv-basicstudies", "MASimple@tv-basicstudies", "MASimple@tv-basicstudies" ],
        "studies_overrides": {{ "MASimple@tv-basicstudies.length": 10, "MASimple@tv-basicstudies.length": 20, "MASimple@tv-basicstudies.length": 50 }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=510)

# ==========================================
# 4. 主程式
# ==========================================

if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "PLTR"]

with st.sidebar:
    st.markdown("### 🦅 COMMAND CENTER")
    # 使用 Radio 但 CSS 已經把它變成按鈕列表了
    mode = st.radio("SYSTEM MODE", ["🚀 自動掃描 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    
    st.markdown("---")
    
    if mode == "🚀 自動掃描 (Scanner)":
        if st.button("🔥 EXECUTE SCAN", use_container_width=True):
            with st.spinner("SCANNING MARKET DATA..."):
                ts = get_tickers()
                try:
                    data = yf.download(ts, period="6mo", group_by='ticker', threads=True, progress=False)
                    res = []
                    for t in ts:
                        try:
                            # 處理多層索引或單層索引
                            if isinstance(data.columns, pd.MultiIndex):
                                df = data[t].dropna()
                            else:
                                if len(ts) == 1: df = data
                                else: continue 
                                
                            r = analyze_stock_logic(t, df)
                            if r: res.append(r)
                        except: continue
                    
                    if res:
                        st.session_state['scan_data'] = pd.DataFrame(res).sort_values('Score', ascending=False)
                    else:
                        st.session_state['scan_data'] = pd.DataFrame()
                except Exception as e:
                    st.error(f"Data Fetch Error: {e}")

# 注入 CSS
inject_css(mode)

st.title("🦅 J Law Alpha Station")

# --- 模式 1: 掃描器 ---
if mode == "🚀 自動掃描 (Scanner)":
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("👈 等待指令：請點擊左側 [ EXECUTE SCAN ]")
    elif df.empty:
        st.warning("⚠️ 目前市場平淡，未發現高動能訊號。")
    else:
        col_nav, col_main = st.columns([1, 3])
        with col_nav:
            st.markdown("##### 🎯 訊號清單")
            # CSS 會美化這個列表
            sel = st.radio("Select Ticker:", df['Symbol'].tolist(), 
                         format_func=lambda x: f"{x} ({df[df['Symbol']==x]['Score'].values[0]})",
                         label_visibility="collapsed")
        with col_main:
            row = df[df['Symbol'] == sel].iloc[0]
            display_full_analysis(row)

# --- 模式 2: 觀察名單 (修復報錯) ---
elif mode == "👀 觀察名單 (Watchlist)":
    col_nav, col_main = st.columns([1, 3])
    
    with col_nav:
        st.markdown("##### 📝 我的清單")
        new_t = st.text_input("輸入代碼 (e.g. AMD)", "").upper()
        if st.button("➕ Add") and new_t:
            if new_t not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(new_t)
        
        sel_watch = st.radio("Watchlist:", st.session_state['watchlist'], label_visibility="collapsed")
    
    with col_main:
        if sel_watch:
            # 即時抓取 (增加錯誤處理)
            try:
                df_watch = yf.download(sel_watch, period="1y", progress=False)
                
                if df_watch.empty:
                    st.error(f"無法獲取 {sel_watch} 的數據，請檢查代碼。")
                else:
                    # 1. 嘗試跑策略
                    res = analyze_stock_logic(sel_watch, df_watch)
                    
                    if res:
                        display_full_analysis(res)
                    else:
                        # 2. 如果沒策略，顯示基本盤 (這裡修復了 TypeError)
                        curr_price = float(df_watch['Close'].iloc[-1]) # 關鍵修復：轉 float
                        prev_price = float(df_watch['Close'].iloc[-2])
                        delta = curr_price - prev_price
                        
                        st.markdown(f"## {sel_watch} <span style='font-size:16px; color:#888'>| 監控模式</span>", unsafe_allow_html=True)
                        st.metric("現價 Price", f"${curr_price:.2f}", f"{delta:.2f}")
                        
                        # 只顯示圖表
                        tv_html = f"""
                        <div class="tradingview-widget-container" style="height:500px;width:100%">
                          <div id="tv_{sel_watch}" style="height:100%"></div>
                          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                          <script type="text/javascript">
                          new TradingView.widget({{ "autosize": true, "symbol": "{sel_watch}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_{sel_watch}" }});
                          </script>
                        </div>
                        """
                        components.html(tv_html, height=510)
            except Exception as e:
                st.error(f"系統錯誤: {str(e)}")

# --- 模式 3: TSLA 戰情室 (新背景) ---
elif mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h2 style='text-align:center; color:#fff; text-shadow:0 0 20px #000; letter-spacing:2px;'>⚡ TESLA INTELLIGENCE</h2>", unsafe_allow_html=True)
    
    # 外部按鈕
    c1, c2, c3 = st.columns(3)
    c1.link_button("🌐 Google News", "https://www.google.com/search?q=Tesla+stock&tbm=nws", use_container_width=True)
    c2.link_button("🐦 X (Elon Musk)", "https://twitter.com/elonmusk", use_container_width=True)
    c3.link_button("📈 TradingView", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)
    
    st.divider()
    
    col_l, col_r = st.columns([1, 2])
    
    with col_l:
        st.markdown("### 📡 Live Feed")
        try:
            t = yf.Ticker("TSLA")
            hist = t.history(period="1d")
            if not hist.empty:
                curr = float(hist['Close'].iloc[-1])
                open_p = float(hist['Open'].iloc[0])
                chg = curr - open_p
                color = "#00E676" if chg >= 0 else "#FF1744"
                
                st.markdown(f"""
                <div style="text-align:center; background:rgba(0,0,0,0.6); padding:20px; border-radius:10px; border:1px solid {color}; backdrop-filter:blur(5px);">
                    <div style="font-size:14px; color:#ccc;">REAL-TIME PRICE</div>
                    <div style="font-size:48px; font-weight:bold; color:{color}; text-shadow:0 0 10px {color};">${curr:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        except: st.error("Connection Lost")
        
        # 迷你圖
        components.html("""
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
          { "symbol": "NASDAQ:TSLA", "width": "100%", "height": "300", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }
          </script>
        </div>
        """, height=320)

    with col_r:
        st.markdown("### 💬 StockTwits Sentiment")
        msgs = get_stocktwits("TSLA")
        if msgs:
            for m in msgs[:7]:
                body = m.get('body')
                user = m.get('user', {}).get('username')
                time = m.get('created_at', '')[11:16]
                st.markdown(f"""
                <div class='twit-card'>
                    <div style='color:#00E676; font-size:12px; font-weight:bold; margin-bottom:4px;'>@{user} • {time}</div>
                    <div style='color:#eee;'>{body}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Connecting to social stream...")
