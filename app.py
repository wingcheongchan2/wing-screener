import streamlit as st
import yfinance as yf
import pandas as pd
import requests 
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 系統配置 & Cyber-UI (視覺回歸)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# TSLA 專屬背景
TSLA_BG = "https://images.unsplash.com/photo-1560958089-b8a1929cea89?q=80&w=2071&auto=format&fit=crop"

def inject_css(mode):
    # 1. 全局背景：恢復深空漸層 (Cyber Style)
    main_bg = """
    <style>
        .stApp {
            background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
            color: #E0E0E0;
            font-family: 'SF Pro Display', sans-serif;
        }
        
        /* 側邊欄磨砂質感 */
        section[data-testid="stSidebar"] {
            background: rgba(5, 5, 5, 0.85);
            backdrop-filter: blur(10px);
            border-right: 1px solid #333;
        }

        /* 2. 列表優化：緊湊清晰 (Compact List) */
        /* 隱藏預設圓圈 */
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        
        /* 選項樣式 */
        div[role="radiogroup"] > label {
            background: transparent;
            border: none;
            border-left: 3px solid #333;
            padding: 8px 15px; /* 變小變緊湊 */
            margin-bottom: 2px;
            border-radius: 0px 5px 5px 0px;
            transition: all 0.2s ease;
        }
        
        /* 滑鼠經過 */
        div[role="radiogroup"] > label:hover {
            background: rgba(255,255,255,0.05);
            border-left-color: #888;
            padding-left: 20px;
        }
        
        /* 選中狀態 */
        div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(90deg, rgba(0, 230, 118, 0.15), transparent) !important;
            border-left: 3px solid #00E676;
            color: #00E676 !important;
            font-weight: bold;
        }

        /* 3. 分析卡片樣式 */
        .analysis-box {
            background: rgba(16, 20, 24, 0.8);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .strategy-tag {
            background: #00E676; color: black; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;
        }
        .risk-tag {
            border: 1px solid #FF1744; color: #FF1744; padding: 2px 6px; border-radius: 4px; font-size: 12px;
        }
    </style>
    """
    
    # TSLA 背景覆蓋
    tsla_bg = f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url("{TSLA_BG}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp {{ background: transparent !important; }}
    </style>
    """
    
    if mode == "⚡ TSLA 戰情室 (Intel)":
        st.markdown(main_bg + tsla_bg, unsafe_allow_html=True)
    else:
        st.markdown(main_bg, unsafe_allow_html=True)

# ==========================================
# 2. J Law 深度分析邏輯 (邏輯增強)
# ==========================================
@st.cache_data
def get_tickers():
    return ["NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "APP", "HOOD", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AVGO", "NET"]

def analyze_jlaw_strategy(ticker, df):
    """
    J Law 核心算法 v6.0: 詳細分析趨勢、支撐、量能與風險
    """
    try:
        if len(df) < 200: return None
        
        # 轉換數據
        curr = df.iloc[-1]
        close = float(curr['Close'])
        high = float(curr['High'])
        low = float(curr['Low'])
        vol = float(curr['Volume'])
        
        # 移動平均線
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # ATR (波動率) 用於止損計算
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = vol / avg_vol
        
        # --- 1. 趨勢過濾 (The Filter) ---
        # 必須由左下往右上，且價格在長期均線之上
        if not (close > ma50 and ma50 > ma200):
            return None 

        pattern_name = ""
        score = 0
        analysis_report = []
        
        # --- 2. 戰術型態識別 ---
        
        # A. Tennis Ball Action (回測 20MA)
        dist_20 = (low - ma20) / ma20
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern_name = "🎾 Tennis Ball (20MA)"
            score = 90
            analysis_report.append(f"✅ **趨勢結構**：股價位於 50MA 與 200MA 之上，長期趨勢向上。")
            analysis_report.append(f"✅ **型態確認**：股價有序回測 20日均線 (${ma20:.2f})，展現出「網球般」的自然反彈行為，非垂直崩跌。")

        # B. Power Trend (強勢 10MA)
        elif abs((low - ma10)/ma10) <= 0.025 and close > ma10:
            pattern_name = "🔥 Power Trend (10MA)"
            score = 95
            analysis_report.append(f"✅ **趨勢結構**：超級動能狀態。股價緊貼 10日均線 (${ma10:.2f}) 上行。")
            analysis_report.append(f"✅ **型態確認**：這是最強勢的持有訊號，賣壓極輕，機構持續吸籌。")

        # C. Institution Defense (50MA)
        elif abs((low - ma50)/ma50) <= 0.03 and close > ma50:
            pattern_name = "🛡️ Institutional Line (50MA)"
            score = 80
            analysis_report.append(f"✅ **趨勢結構**：中期修正回測。")
            analysis_report.append(f"✅ **型態確認**：觸及 50日均線 (${ma50:.2f}) 機構成本區，這是多頭最後防線。")
        else:
            return None # 無法識別型態

        # --- 3. 量能分析 (Volume) ---
        if vol_ratio < 0.8:
            analysis_report.append(f"✅ **量能配合**：今日成交量急縮 (僅均量 {int(vol_ratio*100)}%)，顯示浮動籌碼清洗完畢 (Supply Dry Up)。")
            score += 5
        elif vol_ratio > 1.2 and close > df.iloc[-2]['Close']:
            analysis_report.append(f"✅ **量能配合**：帶量上漲，有買盤進駐。")
        
        # --- 4. 交易計劃 (Trade Plan) ---
        # Entry: 突破前一日高點或當日高點 + 0.1 ATR (濾網)
        trigger_price = high + (atr * 0.1)
        
        # Stop: 近期低點或均線下方 - 0.1 ATR
        # 如果是 10MA 戰法，止損守 20MA；如果是 20MA 戰法，守低點
        stop_price = low - (atr * 0.2)
        
        if trigger_price <= stop_price: return None
        
        risk_per_share = trigger_price - stop_price
        risk_pct = (risk_per_share / trigger_price) * 100
        
        # 目標價設定 (至少 3R)
        target_price = trigger_price + (risk_per_share * 3)
        
        # 添加風險報告
        analysis_report.append(f"⚠️ **風險評估**：單筆風險約 **{risk_pct:.2f}%**。")
        
        return {
            "Symbol": ticker,
            "Pattern": pattern_name,
            "Score": score,
            "Close": close,
            "Entry": round(trigger_price, 2),
            "Stop": round(stop_price, 2),
            "Target": round(target_price, 2),
            "Risk_Pct": round(risk_pct, 2),
            "Report": "\n\n".join(analysis_report)
        }
    except Exception as e:
        return None

# ==========================================
# 3. 顯示組件 (HUD 風格)
# ==========================================
def display_jlaw_report(row):
    """
    顯示詳細的 J Law 分析報告
    """
    # 標題區
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:15px;">
        <h1 style="margin:0; padding-right:15px;">{row['Symbol']}</h1>
        <span class="strategy-tag">{row['Pattern']}</span>
        <span style="margin-left:10px; font-size:14px; color:#888;">Score: {row['Score']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 主要分析內容 (HTML Box)
    st.markdown(f"""
    <div class="analysis-box">
        <h4 style="color:#00E676; margin-top:0;">🦅 J Law 戰術分析報告</h4>
        <div style="color:#ddd; line-height:1.6; white-space: pre-line;">
        {row['Report']}
        </div>
        <hr style="border-color:#333; margin:15px 0;">
        <div style="font-size:14px; color:#aaa;">
            💡 <b>操作建議 (Action)</b>：請在 <b>${row['Entry']}</b> 設定 <span style="color:#fff">Stop Limit Buy Order</span> (觸價買單)。若明日開盤直接下跌不觸發，則取消訂單。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("") # Spacer
    
    # 核心數據 (Entry / Stop / Target)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("現價 Price", f"${row['Close']:.2f}")
    c2.metric("買入 Entry", f"${row['Entry']:.2f}", delta="Trigger")
    c3.metric("止損 Stop", f"${row['Stop']:.2f}", f"-{row['Risk_Pct']}%", delta_color="inverse")
    c4.metric("目標 Target (3R)", f"${row['Target']:.2f}", "Profit")
    
    st.write("---")
    
    # TradingView 圖表
    st.markdown("##### 📈 技術圖表驗證")
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:550px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{row['Symbol']}",
        "interval": "D",
        "timezone": "Exchange",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tv_{row['Symbol']}",
        "studies": [
          "MASimple@tv-basicstudies",
          "MASimple@tv-basicstudies",
          "MASimple@tv-basicstudies"
        ],
        "studies_overrides": {{
            "MASimple@tv-basicstudies.length": 10,
            "MASimple@tv-basicstudies.length": 20,
            "MASimple@tv-basicstudies.length": 50
        }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=560)

# ==========================================
# 4. 主程式邏輯
# ==========================================
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "PLTR"]

