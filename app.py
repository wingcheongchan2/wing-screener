import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components

# ==========================================
# 1. 系統視覺設計 (FinTech Cyberpunk)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 背景：全球金融數據流
BG_URL = "https://images.unsplash.com/photo-1611974765270-ca12586343bb?q=80&w=2070&auto=format&fit=crop"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;800&display=swap');

    /* 全局背景 */
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url("{BG_URL}");
        background-size: cover;
        background-attachment: fixed;
        color: #E0E0E0;
        font-family: 'Inter', sans-serif;
    }}
    
    /* 側邊欄優化 */
    section[data-testid="stSidebar"] {{
        background: rgba(10, 10, 15, 0.9);
        border-right: 1px solid #333;
    }}

    /* 強勢股列表卡片 (Neon Glass) */
    div[role="radiogroup"] > label {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        padding: 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        transition: 0.2s;
        font-family: 'Roboto Mono';
        cursor: pointer;
    }}
    div[role="radiogroup"] > label:hover {{
        border-color: #00E676;
        background: rgba(0, 230, 118, 0.1);
        transform: translateX(5px);
    }}
    div[role="radiogroup"] > label[data-checked="true"] {{
        background: linear-gradient(90deg, #00C853, transparent) !important;
        color: white !important;
        border: 1px solid #00E676;
        font-weight: bold;
    }}
    div[role="radiogroup"] > label > div:first-child {{ display: none !important; }}

    /* 分析報告面板 */
    .analysis-panel {{
        background: #111;
        border-left: 5px solid #00E676;
        padding: 20px;
        border-radius: 5px;
        font-family: 'Roboto Mono', monospace;
        line-height: 1.6;
        margin-bottom: 20px;
    }}

    /* 數據儀表板 */
    .stat-box {{
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid #333;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
    }}
    .stat-label {{ font-size: 11px; color: #888; text-transform: uppercase; }}
    .stat-val {{ font-size: 22px; font-weight: bold; color: #fff; margin-top: 5px; }}
    
    /* 標題特效 */
    h1 {{ text-shadow: 0 0 20px rgba(0,230,118,0.5); letter-spacing: -1px; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 市場核心清單 (Top 100 Most Liquid / Active)
# ==========================================
@st.cache_data
def get_market_tickers():
    """
    不依賴外部網站爬蟲，直接內建華爾街交易量最大的 100+ 隻熱門強勢股。
    這確保了數據源 100% 穩定，且只分析有流動性的標的。
    """
    return [
        # --- Mag 7 & Mega Cap ---
        "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "AMD",
        
        # --- AI & Semi (半導體) ---
        "SMCI", "ARM", "MU", "QCOM", "TSM", "INTC", "AMAT", "LRCX", "KLAC", "MRVL", "VRT",
        "ALAB", "ASTS",
        
        # --- Crypto & Fintech ---
        "MSTR", "COIN", "MARA", "CLSK", "RIOT", "HOOD", "SQ", "PYPL", "AFRM", "UPST", "SOFI",
        
        # --- SaaS & Cloud (高成長) ---
        "PLTR", "CRWD", "PANW", "SNOW", "DDOG", "NET", "ZS", "MDB", "CRM", "ADBE", "NOW",
        "ORCL", "IBM", "APP", "PATH", "U", "AI",
        
        # --- Consumer & EV ---
        "NFLX", "DIS", "ABNB", "UBER", "DASH", "DKNG", "RIVN", "CVNA", "LCID", "F", "GM",
        "CELH", "ELF", "ONON", "SBUX", "NKE", "LULU",
        
        # --- Other Momentum ---
        "LLY", "NVO", "VRTX", "ISRG", "CAT", "DE", "GE", "XOM", "CVX", "JPM", "GS", "BAC"
    ]

# ==========================================
# 3. J Law 核心運算引擎 (深度量化)
# ==========================================
def analyze_stock_pro(ticker, df):
    try:
        # 數據檢查
        if df.empty or len(df) < 200: return None
        
        curr = df.iloc[-1]
        
        # 1. 基礎數據 (強制轉型防止 AttributeError)
        close = float(curr['Close'])
        high = float(curr['High'])
        low = float(curr['Low'])
        
        # 均線計算
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 2. 趨勢過濾 (Trend Filter)
        # J Law 鐵律：股價 > 200MA (長期多頭)
        if close < ma200: return None
        
        # 3. 指標運算
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = float(curr['Volume']) / avg_vol
        
        pattern = ""
        score = 0
        report = []
        
        # --- 戰術型態識別 ---
        
        # A. Tennis Ball Action (20MA 回測)
        dist_20 = (low - ma20) / ma20
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern = "🎾 Tennis Ball (20MA)"
            score = 90
            report.append(f"✅ **型態確認**：股價有序回測 20日均線 (${ma20:.2f})，呈現自然的網球反彈行為。")
            
        # B. Power Trend (10MA 強勢)
        elif abs((low - ma10)/ma10) <= 0.025 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            score = 95
            report.append(f"✅ **型態確認**：超級動能狀態。股價沿著 10日均線 (${ma10:.2f}) 攀升，顯示機構強烈惜售。")
        
        # C. 50MA Defense (機構防線)
        elif abs((low - ma50)/ma50) <= 0.03 and close > ma50:
            pattern = "🛡️ Base Support (50MA)"
            score = 80
            report.append(f"✅ **型態確認**：回測 50日中期均線 (${ma50:.2f})，此處為大型機構的成本防守區。")
        else:
            return None # 不符合任何形態，直接丟棄
            
        # --- 量能分析 ---
        if vol_ratio < 0.75:
            report.append(f"💧 **量能特徵**：極度量縮 (VCP)，今日成交量僅均量的 {int(vol_ratio*100)}%，賣壓枯竭。")
            score += 5
        elif vol_ratio > 1.5:
            report.append(f"🚀 **量能特徵**：帶量攻擊，成交量放大至 {vol_ratio:.1f}倍，主力資金進駐。")
            
        # --- 交易計劃 ---
        entry = high + (atr * 0.1) # 突破高點
        
        # 智能止損
        if "10MA" in pattern: stop = ma20 - (atr*0.1)
        elif "20MA" in pattern: stop = low - (atr*0.2)
        else: stop = ma50 - (atr*0.1)
        
        if entry <= stop: return None
        
        risk = entry - stop
        target = entry + (risk * 3)
        risk_pct = (risk / entry) * 100
        
        return {
            "Symbol": ticker,
            "Pattern": pattern,
            "Score": score,
            "Close": close,
            "Entry": entry,
            "Stop": stop,
            "Target": target,
            "RiskPct": risk_pct,
            "Report": "\n".join(report)
        }
    except Exception as e:
        return None

# ==========================================
# 4. 介面渲染
# ==========================================
def display_analysis(row):
    # 標題區
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #333; padding-bottom:10px; margin-bottom:20px;">
        <div>
            <span style="font-size:42px; font-weight:800; color:#fff;">{row['Symbol']}</span>
            <span style="font-size:16px; background:#00E676; color:#000; padding:4px 8px; border-radius:4px; margin-left:10px; font-weight:bold;">{row['Pattern']}</span>
        </div>
        <div style="text-align:right;">
            <div style="font-size:12px; color:#888;">STRATEGY SCORE</div>
            <div style="font-size:32px; color:#00E676; font-weight:bold;">{row['Score']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 戰術儀表板
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-box"><div class="stat-label">CURRENT PRICE</div><div class="stat-val">${row["Close"]:.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-box" style="border-top:3px solid #00E676"><div class="stat-label">BUY TRIGGER</div><div class="stat-val" style="color:#00E676">${row["Entry"]:.2f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-box" style="border-top:3px solid #FF1744"><div class="stat-label">STOP LOSS</div><div class="stat-val" style="color:#FF1744">${row["Stop"]:.2f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-box"><div class="stat-label">RISK %</div><div class="stat-val">{row["RiskPct"]:.2f}%</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # 深度分析報告
    st.markdown(f"""
    <div class="analysis-panel">
        <h4 style="color:#fff; margin-top:0;">🦅 J LAW TACTICAL REPORT</h4>
        <div style="color:#ccc; font-size:15px; white-space: pre-line;">
        {row['Report']}
        </div>
        <br>
        <div style="border-top:1px solid #333; padding-top:10px; font-size:13px; color:#888;">
            <b>🎯 EXECUTION:</b> Place a <u>Stop Limit Buy Order</u> at <b>${row['Entry']:.2f}</b>. <br>Target Profit: <b>${row['Target']:.2f} (3R)</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TradingView 圖表
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:600px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
        "locale": "en", "toolbar_bg": "#f1f3f6", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
        "container_id": "tv_{row['Symbol']}",
        "studies": ["MASimple@tv-basicstudies","MASimple@tv-basicstudies","MASimple@tv-basicstudies"],
        "studies_overrides": {{ "MASimple@tv-basicstudies.length": 10, "MASimple@tv-basicstudies.length": 20, "MASimple@tv-basicstudies.length": 50 }}
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=610)

# ==========================================
# 5. 主程式
# ==========================================

# 狀態初始化 (這裡修復了上一版的 Bug)
if 'scan_data' not in st.session_state: 
    st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: 
    st.session_state['watchlist'] = ["TSLA", "NVDA", "MSTR"]

with st.sidebar:
    st.markdown("### 🦅 ALPHA STATION")
    mode = st.radio("MODULE", ["⚡ 掃描全美強勢股 (Mega Scan)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    
    st.markdown("---")
    
    if mode == "⚡ 掃描全美強勢股 (Mega Scan)":
        st.info("掃描目標：華爾街 Top 100 最熱門交易標的 (S&P/Nasdaq Leaders)")
        if st.button("🚀 啟動全市場掃描", use_container_width=True):
            
            # 1. 獲取內建清單
            tickers = get_market_tickers()
            
            # 2. 顯示進度
            status = st.status(f"正在連線 Yahoo Finance 分析 {len(tickers)} 隻股票...", expanded=True)
            
            # 3. 批量下載 (效率優化)
            data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
            
            results = []
            progress_bar = status.progress(0)
            
            for i, ticker in enumerate(tickers):
                # 更新進度條
                progress_bar.progress((i + 1) / len(tickers))
                try:
                    # 處理數據結構
                    if len(tickers) > 1:
                        if ticker not in data.columns.levels[0]: continue
                        df = data[ticker].dropna()
                    else: df = data
                    
                    # 執行演算法
                    res = analyze_stock_pro(ticker, df)
                    if res: results.append(res)
                except: continue
            
            status.update(label="分析完成！", state="complete", expanded=False)
            
            if results:
                st.session_state['scan_data'] = pd.DataFrame(results).sort_values('Score', ascending=False)
            else:
                st.session_state['scan_data'] = pd.DataFrame()

# 頁面內容
if mode == "⚡ 掃描全美強勢股 (Mega Scan)":
    st.title("⚡ MARKET SCANNER")
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("👈 等待指令：請點擊左側 [ 啟動全市場掃描 ] 。系統將自動篩選市場領頭羊。")
    elif df.empty:
        st.warning("⚠️ 掃描完成：今日市場環境較差，在 Top 100 強勢股中未發現符合 J Law 嚴格標準的標的。")
    else:
        c_list, c_main = st.columns([1, 3.5])
        with c_list:
            st.markdown(f"**FOUND: {len(df)} STOCKS**")
            sel = st.radio("Results", df['Symbol'].tolist(), 
                         format_func=lambda x: f"{x}  [{df[df['Symbol']==x]['Score'].values[0]}]",
                         label_visibility="collapsed")
        with c_main:
            row = df[df['Symbol'] == sel].iloc[0]
            display_analysis(row)

elif mode == "👀 觀察名單 (Watchlist)":
    st.title("👀 WATCHLIST")
    c1, c2 = st.columns([1, 4])
    with c1:
        t_in = st.text_input("Add Symbol", "").upper()
        if st.button("➕") and t_in: 
            if t_in not in st.session_state['watchlist']: st.session_state['watchlist'].append(t_in)
        sel = st.radio("List", st.session_state['watchlist'], label_visibility="collapsed")
    with c2:
        if sel:
            d = yf.download(sel, period="1y", progress=False)
            if not d.empty:
                r = analyze_stock_pro(sel, d)
                if r: display_analysis(r)
                else:
                    st.header(f"{sel} - Monitoring")
                    st.info("No active setup detected based on J Law rules.")
                    curr = d['Close'].iloc[-1]
                    st.metric("Price", f"${curr:.2f}")
                    components.html(f"""<div class="tradingview-widget-container" style="height:500px;width:100%"><div id="tv_{sel}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{sel}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_{sel}" }});</script></div>""", height=510)

elif mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h1 style='text-align:center;'>⚡ TESLA INTELLIGENCE</h1>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.link_button("News", "https://www.google.com/search?q=Tesla+stock&tbm=nws", use_container_width=True)
    c2.link_button("Elon X", "https://twitter.com/elonmusk", use_container_width=True)
    c3.link_button("Chart", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)
    st.divider()
    
    cl, cr = st.columns([1, 2])
    with cl:
        try:
            t = yf.Ticker("TSLA")
            h = t.history(period="1d")
            curr = h['Close'].iloc[-1]
            op = h['Open'].iloc[0]
            clr = "#00E676" if curr>=op else "#FF1744"
            st.markdown(f"<div style='text-align:center; background:rgba(0,0,0,0.5); padding:30px; border:1px solid {clr}; border-radius:10px;'><h1 style='color:{clr}; font-size:50px; margin:0'>${curr:.2f}</h1></div>", unsafe_allow_html=True)
        except: pass
        components.html("""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{ "symbol": "NASDAQ:TSLA", "width": "100%", "height": "350", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }</script></div>""", height=360)
        
    with cr:
        st.markdown("### Social Stream")
        try:
            r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/TSLA.json", headers={'User-Agent':'Mozilla/5.0'}, timeout=2)
            for m in r.json().get('messages', [])[:6]:
                u = m['user']['username']
                b = m['body']
                st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:10px; margin-bottom:8px; border-radius:5px; border-left:3px solid #2962FF'><b style='color:#ccc'>@{u}</b><br><span style='color:#eee; font-size:13px'>{b}</span></div>", unsafe_allow_html=True)
        except: st.info("Loading Social Data...")
