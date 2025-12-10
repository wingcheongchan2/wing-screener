import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components

# ==========================================
# 1. 系統視覺核心 (Safe CSS Architecture)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 背景：專業金融藍 (Professional FinTech Blue)
BG_URL = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"

# 定義 CSS (使用純字符串，避免 SyntaxError)
main_css = """
<style>
    /* 引入專業等寬字體 */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');

    /* --- 全局背景 --- */
    .stApp {
        background-image: linear-gradient(rgba(10, 25, 47, 0.85), rgba(10, 25, 47, 0.95)), url("REPLACE_BG_URL");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #e6f1ff;
        font-family: 'Inter', sans-serif;
    }
    
    /* 側邊欄：玻璃擬態深藍 */
    section[data-testid="stSidebar"] {
        background: rgba(17, 34, 64, 0.95);
        border-right: 1px solid #233554;
        backdrop-filter: blur(10px);
    }
    
    /* --- 股票列表：高密度數據磁貼 --- */
    div[role="radiogroup"] > label > div:first-child { display: none !important; }
    
    div[role="radiogroup"] {
        gap: 0px;
    }
    
    div[role="radiogroup"] > label {
        background: transparent;
        border-bottom: 1px solid #233554;
        padding: 12px 15px;
        margin: 0;
        border-radius: 0;
        transition: all 0.2s ease;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #8892b0;
        cursor: pointer;
    }
    
    div[role="radiogroup"] > label:hover {
        background: rgba(100, 255, 218, 0.05);
        color: #64ffda;
        padding-left: 20px;
    }
    
    div[role="radiogroup"] > label[data-checked="true"] {
        background: rgba(17, 34, 64, 1) !important;
        border-left: 4px solid #64ffda;
        color: #e6f1ff !important;
        font-weight: 700;
        padding-left: 20px;
    }

    /* --- 數據儀表板 --- */
    .stat-card {
        flex: 1;
        background: #112240;
        border: 1px solid #233554;
        padding: 15px;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .stat-label { font-size: 11px; color: #64ffda; letter-spacing: 1px; text-transform: uppercase; font-family: 'JetBrains Mono'; }
    .stat-value { font-size: 24px; font-weight: 700; color: #fff; margin-top: 5px; }

    /* --- 報告面板 --- */
    .report-panel {
        background: #0a192f;
        border: 1px solid #233554;
        border-top: 3px solid #64ffda;
        padding: 25px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.8;
        color: #a8b2d1;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .report-highlight { color: #64ffda; font-weight: bold; }
    .report-section { border-bottom: 1px solid #233554; padding-bottom: 10px; margin-bottom: 10px; }
    
    /* 按鈕樣式 */
    div.stButton > button {
        background: transparent;
        border: 1px solid #64ffda;
        color: #64ffda;
        border-radius: 4px;
        font-family: 'JetBrains Mono';
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background: rgba(100, 255, 218, 0.1);
        box-shadow: 0 0 15px rgba(100, 255, 218, 0.2);
    }
    
    h1, h2, h3 { color: #e6f1ff; }
</style>
"""

# 安全注入 CSS (替換網址變數)
st.markdown(main_css.replace("REPLACE_BG_URL", BG_URL), unsafe_allow_html=True)

# ==========================================
# 2. 市場核心 (Top Tier Alpha Universe)
# ==========================================
@st.cache_data
def get_market_universe():
    return [
        "NVDA", "TSLA", "MSTR", "PLTR", "COIN", "SMCI", "APP", "HOOD", 
        "AMD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "NET",
        "CRWD", "PANW", "UBER", "ABNB", "DASH", "DKNG", "RIVN", "CVNA",
        "AFRM", "UPST", "MARA", "CLSK", "RIOT", "SOFI", "PATH", "U", "AI",
        "ARM", "MU", "QCOM", "INTC", "TSM", "CELH", "ELF", "LULU", "ONON"
    ]