with st.sidebar:
    st.markdown("### 🦅 COMMAND CENTER")
    # 更換名稱
    mode = st.radio("SYSTEM MODE", ["⚡ 強勢股票掃描器", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    
    st.markdown("---")
    
    if mode == "⚡ 強勢股票掃描器":
        if st.button("🔥 EXECUTE SCAN", use_container_width=True):
            with st.spinner("Analyzing Market Structure..."):
                ts = get_tickers()
                try:
                    data = yf.download(ts, period="1y", group_by='ticker', threads=True, progress=False)
                    res = []
                    for t in ts:
                        try:
                            # 處理多層/單層索引
                            if isinstance(data.columns, pd.MultiIndex):
                                df = data[t].dropna()
                            else:
                                if len(ts) == 1: df = data
                                else: continue 
                            
                            r = analyze_jlaw_strategy(t, df)
                            if r: res.append(r)
                        except: continue
                    
                    if res:
                        st.session_state['scan_data'] = pd.DataFrame(res).sort_values('Score', ascending=False)
                    else:
                        st.session_state['scan_data'] = pd.DataFrame()
                except Exception as e:
                    st.error(f"Error: {e}")

# 注入 CSS
inject_css(mode)

st.title("🦅 J Law Alpha Station")

# --- Mode 1: 強勢股票掃描器 (優化版) ---
if mode == "⚡ 強勢股票掃描器":
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("👈 等待指令：請點擊左側 [ EXECUTE SCAN ] 開始分析強勢股。")
    elif df.empty:
        st.warning("⚠️ 市場目前處於震盪或修正期，未發現符合「強趨勢 + 低風險」的完美設置。建議空手觀望。")
    else:
        # 左 1 : 右 3.5 比例，讓列表更緊湊，右邊空間更大
        col_list, col_detail = st.columns([1, 3.5])
        
        with col_list:
            st.markdown("##### 🎯 訊號清單")
            # CSS 已經將其變為緊湊型按鈕
            sel = st.radio(
                "Select:", 
                df['Symbol'].tolist(), 
                format_func=lambda x: f"{x}  ({df[df['Symbol']==x]['Score'].values[0]})",
                label_visibility="collapsed"
            )
            st.caption("Score 90+: High Conviction")
            
        with col_detail:
            if sel:
                row = df[df['Symbol'] == sel].iloc[0]
                display_jlaw_report(row)

# --- Mode 2: 觀察名單 ---
elif mode == "👀 觀察名單 (Watchlist)":
    col_nav, col_main = st.columns([1, 3])
    with col_nav:
        st.markdown("##### 📝 清單管理")
        new_t = st.text_input("Symbol (e.g. COIN)", "").upper()
        if st.button("➕ Add") and new_t:
            if new_t not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(new_t)
        
        sel_watch = st.radio("List:", st.session_state['watchlist'], label_visibility="collapsed")
    
    with col_main:
        if sel_watch:
            try:
                df_watch = yf.download(sel_watch, period="1y", progress=False)
                if df_watch.empty:
                    st.error("Invalid Symbol")
                else:
                    # 嘗試跑策略分析
                    res = analyze_jlaw_strategy(sel_watch, df_watch)
                    
                    if res:
                        display_jlaw_report(res)
                    else:
                        # 顯示基本圖表 (無策略)
                        curr = float(df_watch['Close'].iloc[-1])
                        st.markdown(f"## {sel_watch} <span style='font-size:16px; color:#666'>| Monitoring</span>", unsafe_allow_html=True)
                        st.metric("Price", f"${curr:.2f}")
                        
                        tv_html = f"""<div class="tradingview-widget-container" style="height:500px;width:100%"><div id="tv_{sel_watch}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{sel_watch}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_{sel_watch}" }});</script></div>"""
                        components.html(tv_html, height=510)
            except: st.error("Error loading data")

# --- Mode 3: TSLA 戰情室 ---
elif mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h2 style='text-align:center; color:#fff; text-shadow:0 0 20px #000;'>⚡ TESLA INTELLIGENCE</h2>", unsafe_allow_html=True)
    
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
                op = float(hist['Open'].iloc[0])
                color = "#00E676" if curr >= op else "#FF1744"
                st.markdown(f"""<div style="text-align:center; background:rgba(0,0,0,0.6); padding:20px; border-radius:10px; border:1px solid {color};"><div style="font-size:48px; font-weight:bold; color:{color};">${curr:.2f}</div></div>""", unsafe_allow_html=True)
        except: pass
        
        components.html("""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{ "symbol": "NASDAQ:TSLA", "width": "100%", "height": "300", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }</script></div>""", height=320)

    with col_r:
        st.markdown("### 💬 StockTwits")
        # 簡單抓取
        try:
            url = f"https://api.stocktwits.com/api/2/streams/symbol/TSLA.json"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers, timeout=2)
            msgs = r.json().get('messages', [])
            for m in msgs[:6]:
                user = m.get('user', {}).get('username')
                body = m.get('body')
                st.markdown(f"<div style='background:rgba(30,30,30,0.8); padding:10px; margin-bottom:8px; border-left:3px solid #304FFE; border-radius:4px;'><b style='color:#ccc'>@{user}</b><br><span style='color:#eee'>{body}</span></div>", unsafe_allow_html=True)
        except: st.info("Loading Social Data...")
