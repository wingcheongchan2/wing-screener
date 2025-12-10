import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. 專業級 UI 設定 (Bloomberg 風格)
# ==========================================
st.set_page_config(page_title="J Law Alpha Trader", layout="wide", page_icon="🦅")

# 黑金戰情室風格 CSS
st.markdown("""
<style>
    /* 全局背景 */
    .stApp { background-color: #000000; color: #e0e0e0; }
    
    /* 側邊欄 */
    section[data-testid="stSidebar"] { background-color: #111111; }
    
    /* 按鈕特效 */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00C853 0%, #009624 100%);
        color: white; border: none; font-weight: bold; padding: 10px; font-size: 16px;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #00E676 0%, #00C853 100%);
        box-shadow: 0 0 15px rgba(0, 200, 83, 0.6);
    }

    /* 評分卡片 */
    .score-card {
        background-color: #1a1a1a; border: 1px solid #333; border-radius: 10px;
        padding: 20px; text-align: center; margin-bottom: 20px;
    }
    .score-val { font-size: 36px; font-weight: 900; }
    .score-high { color: #00E676; text-shadow: 0 0 10px rgba(0,230,118,0.5); }
    .score-med { color: #FFD600; }
    .score-low { color: #FF1744; }
    
    /* 交易計劃框 */
    .plan-box {
        background-color: #0d1117; border-left: 5px solid #00E676;
        padding: 15px; margin: 10px 0; border-radius: 5px;
    }
    .plan-label { font-size: 12px; color: #888; text-transform: uppercase; }
    .plan-price { font-size: 20px; font-weight: bold; color: #fff; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 J Law 冠軍操盤室：自動獲利系統")
st.markdown("---")

# ==========================================
# 2. 自動化掃描核心 (核心大腦)
# ==========================================

@st.cache_data
def get_target_pool():
    # J Law 精選流動性高、波動大的優質股 (High Beta)
    return [
        "NVDA", "TSLA", "AMD", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "NFLX",
        "COIN", "MSTR", "MARA", "RIOT", "HOOD", "PLTR", "SOFI", "UPST", "AFRM",
        "SMCI", "ARM", "AVGO", "MU", "QCOM", "TSM", "MRVL", "LRCX", "AMAT",
        "CRWD", "PANW", "SNPS", "NOW", "UBER", "DASH", "ABNB", "SQ", "PYPL",
        "JPM", "GS", "V", "MA", "CAT", "DE", "BA", "LULU", "CELH"
    ]

def analyze_stock_pro(ticker, df):
    """
    J Law 核心演算法：計算分數並生成交易計劃
    """
    try:
        if len(df) < 200: return None
        
        # 提取數據
        curr = df.iloc[-1]
        close = curr['Close']
        high = curr['High']
        low = curr['Low']
        vol = curr['Volume']
        
        # 技術指標計算
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        # --- 1. 評分系統 (0-100分) ---
        score = 0
        reasons = []
        
        # A. 趨勢 (Trend) - 佔 40分
        if close > ma200:
            score += 20
            reasons.append("✅ 長期趨勢向上 (Stage 2)")
            if close > ma50:
                score += 20
                reasons.append("✅ 中期動能強勁")
        else:
            return None # 200MA 以下直接淘汰 (不浪費時間)

        # B. 位置 (Location) - 佔 40分
        # 尋找 "Tennis Ball Action" (回測 20MA)
        dist_20 = (close - ma20) / ma20
        dist_10 = (close - ma10) / ma10
        
        if -0.02 <= dist_20 <= 0.03: # 在 20MA 附近 (誤差3%)
            score += 40
            reasons.append("🎯 完美回測 20MA (網球行為)")
        elif -0.02 <= dist_10 <= 0.02: # 在 10MA 附近 (超強勢)
            score += 35
            reasons.append("🔥 回測 10MA (超強勢整理)")
        elif 0.03 < dist_20 < 0.08:
            score += 15
            reasons.append("⚠️ 略微偏離 (等待回調)")
        else:
            reasons.append("❌ 乖離過大 (勿追高)")
            
        # C. 量能 (Volume) - 佔 20分
        vol_ratio = vol / avg_vol
        if vol_ratio < 0.8:
            score += 20
            reasons.append("💧 極致縮量 (無賣壓)")
        elif vol_ratio < 1.2:
            score += 10
            reasons.append("👌 量能正常")
        else:
            reasons.append("🔊 爆量 (需小心出貨)")
            
        # --- 2. 交易計劃生成 (The Money Maker) ---
        # 進場：突破今日高點 + 0.1 ATR (確認訊號)
        entry_price = high + (atr * 0.05)
        # 止蝕：跌破今日低點 - 0.1 ATR
        stop_loss = low - (atr * 0.05)
        
        # 若止損太窄，使用 20MA 作為防守
        if entry_price - stop_loss < (close * 0.015):
             stop_loss = min(stop_loss, ma20 * 0.99)
             
        risk = entry_price - stop_loss
        target_2r = entry_price + (risk * 2)
        target_3r = entry_price + (risk * 3)
        
        return {
            "Symbol": ticker,
            "Score": score,
            "Price": close,
            "Entry": round(entry_price, 2),
            "Stop": round(stop_loss, 2),
            "Risk": round(risk, 2),
            "Target_2R": round(target_2r, 2),
            "Target_3R": round(target_3r, 2),
            "Reasons": reasons,
            "Vol_Ratio": round(vol_ratio, 2),
            "MA20": round(ma20, 2)
        }
    except:
        return None

# ==========================================
# 3. 側邊欄：資金與操作
# ==========================================
with st.sidebar:
    st.header("💰 資金控管中心")
    account_size = st.number_input("總資金 (USD)", value=10000, step=1000)
    risk_pct = st.slider("單筆風險 (%)", 0.5, 3.0, 1.0)
    
    max_loss = account_size * (risk_pct / 100)
    st.info(f"🛡️ 單筆最大虧損限制： **${max_loss:.0f}**")
    
    st.markdown("---")
    st.header("🚀 掃描控制")
    run_scan = st.button("開始自動掃描", use_container_width=True)
    st.caption("掃描美股 Top 60 流動性最佳標的")

# ==========================================
# 4. 主程序與顯示邏輯
# ==========================================

# 初始化 Session
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

if run_scan:
    tickers = get_target_pool()
    data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, t in enumerate(tickers):
        progress_bar.progress((i+1)/len(tickers))
        status_text.text(f"正在分析: {t} ...")
        
        try:
            if len(tickers) == 1: df = data
            else: 
                if t not in data.columns.levels[0]: continue
                df = data[t].dropna()
            
            res = analyze_stock_pro(t, df)
            if res and res['Score'] >= 60: # 只顯示 60 分以上的
                results.append(res)
        except: continue
        
    progress_bar.empty()
    status_text.empty()
    
    if results:
        # 依分數排序
        df_res = pd.DataFrame(results).sort_values(by='Score', ascending=False)
        st.session_state['scan_results'] = df_res
        st.success(f"✅ 掃描完成！發現 {len(results)} 個潛在獲利機會。")
    else:
        st.warning("⚠️ 市場目前狀況不佳，沒有發現高分 Setup，建議空手觀望。")

# --- 顯示結果 ---
if st.session_state['scan_results'] is not None:
    df = st.session_state['scan_results']
    
    # 使用 Tabs 分頁
    tab1, tab2 = st.tabs(["🏆 冠軍精選 (Top Picks)", "📋 完整清單"])
    
    with tab1:
        # 顯示前 3 名
        top_picks = df.head(5)
        
        for index, row in top_picks.iterrows():
            # 計算股數
            shares = int(max_loss / row['Risk']) if row['Risk'] > 0 else 0
            position_size = shares * row['Entry']
            
            # 卡片容器
            with st.container():
                # 標題列
                c1, c2, c3 = st.columns([1, 1, 2])
                with c1:
                    st.markdown(f"## {row['Symbol']}")
                with c2:
                    score_color = "score-high" if row['Score'] >= 80 else "score-med"
                    st.markdown(f"<div class='score-val {score_color}'>{row['Score']}分</div>", unsafe_allow_html=True)
                with c3:
                    st.markdown("**分析理由：**")
                    for r in row['Reasons']:
                        st.markdown(f"- {r}")
                
                st.markdown("---")
                
                # 交易計劃核心區 (Money Zone)
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.markdown('<div class="plan-box"><div class="plan-label">🔵 進場價 (Buy Stop)</div><div class="plan-price">${}</div></div>'.format(row['Entry']), unsafe_allow_html=True)
                with k2:
                    st.markdown('<div class="plan-box"><div class="plan-label">🔴 止蝕價 (Stop Loss)</div><div class="plan-price" style="color:#FF1744">${}</div></div>'.format(row['Stop']), unsafe_allow_html=True)
                with k3:
                    st.markdown('<div class="plan-box"><div class="plan-label">🎯 第一目標 (2R)</div><div class="plan-price" style="color:#00E676">${}</div></div>'.format(row['Target_2R']), unsafe_allow_html=True)
                with k4:
                    st.markdown(f'<div class="plan-box"><div class="plan-label">💰 建議股數</div><div class="plan-price" style="color:#FFD600">{shares} 股</div></div>', unsafe_allow_html=True)
                
                st.caption(f"⚠️ 此筆交易預計風險: ${max_loss:.0f} (佔總資金 {risk_pct}%) | 倉位總值: ${position_size:.0f}")

                # 嵌入 TradingView 圖表
                st.components.v1.html(f"""
                <div class="tradingview-widget-container">
                  <div id="tv_{row['Symbol']}"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget(
                  {{
                    "width": "100%", "height": 400, "symbol": "{row['Symbol']}",
                    "interval": "D", "timezone": "Exchange", "theme": "dark",
                    "style": "1", "locale": "zh_TW", "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false, "hide_side_toolbar": false,
                    "allow_symbol_change": true, "container_id": "tv_{row['Symbol']}",
                    "studies": ["MASimple@tv-basicstudies"]
                  }});
                  </script>
                </div>
                """, height=410)
                
                st.divider()

    with tab2:
        st.dataframe(df[['Symbol', 'Score', 'Price', 'Entry', 'Stop', 'Risk', 'Target_3R', 'Vol_Ratio']], use_container_width=True)

else:
    # 歡迎畫面
    st.info("👈 請在左側設定你的資金，然後點擊「開始自動掃描」。")
    
    st.markdown("""
    ### 🦅 J Law 獲利法則 (系統邏輯)
    1.  **Trend is King**: 系統只會搜尋 **200MA** 之上的股票。
    2.  **Buy the Pullback**: 尋找回測 **20MA (網球行為)** 的機會。
    3.  **Risk First**: 先算會賠多少，再算會賺多少。
    
    **如何使用本系統賺錢：**
    1.  點擊掃描。
    2.  專注於 **80分以上 (綠色分數)** 的股票。
    3.  在券商設定 **Buy Stop (觸價單)** = 系統顯示的進場價。
    4.  **不到價不進場**，嚴格執行系統給出的股數。
    """)