# ==========================================
# 3. J Law 戰略分析引擎
# ==========================================
def analyze_stock_pro(ticker, df):
    try:
        if len(df) < 200: return None
        curr = df.iloc[-1]
        
        # 1. 精密數據轉換
        close = float(curr['Close'])
        high = float(curr['High'])
        low = float(curr['Low'])
        vol = float(curr['Volume'])
        
        # 2. 技術指標矩陣
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = vol / avg_vol
        
        # 3. 趨勢審查
        if close < ma200: return None
        
        pattern = ""
        score = 0
        analysis_lines = []
        
        # --- 型態識別 ---
        
        # A. Tennis Ball (網球行為 - 20MA)
        dist_20 = (low - ma20) / ma20
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern = "TENNIS BALL (20MA)"
            score = 90
            analysis_lines.append(f"[TREND] Primary trend is UP. Price is respecting the 20-day Moving Average (${ma20:.2f}).")
            analysis_lines.append(f"[ACTION] Price pulled back orderly to the 20MA, exhibiting 'Tennis Ball' bounce behavior.")

        # B. Power Trend (強力趨勢 - 10MA)
        elif abs((low - ma10)/ma10) <= 0.025 and close > ma10:
            pattern = "POWER TREND (10MA)"
            score = 95
            analysis_lines.append(f"[TREND] Super Momentum phase. Stock is surfing the 10-day Moving Average (${ma10:.2f}).")
            analysis_lines.append(f"[ACTION] Institutions are aggressively defending the price. No deep pullback observed.")

        # C. Base Support (機構防線 - 50MA)
        elif abs((low - ma50)/ma50) <= 0.03 and close > ma50:
            pattern = "BASE SUPPORT (50MA)"
            score = 80
            analysis_lines.append(f"[TREND] Intermediate correction to the Institutional Line (50MA at ${ma50:.2f}).")
            analysis_lines.append(f"[ACTION] Price is testing key institutional support. Look for reversal confirmation.")
        else:
            return None 
            
        # --- 量能分析 ---
        if vol_ratio < 0.75:
            analysis_lines.append(f"[VOLUME] VCP Detected. Volume contracted to {int(vol_ratio*100)}% of average. Supply is exhausted.")
            score += 5
        elif vol_ratio > 1.5:
            analysis_lines.append(f"[VOLUME] Accumulation Day. High volume breakout ({vol_ratio:.1f}x avg). Big money entering.")
            
        # --- 自動交易計劃 ---
        entry_price = high + (atr * 0.1)
        
        if "10MA" in pattern: stop_price = ma20 - (atr * 0.1)
        elif "20MA" in pattern: stop_price = low - (atr * 0.2)
        else: stop_price = ma50 - (atr * 0.1)
        
        if entry_price <= stop_price: return None
        
        risk_per_share = entry_price - stop_price
        target_price = entry_price + (risk_per_share * 3)
        
        risk_pct = (risk_per_share / entry_price) * 100
        rr_ratio = (target_price - entry_price) / risk_per_share
        
        analysis_lines.append(f"[RISK] Calculated Stop Loss at ${stop_price:.2f} (-{risk_pct:.2f}%).")
        
        return {
            "Symbol": ticker,
            "Pattern": pattern,
            "Score": score,
            "Close": close,
            "Entry": entry_price,
            "Stop": stop_price,
            "Target": target_price,
            "RiskPct": risk_pct,
            "RR": rr_ratio,
            "Report": "<br>".join(analysis_lines)
        }
    except Exception as e:
        return None

