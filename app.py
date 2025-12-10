import streamlit as st
import yfinance as yf
import pandas as pd
import requests # 新增 requests 庫來抓取 StockTwits
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 系統配置 & 背景修復
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 使用 Unsplash 的 Cyberpunk 車輛圖片 (高穩定性)
# 備用圖源: https://images.unsplash.com/photo-1617788138017-80ad40651399?q=80&w=2070&auto=format&fit=crop
BG_IMAGE_URL = "https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=2071&auto=format&fit=crop"

def inject_custom_css(bg_url=None):
    # 預設深色背景
    base_bg = """
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
        color: #E0E0E0;
    }
    """
    
    # 如果有背景圖，使用覆蓋模式
    if bg_url:
        base_bg = f"""
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url("{bg_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #ffffff;
        }}
        """

    st.markdown(f"""
    <style>
        {base_bg}
        
        /* 側邊欄半透明黑化 */
        section[data-testid="stSidebar"] {{
            background-color: rgba(0, 0, 0, 0.9) !important;
            border-right: 1px solid #333;
        }}

        /* 標題與按鈕優化 */
        h1, h2, h3 {{ font-family: 'Arial', sans-serif; font-weight: 800; text-shadow: 0px 0px 10px rgba(0,0,0,0.8); }}
        
        div.stButton > button:first-child {{
            background: linear-gradient(90deg, #00C853, #64DD17);
            color: black;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            transition: 0.3s;
        }}
        div.stButton > button:first-child:hover {{
            box-shadow: 0 0 20px rgba(0, 200, 83, 0.8);
            transform: scale(1.05);
        }}
        
        /* StockTwits 卡片樣式 */
        .twit-card {{
            background: rgba(30, 30, 30, 0.8);
            border-left: 4px solid #304FFE;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
        }}
        .user-name {{ color: #aaa; font-size: 12px; font-weight: bold; }}
        .twit-body {{ color: #fff; font-size: 15px; margin-top: 5px; line-height: 1.4; }}
        .sentiment-bull {{ color: #00E676; font-size: 12px; border: 1px solid #00E676; padding: 2px 5px; border-radius: 4px; }}
        .sentiment-bear {{ color: #FF1744; font-size: 12px; border: 1px solid #FF1744; padding: 2px 5px; border-radius: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據獲取邏輯
# ==========================================
@st.cache_data
def get_tickers():
    return ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "AAPL", "MSFT", "AMZN", "META", "GOOGL"]

def get_stocktwits_data(symbol="TSLA"):
    """從 StockTwits 獲取真實社群討論 (取代不穩定的 Yahoo News)"""
    try:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        return data.get('messages', [])
    except:
        return []

def analyze_stock(ticker, df):
    # (保留原本的技術分析邏輯，為節省篇幅省略部分重複代碼，功能不變)
    try:
        if len(df) < 50: return None
        curr = df.iloc[-1]
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        
        pattern = ""
        score = 0
        close = curr['Close']
        
        if close > ma20 and abs(curr['Low'] - ma20)/ma20 < 0.03:
            pattern = "🎾 Tennis Ball (20MA)"
            score = 90
        elif close > ma10 and abs(curr['Low'] - ma10)/ma10 < 0.02:
            pattern = "🔥 Power Trend (10MA)"
            score = 95
        elif close > ma50 and abs(curr['Low'] - ma50)/ma50 < 0.03:
            pattern = "🛡️ Defense (50MA)"
            score = 80
        else:
            return None
            
        return {
            "Symbol": ticker, "Pattern": pattern, "Score": score,
            "Close": close, "Entry": curr['High']*1.002, 
            "Stop": curr['Low']*0.998, "Target": curr['High']*1.05
        }
    except: return None

# ==========================================
# 3. 介面與導航
# ==========================================
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "COIN"]
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None

with st.sidebar:
    st.markdown("## 🦅 COMMAND CENTER")
    mode = st.radio("模式", ["🚀 掃描 (Scanner)", "👀 觀察 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    st.markdown("---")
    
    if mode == "🚀 掃描 (Scanner)":
        if st.button("開始掃描"):
            with st.spinner("掃描市場..."):
                ts = get_tickers()
                data = yf.download(ts, period="6mo", group_by='ticker', threads=True)
                res = []
                for t in ts:
                    try:
                        df = data[t].dropna() if len(ts) > 1 else data
                        r = analyze_stock(t, df)
                        if r: res.append(r)
                    except: continue
                st.session_state['scan_data'] = pd.DataFrame(res)
                
    elif mode == "👀 觀察 (Watchlist)":
        new = st.text_input("新增代碼", "").upper()
        if st.button("➕") and new:
            if new not in st.session_state['watchlist']: st.session_state['watchlist'].append(new)
        st.write(st.session_state['watchlist'])

# ==========================================
# 4. 主視圖渲染
# ==========================================

# 根據模式切換背景
if mode == "⚡ TSLA 戰情室 (Intel)":
    inject_custom_css(BG_IMAGE_URL)
else:
    inject_custom_css(None)

st.title("🦅 J Law Alpha Station")

if mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h2 style='text-align:center; color:#fff;'>⚡ TESLA WAR ROOM</h2>", unsafe_allow_html=True)
    
    # 外部連結 (最穩)
    c1, c2, c3 = st.columns(3)
    c1.link_button("🌐 Google News", "https://www.google.com/search?q=Tesla+stock&tbm=nws")
    c2.link_button("🐦 X (Elon Musk)", "https://twitter.com/elonmusk")
    c3.link_button("📈 TradingView", "https://www.tradingview.com/chart/?symbol=TSLA")
    
    st.divider()

    # 即時股價與社群情緒
    col_price, col_feed = st.columns([1, 2])
    
    with col_price:
        st.markdown("### 📊 Live Data")
        try:
            # 獲取即時價格
            t = yf.Ticker("TSLA")
            hist = t.history(period='1d')
            if not hist.empty:
                curr = hist['Close'].iloc[-1]
                chg = curr - hist['Open'].iloc[0]
                color = "green" if chg >= 0 else "red"
                st.markdown(f"""
                <div style="background:rgba(0,0,0,0.5); padding:20px; border-radius:10px; text-align:center; border: 1px solid {color};">
                    <h1 style="color:{color}; margin:0;">${curr:.2f}</h1>
                    <p style="color:#aaa;">Real-time Price</p>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.error("報價連線中斷")

        # 這裡不放容易壞的新聞，放 TradingView 迷你圖
        components.html("""
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
          {
          "symbol": "NASDAQ:TSLA",
          "width": "100%",
          "height": "350",
          "locale": "en",
          "dateRange": "12M",
          "colorTheme": "dark",
          "isTransparent": true,
          "autosize": false,
          "largeChartUrl": ""
        }
          </script>
        </div>
        """, height=350)

    with col_feed:
        st.markdown("### 💬 StockTwits Community (Live)")
        
        # 抓取 StockTwits 數據 (取代 Yahoo News)
        messages = get_stocktwits_data("TSLA")
        
        if not messages:
            st.warning("無法連線至社群數據源，請使用上方 X 按鈕。")
        else:
            cnt = 0
            for msg in messages:
                if cnt >= 8: break # 顯示前8條
                
                body = msg.get('body', '')
                user = msg.get('user', {}).get('username', 'Unknown')
                created = msg.get('created_at', '')[:10]
                sentiment = msg.get('entities', {}).get('sentiment', None)
                
                # 情緒標籤
                sent_tag = ""
                if sentiment:
                    s_val = sentiment.get('basic', '')
                    if s_val == 'Bullish': sent_tag = '<span class="sentiment-bull">BULLISH 🚀</span>'
                    elif s_val == 'Bearish': sent_tag = '<span class="sentiment-bear">BEARISH 🔻</span>'

                st.markdown(f"""
                <div class="twit-card">
                    <div class="user-name">@{user} &nbsp; {created} &nbsp; {sent_tag}</div>
                    <div class="twit-body">{body}</div>
                </div>
                """, unsafe_allow_html=True)
                cnt += 1

elif mode == "🚀 掃描 (Scanner)":
    # 掃描結果顯示邏輯
    if st.session_state['scan_data'] is not None and not st.session_state['scan_data'].empty:
        df = st.session_state['scan_data']
        sel = st.selectbox("結果", df['Symbol'])
        row = df[df['Symbol']==sel].iloc[0]
        st.metric(label=row['Symbol'], value=f"${row['Close']:.2f}")
        st.info(f"訊號: {row['Pattern']} | 分數: {row['Score']}")
        
        # 簡單圖表
        st.line_chart(yf.Ticker(sel).history(period='3mo')['Close'])
    else:
        st.info("請點擊左側「開始掃描」")

elif mode == "👀 觀察 (Watchlist)":
    # 觀察名單顯示
    if st.session_state['watchlist']:
        sel = st.selectbox("我的清單", st.session_state['watchlist'])
        st.subheader(f"{sel} Chart")
        # TradingView 全功能圖表
        components.html(f"""
        <div class="tradingview-widget-container" style="height:500px;width:100%">
          <div id="tv_chart" style="height:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{ "autosize": true, "symbol": "{sel}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_chart" }});
          </script>
        </div>
        """, height=500)
