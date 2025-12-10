import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components

# ==========================================
# 1. 系統視覺核心 (Safe CSS & Background Logic)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 1. 主畫面背景：型格暗黑數據流
MAIN_BG_URL = "https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2070&auto=format&fit=crop"

# 2. TSLA 專屬背景：黑色底 + 紅色 Logo
TSLA_BG_URL = "https://c4.wallpaperflare.com/wallpaper/478/486/477/tesla-motors-logo-tesla-red-background-wallpaper-preview.jpg"

def inject_css(current_mode):
    # 決定背景圖
    if current_mode == "⚡ TSLA 戰情室 (Intel)":
        target_bg = TSLA_BG_URL
        # 紅色 Logo 背景不需要太深遮罩
        overlay = "rgba(0,0,0,0.7), rgba(0,0,0,0.9)" 
    else:
        target_bg = MAIN_BG_URL
        # 主背景需要深色遮罩
        overlay = "rgba(0,0,0,0.85), rgba(0,0,0,0.95)"

    # CSS 樣式表 (純文字拼接，防止語法錯誤)
    style_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

        /* 全局背景 */
        .stApp {{
            background-image: linear-gradient({overlay}), url("{target_bg}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #E0E0E0;
            font-family: 'Noto Sans TC', sans-serif;
        }}
        
        /* 側邊欄 */
        section[data-testid="stSidebar"] {{
            background: rgba(5, 5, 5, 0.95);
            border-right: 1px solid #333;
            backdrop-filter: blur(10px);
        }}
        
        /* 股票列表：數據磁貼風格 */
        div[role="radiogroup"] > label > div:first-child {{ display: none !important; }}
        div[role="radiogroup"] {{ gap: 5px; }}
        
        div[role="radiogroup"] > label {{
            background: rgba(255,255,255,0.03);
            border: 1px solid #333;
            padding: 12px 15px;
            border-radius: 4px;
            transition: all 0.2s;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #aaa;
            cursor: pointer;
        }}
        
        div[role="radiogroup"] > label:hover {{
            border-color: #00E676;
            color: #fff;
            background: rgba(0, 230, 118, 0.05);
            transform: translateX(3px);
        }}
        
        div[role="radiogroup"] > label[data-checked="true"] {{
            background: #000 !important;
            border: 1px solid #00E676;
            box-shadow: 0 0 10px rgba(0, 230, 118, 0.2);
            color: #00E676 !important;
            font-weight: 700;
        }}

        /* 數據卡片 */
        .stat-card {{
            background: rgba(20,20,20,0.8);
            border: 1px solid #333;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-label {{ font-size: 12px; color: #888; letter-spacing: 1px; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #fff; margin-top: 5px; font-family: 'JetBrains Mono'; }}

        /* 報告面板 */
        .report-panel {{
            background: rgba(10, 10, 10, 0.9);
            border: 1px solid #333;
            border-left: 4px solid #00E676;
            padding: 25px;
            border-radius: 4px;
            font-family: 'Noto Sans TC', sans-serif;
            line-height: 1.8;
            font-size: 15px;
            margin-bottom: 20px;
        }}
        .report-hl {{ color: #00E676; font-weight: bold; }}
        .report-risk {{ color: #FF1744; font-weight: bold; }}
        
        /* 按鈕 */
        div.stButton > button {{
            background: transparent;
            border: 1px solid #00E676;
            color: #00E676;
            border-radius: 4px;
            font-family: 'Noto Sans TC';
            font-weight: bold;
        }}
        div.stButton > button:hover {{
            background: rgba(0, 230, 118, 0.1);
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.3);
        }}
        
        h1, h2, h3 {{ color: #fff; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}
    </style>
    """
    st.markdown(style_code, unsafe_allow_html=True)

# ==========================================
# 2. 市場核心清單
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
# 3. J Law 核心大腦 (數據安全版)
# ==========================================
def analyze_stock_pro(ticker, df):
    try:
        if len(df) < 200: return None
        curr = df.iloc[-1]
        
        # 安全獲取數值 (防止 Series 錯誤)
        try:
            close = float(curr['Close'])
            high = float(curr['High'])
            low = float(curr['Low'])
            vol = float(curr['Volume'])
        except:
            # 如果是 Series，取第一個值
            close = float(curr['Close'].iloc[0]) if hasattr(curr['Close'], 'iloc') else float(curr['Close'])
            high = float(curr['High'].iloc[0]) if hasattr(curr['High'], 'iloc') else float(curr['High'])
            low = float(curr['Low'].iloc[0]) if hasattr(curr['Low'], 'iloc') else float(curr['Low'])
            vol = float(curr['Volume'].iloc[0]) if hasattr(curr['Volume'], 'iloc') else float(curr['Volume'])
        
        # 指標
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        
        # 避免除以零
        if avg_vol == 0: vol_ratio = 1.0
        else: vol_ratio = vol / avg_vol
        
        # 趨勢過濾
        if close < ma200: return None
        
        pattern = ""
        score = 0
        analysis_lines = []
        
        # --- 型態識別 ---
        # A. Tennis Ball (20MA)
        dist_20 = (low - ma20) / ma20
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern = "🎾 Tennis Ball (網球行為)"
            score = 90
            analysis_lines.append(f"📈 **趨勢解讀**：股價長期趨勢向上，目前有序回測 20日均線 (${ma20:.2f})。")
            analysis_lines.append(f"✅ **型態確認**：股價觸及均線後有支撐，如同網球落地反彈，機構仍在控盤。")

        # B. Power Trend (10MA)
        elif abs((low - ma10)/ma10) <= 0.025 and close > ma10:
            pattern = "🔥 Power Trend (強力趨勢)"
            score = 95
            analysis_lines.append(f"📈 **趨勢解讀**：進入超級動能狀態！股價緊貼 10日均線 (${ma10:.2f}) 攀升。")
            analysis_lines.append(f"✅ **型態確認**：最強勢持有訊號，市場惜售心理極強。")

        # C. 50MA Defense
        elif abs((low - ma50)/ma50) <= 0.03 and close > ma50:
            pattern = "🛡️ Base Support (50MA防線)"
            score = 80
            analysis_lines.append(f"📈 **趨勢解讀**：中期修正波段，回測 50日機構成本線 (${ma50:.2f})。")
            analysis_lines.append(f"✅ **型態確認**：多頭最後防線，觀察是否出現止跌 K 線。")
        else:
            return None 
            
        # 量能分析
        if vol_ratio < 0.75:
            analysis_lines.append(f"💧 **量能籌碼**：出現 VCP 特徵！量縮至均量的 {int(vol_ratio*100)}%，浮額清洗完畢。")
            score += 5
        elif vol_ratio > 1.5:
            analysis_lines.append(f"🚀 **量能籌碼**：爆量攻擊！成交量放大至 {vol_ratio:.1f}倍，大戶資金進場。")
            
        # 交易計劃
        entry_price = high + (atr * 0.1)
        
        if "10MA" in pattern: stop_price = ma20 - (atr * 0.1)
        elif "20MA" in pattern: stop_price = low - (atr * 0.2)
        else: stop_price = ma50 - (atr * 0.1)
        
        if entry_price <= stop_price: return None
        
        risk_per_share = entry_price - stop_price
        target_price = entry_price + (risk_per_share * 3)
        risk_pct = (risk_per_share / entry_price) * 100
        rr_ratio = (target_price - entry_price) / risk_per_share
        
        analysis_lines.append(f"⚠️ **風險評估**：單筆風險為 -{risk_pct:.2f}%。")
        
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
    except: return None

def display_dashboard(row):
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid #333; padding-bottom:15px; margin-bottom:20px;">
        <div>
            <span style="color:#00E676; font-size:14px; font-weight:bold;">STOCK TICKER</span><br>
            <span style="font-size:48px; font-weight:900; letter-spacing:-1px; color:#fff;">{row['Symbol']}</span>
            <span style="background:rgba(0, 230, 118, 0.1); color:#00E676; border:1px solid #00E676; padding:2px 8px; font-size:12px; margin-left:10px;">{row['Pattern']}</span>
        </div>
        <div style="text-align:right;">
            <span style="color:#888; font-size:12px;">AI 戰術評分</span><br>
            <span style="font-size:36px; font-weight:700; color:#00E676;">{row['Score']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    # 這裡加上 float 轉換，防止報錯
    c1.markdown(f'<div class="stat-card"><div class="stat-label">現價 PRICE</div><div class="stat-value">${float(row["Close"]):.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card" style="border-bottom:3px solid #00E676"><div class="stat-label">買入 ENTRY</div><div class="stat-value" style="color:#00E676">${float(row["Entry"]):.2f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card" style="border-bottom:3px solid #FF1744"><div class="stat-label">止蝕 STOP</div><div class="stat-value" style="color:#FF1744">${float(row["Stop"]):.2f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-label">目標 TARGET (3R)</div><div class="stat-value">${float(row["Target"]):.2f}</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    st.markdown(f"""
    <div class="report-panel">
        <div style="border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:10px;">
            <span class="report-hl">⚡ J LAW 戰術分析報告</span>
        </div>
        {row['Report']}
        <br><br>
        <div style="border-top:1px solid #333; padding-top:15px; color:#aaa; font-size:14px;">
            <span class="report-hl">🎯 交易執行計劃 (Execution):</span><br>
            1. 請在券商設定 <b>Stop Limit Buy Order (觸價買單)</b> 於 <b>${float(row['Entry']):.2f}</b>。<br>
            2. 一旦成交，立即設定硬性止損單於 <b class="report-risk">${float(row['Stop']):.2f}</b>。<br>
            3. 此交易預期風險回報比 (R/R) 為 <b>1:{float(row['RR']):.1f}</b>。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tv_html = f"""
    <div class="tradingview-widget-container" style="height:600px;width:100%">
      <div id="tv_{row['Symbol']}" style="height:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
        "locale": "zh_TW", "toolbar_bg": "#000", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
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
    st.markdown("### 🦅 ALPHA STATION <span style='font-size:10px; color:#00E676; border:1px solid #00E676; padding:1px 3px;'>V13.0</span>", unsafe_allow_html=True)
    # 這裡決定 current_mode
    mode = st.radio("系統模組", ["⚡ 強勢股掃描器 (Scanner)", "👀 觀察名單 (Watchlist)", "⚡ TSLA 戰情室 (Intel)"])
    
    # 立即注入 CSS 確保背景正確切換
    inject_css(mode)
    
    st.markdown("---")
    
    if mode == "⚡ 強勢股掃描器 (Scanner)":
        st.caption("監控目標：華爾街熱門交易標的")
        if st.button("🔥 啟動全市場掃描", use_container_width=True):
            universe = get_market_universe()
            status = st.status("正在連線華爾街數據庫...", expanded=True)
            
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
                
            status.update(label="掃描完成", state="complete", expanded=False)
            
            if results:
                st.session_state['scan_data'] = pd.DataFrame(results).sort_values('Score', ascending=False)
            else:
                st.session_state['scan_data'] = pd.DataFrame()

# 頁面渲染
if mode == "⚡ 強勢股掃描器 (Scanner)":
    st.title("⚡ 強勢股掃描器")
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("系統待命。請點擊左側 [ 🔥 啟動全市場掃描 ] 。")
    elif df.empty:
        st.warning("⚠️ 掃描完成：今日市場環境較差，未發現符合 J Law 標準的標的。")
    else:
        c_list, c_main = st.columns([1, 4])
        with c_list:
            st.markdown(f"<div style='margin-bottom:10px; color:#888; font-size:12px;'>掃描結果 ({len(df)})</div>", unsafe_allow_html=True)
            sel = st.radio("Results", df['Symbol'].tolist(), 
                         format_func=lambda x: f"{x}  [{df[df['Symbol']==x]['Score'].values[0]}]",
                         label_visibility="collapsed")
        with c_main:
            row = df[df['Symbol'] == sel].iloc[0]
            display_dashboard(row)

elif mode == "👀 觀察名單 (Watchlist)":
    st.title("👀 我的觀察名單")
    c1, c2 = st.columns([1, 4])
    with c1:
        new_t = st.text_input("輸入代碼", "").upper()
        if st.button("➕ 新增") and new_t:
            if new_t not in st.session_state['watchlist']: st.session_state['watchlist'].append(new_t)
        sel = st.radio("List", st.session_state['watchlist'], label_visibility="collapsed")
    with c2:
        if sel:
            # 修復 Crash 的關鍵點：增加錯誤處理與類型轉換
            try:
                d = yf.download(sel, period="1y", progress=False)
                if not d.empty:
                    # 安全取價
                    raw_close = d['Close'].iloc[-1]
                    # 如果是 Series (MultiIndex 造成)，取值
                    if isinstance(raw_close, pd.Series):
                        curr_price = float(raw_close.iloc[0])
                    else:
                        curr_price = float(raw_close)
                        
                    r = analyze_stock_pro(sel, d)
                    if r: display_dashboard(r)
                    else:
                        st.header(f"{sel}")
                        st.info("⚠️ 目前無 J Law 戰術訊號，僅顯示即時走勢。")
                        st.metric("現價", f"${curr_price:.2f}")
                        components.html(f"""<div class="tradingview-widget-container" style="height:500px;width:100%"><div id="tv_{sel}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{sel}", "interval": "D", "theme": "dark", "style": "1", "container_id": "tv_{sel}" }});</script></div>""", height=510)
            except Exception as e: st.error(f"數據讀取錯誤: {e}")

# --- 模式 3: TSLA 戰情室 (紅色 Logo 背景) ---
elif mode == "⚡ TSLA 戰情室 (Intel)":
    st.markdown("<h1 style='text-align:center; color:#fff; text-shadow:0 0 20px #D50000;'>⚡ TESLA 戰情室</h1>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.link_button("Google News", "https://www.google.com/search?q=Tesla+stock&tbm=nws", use_container_width=True)
    c2.link_button("Elon Musk X", "https://twitter.com/elonmusk", use_container_width=True)
    c3.link_button("TradingView", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)
    st.divider()
    
    cl, cr = st.columns([1, 2])
    with cl:
        try:
            t = yf.Ticker("TSLA")
            h = t.history(period="1d")
            # 同樣強制轉型
            raw_close = h['Close'].iloc[-1]
            raw_open = h['Open'].iloc[0]
            curr = float(raw_close.iloc[0]) if isinstance(raw_close, pd.Series) else float(raw_close)
            op = float(raw_open.iloc[0]) if isinstance(raw_open, pd.Series) else float(raw_open)
            
            clr = "#00E676" if curr>=op else "#FF1744"
            st.markdown(f"<div style='text-align:center; background:rgba(0,0,0,0.8); padding:30px; border:1px solid {clr}; border-radius:4px;'><h1 style='color:{clr}; font-size:48px; margin:0; font-family:JetBrains Mono'>${curr:.2f}</h1></div>", unsafe_allow_html=True)
        except: pass
        components.html("""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{ "symbol": "NASDAQ:TSLA", "width": "100%", "height": "350", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }</script></div>""", height=360)
        
    with cr:
        st.markdown("### 💬 社群情緒")
        try:
            r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/TSLA.json", headers={'User-Agent':'Mozilla/5.0'}, timeout=2)
            for m in r.json().get('messages', [])[:5]:
                u = m['user']['username']
                b = m['body']
                st.markdown(f"<div style='background:rgba(0,0,0,0.8); padding:12px; margin-bottom:8px; border-radius:4px; border-left:3px solid #D50000; font-family:Noto Sans TC; font-size:13px;'><strong style='color:#D50000'>@{u}</strong><br><span style='color:#ccc'>{b}</span></div>", unsafe_allow_html=True)
        except: st.info("載入中...")