# ==========================================
# 4. 顯示組件
# ==========================================
def display_dashboard(row):
    # 頂部標題區
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid #233554; padding-bottom:15px; margin-bottom:20px;">
        <div>
            <span style="font-family:'JetBrains Mono'; color:#64ffda; font-size:14px;">ASSET TICKER</span><br>
            <span style="font-size:48px; font-weight:800; letter-spacing:-1px; color:#e6f1ff;">{row['Symbol']}</span>
            <span style="background:rgba(100, 255, 218, 0.1); color:#64ffda; border:1px solid #64ffda; padding:2px 8px; font-size:12px; margin-left:10px;">{row['Pattern']}</span>
        </div>
        <div style="text-align:right;">
            <span style="font-family:'JetBrains Mono'; color:#8892b0; font-size:12px;">CONFIDENCE SCORE</span><br>
            <span style="font-size:36px; font-weight:700; color:#64ffda;">{row['Score']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4格戰術數據
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><div class="stat-label">Market Price</div><div class="stat-value">${row["Close"]:.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card" style="border-bottom:3px solid #64ffda"><div class="stat-label">Entry Trigger</div><div class="stat-value" style="color:#64ffda">${row["Entry"]:.2f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card" style="border-bottom:3px solid #ff5f56"><div class="stat-label">Hard Stop</div><div class="stat-value" style="color:#ff5f56">${row["Stop"]:.2f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-label">Target (3R)</div><div class="stat-value">${row["Target"]:.2f}</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # 專業分析報告
    st.markdown(f"""
    <div class="report-panel">
        <div class="report-section">
            <span class="report-highlight">⚡ TACTICAL ANALYSIS LOG</span>
        </div>
        {row['Report']}
        <br><br>
        <div class="report-section" style="border-top:1px solid #233554; padding-top:15px; border-bottom:none;">
            <span class="report-highlight">🎯 EXECUTION PROTOCOL:</span><br>
            1. Set <b>Stop Limit Buy Order</b> at <b>${row['Entry']:.2f}</b>.<br>
            2. If filled, immediately place Stop Loss at <b>${row['Stop']:.2f}</b> (Risk: {row['RiskPct']:.2f}%).<br>
            3. Target Reward-to-Risk Ratio is <b>1:{row['RR']:.1f}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TradingView 專業圖表
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:600px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
        "locale": "en", "toolbar_bg": "#112240", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
        "container_id": "tv_{row['Symbol']}",
        "studies": ["MASimple@tv-basicstudies","MASimple@tv-basicstudies","MASimple@tv-basicstudies"],
        "studies_overrides": {{ "MASimple@tv-basicstudies.length": 10, "MASimple@tv-basicstudies.length": 20, "MASimple@tv-basicstudies.length": 50 }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=610)

# ==========================================
# 5. 主程式邏輯
# ==========================================
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "MSTR"]

with st.sidebar:
    st.markdown("### 🦅 ALPHA STATION <span style='font-size:10px; color:#64ffda; border:1px solid #64ffda; padding:1px 3px;'>PRO</span>", unsafe_allow_html=True)
    mode = st.radio("SYSTEM MODULE", ["⚡ 強勢股掃描器 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    
    st.markdown("---")
    
    if mode == "⚡ 強勢股掃描器 (Scanner)":
        st.caption("TARGET: HIGH LIQUIDITY MOMENTUM")
        if st.button("INITIATE SCAN", use_container_width=True):
            universe = get_market_universe()
            status = st.status("Establishing Data Link...", expanded=True)
            
            # 批量下載 (快)
            status.write(f"Downloading data for {len(universe)} tickers...")
            data = yf.download(universe, period="1y", group_by='ticker', threads=True, progress=False)
            
            results = []
            prog = status.progress(0)
            
            for i, ticker in enumerate(universe):
                prog.progress((i + 1) / len(universe))
                try:
                    if len(universe) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        df = data[ticker].dropna()
                    else: df = data
                    
                    res = analyze_stock_pro(ticker, df)
                    if res: results.append(res)
                except: continue
                
            status.update(label="Scan Complete", state="complete", expanded=False)
            
            if results:
                st.session_state['scan_data'] = pd.DataFrame(results).sort_values('Score', ascending=False)
            else:
                st.session_state['scan_data'] = pd.DataFrame()

# 頁面內容渲染
if mode == "⚡ 強勢股掃描器 (Scanner)":
    st.title("⚡ MARKET SCANNER")
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("System Ready. Click [ INITIATE SCAN ] on the sidebar.")
    elif df.empty:
        st.warning("No valid setups found in the Top 100 list under current market conditions.")
    else:
        # 佈局：左側窄列表，右側寬面板
        c_list, c_main = st.columns([1, 4])
        with c_list:
            st.markdown(f"<div style='margin-bottom:10px; color:#8892b0; font-size:12px;'>RESULTS ({len(df)})</div>", unsafe_allow_html=True)
            sel = st.radio("Results", df['Symbol'].tolist(), 
                         format_func=lambda x: f"{x}  [{df[df['Symbol']==x]['Score'].values[0]}]",
                         label_visibility="collapsed")
        with c_main:
            row = df[df['Symbol'] == sel].iloc[0]
            display_dashboard(row)

elif mode == "👀 觀察名單 (Watchlist)":
    st.title("👀 WATCHLIST")
    c1, c2 = st.columns([1, 4])
    with c1:
        new_t = st.text_input("SYMBOL", "").upper()
        if st.button("ADD") and new_t:
            if new_t not in st.session_state['watchlist']: st.session_state['watchlist'].append(new_t)
        sel = st.radio("List", st.session_state['watchlist'], label_visibility="collapsed")
    with c2:
        if sel:
            d = yf.download(sel, period="1y", progress=False)
            if not d.empty:
                r = analyze_stock_pro(sel, d)
                if r: display_dashboard(r)
                else:
                    st.header(f"{sel} / MONITORING")
                    st.info("No actionable setup detected. Showing price action only.")
                    st.metric("Price", f"${d['Close'].iloc[-1]:.2f}")
                    components.html(f"""<div class="tradingview-widget-container" style="height:500px;width:100%"><div id="tv_{sel}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{sel}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_{sel}" }});</script></div>""", height=510)

elif mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h1 style='text-align:center; color:#e6f1ff;'>TESLA WAR ROOM</h1>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.link_button("News Feed", "https://www.google.com/search?q=Tesla+stock&tbm=nws", use_container_width=True)
    c2.link_button("Elon Musk X", "https://twitter.com/elonmusk", use_container_width=True)
    c3.link_button("Full Chart", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)
    st.divider()
    
    cl, cr = st.columns([1, 2])
    with cl:
        try:
            t = yf.Ticker("TSLA")
            h = t.history(period="1d")
            curr = h['Close'].iloc[-1]
            op = h['Open'].iloc[0]
            clr = "#64ffda" if curr>=op else "#ff5f56"
            st.markdown(f"<div style='text-align:center; background:rgba(17, 34, 64, 0.8); padding:30px; border:1px solid {clr}; border-radius:4px;'><h1 style='color:{clr}; font-size:48px; margin:0; font-family:JetBrains Mono'>${curr:.2f}</h1></div>", unsafe_allow_html=True)
        except: pass
        components.html("""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{ "symbol": "NASDAQ:TSLA", "width": "100%", "height": "350", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }</script></div>""", height=360)
        
    with cr:
        st.markdown("### 💬 Social Sentiment")
        try:
            r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/TSLA.json", headers={'User-Agent':'Mozilla/5.0'}, timeout=2)
            for m in r.json().get('messages', [])[:5]:
                u = m['user']['username']
                b = m['body']
                st.markdown(f"<div style='background:rgba(17, 34, 64, 0.8); padding:12px; margin-bottom:8px; border-radius:4px; border-left:3px solid #2962FF; font-family:JetBrains Mono; font-size:13px;'><strong style='color:#64ffda'>@{u}</strong><br><span style='color:#a8b2d1'>{b}</span></div>", unsafe_allow_html=True)
        except: st.info("Loading stream...")
