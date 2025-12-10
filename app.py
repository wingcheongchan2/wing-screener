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
    }}
    div[role="radiogroup"] > label:hover {{
        border-color: #00E676;
        background: rgba(0, 230, 118, 0.1);
        transform: translateX(5px);
    }}
    div[role="radiogroup"] > label[data-checked="true"] {{
        background: linear-gradient(90deg, #00C853, transparent);
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
# 2. 自動擴充市場宇宙 (The Mega Universe)
# ==========================================
@st.cache_data
def get_market_tickers():
    """
    自動從 Wikipedia 抓取 S&P 500 和 Nasdaq 100 成分股。
    這是目前最快能獲取「市場上最重要股票」的方法。
    """
    tickers = []
    try:
        # 1. 抓取 S&P 500
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        tickers.extend(sp500['Symbol'].tolist())
        
        # 2. 抓取 Nasdaq 100 (動能股集中地)
        # 由於 Wiki 結構常變，這裡我們手動補充一些熱門動能股以防萬一
        tech_growth = [
            "PLTR", "MSTR", "COIN", "APP", "HOOD", "DKNG", "UPST", "AFRM", "RIVN", 
            "CVNA", "MARA", "CLSK", "RIOT", "HUT", "SOFI", "PATH", "U", "AI", "SMCI",
            "ARM", "CART", "RDDT", "ALAB", "VRT"
        ]
        tickers.extend(tech_growth)
        
        # 去重並修正 (BRK.B -> BRK-B)
        tickers = [t.replace('.', '-') for t in tickers]
        tickers = list(set(tickers)) # 去除重複
        
        return tickers # 返回約 500-550 隻股票
    except Exception as e:
        # 如果抓取失敗，回傳核心備用名單
        return ["NVDA", "TSLA", "AMD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "PLTR", "COIN", "MSTR", "SMCI"]

# ==========================================
# 3. J Law 核心運算引擎 (深度量化)
# ==========================================
def analyze_stock_pro(ticker, df):
    try:
        if len(df) < 200: return None
        curr = df.iloc[-1]
        
        # 1. 基礎數據
        close = float(curr['Close'])
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 2. 趨勢過濾 (Trend Filter) - J Law 第一條鐵律
        # 股價必須高於 200MA，且 50MA > 200MA (黃金交叉後)
        if close < ma200: return None
        if ma50 < ma200: return None
        
        # 3. 指標運算
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = float(curr['Volume']) / avg_vol
        
        pattern = ""
        score = 0
        report = []
        
        # --- 戰術型態識別 ---
        
        # A. Tennis Ball Action (20MA 回測)
        # 定義：股價回落到 20MA 附近 (差距3.5%內) 且沒有跌破太遠
        dist_20 = (curr['Low'] - ma20) / ma20
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern = "🎾 Tennis Ball (20MA)"
            score = 90
            report.append(f"✅ **型態確認**：股價有序回測 20日均線 (${ma20:.2f})，呈現自然的網球反彈行為。")
            
        # B. Power Trend (10MA 強勢)
        # 定義：股價極強，根本不回測 20MA，只在 10MA 附近整理
        elif abs((curr['Low'] - ma10)/ma10) <= 0.025 and close > ma10:
            pattern = "🔥 Power Trend (10MA)"
            score = 95
            report.append(f"✅ **型態確認**：超級動能狀態。股價沿著 10日均線 (${ma10:.2f}) 攀升，顯示機構強烈惜售，不願讓股價回調。")
        
        # C. 50MA Defense (機構防線)
        elif abs((curr['Low'] - ma50)/ma50) <= 0.03 and close > ma50:
            pattern = "🛡️ Base Support (50MA)"
            score = 80
            report.append(f"✅ **型態確認**：回測 50日中期均線 (${ma50:.2f})，此處為大型機構的成本防守區。")
        else:
            return None # 不符合任何形態，直接丟棄
            
        # --- 量能分析 ---
        if vol_ratio < 0.75:
            report.append(f"💧 **量能特徵**：極度量縮 (VCP)，今日成交量僅均量的 {int(vol_ratio*100)}%，賣壓枯竭。")
            score += 5
        elif vol_ratio > 1.5 and close > df.iloc[-2]['Close']:
            report.append(f"🚀 **量能特徵**：帶量攻擊，有主力資金進駐點火。")
            
        # --- 交易計劃 ---
        entry = curr['High'] + (atr * 0.1) # 突破高點
        
        # 智能止損
        if "10MA" in pattern: stop = ma20 - (atr*0.1)
        elif "20MA" in pattern: stop = curr['Low'] - (atr*0.2)
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
    except: return None

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
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_s
