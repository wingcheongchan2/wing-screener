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
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        font-weight: 800;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        box-shadow: 0 0 15px rgba(0, 200, 83, 0.4);
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 200, 83, 0.7);
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
    .stock-card:hover {
        border-color: #00C853;
        background: rgba(255, 255, 255, 0.08);
    }

    /* 數據格子 */
    .stat-box {
        background: #111;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        border-top: 3px solid #333;
    }
    .stat-box.green { border-top-color: #00E676; }
    .stat-box.red { border-top-color: #FF1744; }
    .stat-box.blue { border-top-color: #2979FF; }

    .stat-label { font-size: 12px; color: #888; letter-spacing: 1px; }
    .stat-value { font-size: 18px; font-weight: bold; color: #fff; margin-top: 5px; }

    /* 標題特效 */
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; font-weight: 700; }
    .highlight { color: #00E676; }
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心大腦：J Law 自動搜尋引擎
# ==========================================

@st.cache_data
def get_tickers():
    # J Law 核心觀察名單 (高動能/流動性佳)
    return [
        "NVDA", "TSLA", "AMD", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "HOOD", 
        "AAPL", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AVGO", "MU", "QCOM", 
        "CRWD", "PANW", "SNPS", "UBER", "ABNB", "DASH", "DKNG", "RIVN", "CVNA", 
        "SOFI", "UPST", "AFRM", "MARA", "RIOT", "CLSK", "HUT", "JPM", "GS", "CAT"
    ]

def analyze_stock_logic(ticker, df):
    """
    執行 J Law 完整技術分析與交易計劃生成
    """
    try:
        if len(df) < 200: return None
        
        curr = df.iloc[-1]
        close = curr['Close']
        open_p = curr['Open']
        high = curr['High']
        low = curr['Low']
        vol = curr['Volume']
        
        # 1. 技術指標運算
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
        
        vol_ratio = vol / avg_vol
        
        # 2. 核心過濾 (The Filter)
        if close < ma200: return None # 趨勢不對，直接淘汰
        
        # 3. 型態識別 (Pattern Recognition)
        pattern = ""
        pattern_score = 0
        
        # 檢測與均線的距離
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        dist_50 = (low - ma50) / ma50
        
        analysis_text = []
        
        # J Law: Tennis Ball Action (20MA 回測)
        if abs(dist_20) <= 0.03: 
            pattern = "🎾 Tennis Ball (20MA)"
            pattern_score = 90
            analysis_text.append(f"股價回測 20MA (支撐價 ${ma20:.2f})，符合網球行為。")
        # J Law: Power Trend (10MA 強勢整理)
        elif abs(dist_10) <= 0.02:
            pattern = "🔥 Power Trend (10MA)"
            pattern_score = 95
            analysis_text.append(f"股價沿著 10MA 強勢整理 (支撐價 ${ma10:.2f})，動能極強。")
        # J Law: Institution Defense (50MA 機構防線)
        elif abs(dist_50) <= 0.03:
            pattern = "🛡️ Institutional Line (50MA)"
            pattern_score = 80
            analysis_text.append(f"股價回測 50MA 機構成本區 (支撐價 ${ma50:.2f})。")
        else:
            return None # 沒型態，不顯示
            
        # 4. 量能確認 (Volume Check)
        if vol_ratio < 1.0:
            analysis_text.append(f"成交量萎縮至均量的 {int(vol_ratio*100)}%，顯示賣壓枯竭 (No Supply)。")
            pattern_score += 5
        elif vol_ratio > 1.5 and close < open_p:
            return None # 爆量長黑，危險
            
        # 5. 生成交易計劃 (Trade Plan)
        # Entry: 突破今日高點 + 緩衝
        entry_price = high + (atr * 0.1)
        # Stop: 跌破今日低點 - 緩衝
        stop_price = low - (atr * 0.1)
        
        # 風險管理微調
        if entry_price <= stop_price: return None
        risk = entry_price - stop_price
        target = entry_price + (risk * 2.5) # 2.5R 獲利目標
        
        return {
            "Symbol": ticker,
            "Pattern": pattern,
            "Score": pattern_score,
            "Close": close,
            "Entry": round(entry_price, 2),
            "Stop": round(stop_price, 2),
            "Target": round(target, 2),
            "Analysis": " ".join(analysis_text),
            "Vol_Ratio": round(vol_ratio, 2)
        }
    except:
        return None

# ==========================================
# 3. 介面邏輯
# ==========================================

# 側邊欄
with st.sidebar:
    st.markdown("## 🦅 COMMAND CENTER")
    st.markdown("設定你的掃描參數")
    
    scan_btn = st.button("🚀 啟動 J Law 戰術掃描", use_container_width=True)
    
    st.markdown("---")
    st.info("💡 **操作指南**：\n1. 點擊掃描按鈕。\n2. 系統自動尋找符合「趨勢+支撐+縮量」的股票。\n3. 右側查看 TradingView 圖表與進場點。")

# 主畫面
st.markdown("# 🦅 J Law <span class='highlight'>Alpha Station</span>", unsafe_allow_html=True)
st.markdown("專業級自動化股票分析系統 | Powered by Python & TradingView")
st.markdown("---")

# 初始化狀態
if 'scan_data' not in st.session_state:
    st.session_state['scan_data'] = None

# 執行掃描
if scan_btn:
    tickers = get_tickers()
    status_box = st.status("正在連線華爾街數據庫...", expanded=True)
    
    data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
    
    results = []
    
    total_tickers = len(tickers)
    for i, t in enumerate(tickers):
        status_box.update(label=f"正在分析 [{i+1}/{total_tickers}]: {t} ...")
        try:
            if total_tickers == 1: df = data
            else:
                if t not in data.columns.levels[0]: continue
                df = data[t].dropna()
            
            res = analyze_stock_logic(t, df)
            if res: results.append(res)
        except: continue
    
    status_box.update(label="分析完成！", state="complete", expanded=False)
    
    if results:
        # 排序：分數高 -> 低
        df_res = pd.DataFrame(results).sort_values('Score', ascending=False)
        st.session_state['scan_data'] = df_res
    else:
        st.warning("⚠️ 目前市場過於波動，未發現符合 J Law 標準的完美 Setup。")

# 顯示結果
if st.session_state['scan_data'] is not None:
    df = st.session_state['scan_data']
    
    # 佈局：左側選單列表，右側詳細戰情室
    col_nav, col_main = st.columns([1, 2.5])
    
    with col_nav:
        st.subheader("📋 訊號列表")
        # 自定義樣式的 Radio 選單
        selected_ticker = st.radio(
            "選擇標的查看詳情：",
            options=df['Symbol'].tolist(),
            format_func=lambda x: f"{x}  |  {df[df['Symbol']==x]['Pattern'].values[0].split(' ')[0]}",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("**列表說明：**")
        st.caption("🔥 = Power Trend (10MA)")
        st.caption("🎾 = Tennis Ball (20MA)")
        st.caption("🛡️ = Defense (50MA)")

    with col_main:
        if selected_ticker:
            row = df[df['Symbol'] == selected_ticker].iloc[0]
            
            # --- 1. 頂部戰術看板 ---
            st.markdown(f"## {row['Symbol']} 戰術分析報告")
            
            # 使用 CSS 卡片顯示分析文字
            st.markdown(f"""
            <div class="stock-card" style="border-left: 5px solid #00E676;">
                <h4 style="margin:0; color:#00E676;">🤖 J Law AI 分析：</h4>
                <p style="font-size:16px; margin-top:5px;">{row['Analysis']}</p>
                <p style="font-size:14px; color:#aaa; margin-bottom:0;">策略評分：<b>{row['Score']} / 100</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- 2. 交易計劃數據網格 ---
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="stat-box blue"><div class="stat-label">現價 PRICE</div><div class="stat-value">${row["Close"]:.2f}</div></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat-box green"><div class="stat-label">買入 ENTRY</div><div class="stat-value">${row["Entry"]}</div></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat-box red"><div class="stat-label">止蝕 STOP</div><div class="stat-value">${row["Stop"]}</div></div>', unsafe_allow_html=True)
            with c4:
                st.markdown(f'<div class="stat-box green"><div class="stat-label">目標 TARGET</div><div class="stat-value">${row["Target"]}</div></div>', unsafe_allow_html=True)
            
            st.write("") # Spacer

            # --- 3. TradingView 自動整合 ---
            st.markdown("### 📈 即時圖表驗證")
            
            # 這是 TradingView 高階圖表 Widget
            tv_html = f"""
            <div class="tradingview-widget-container" style="height:500px;width:100%">
              <div id="tradingview_{row['Symbol']}" style="height:calc(100% - 32px);width:100%"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
                "autosize": true,
                "symbol": "{row['Symbol']}",
                "interval": "D",
                "timezone": "Exchange",
                "theme": "dark",
                "style": "1",
                "locale": "zh_TW",
                "enable_publishing": false,
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_{row['Symbol']}",
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
              }}
              );
              </script>
            </div>
            """
            components.html(tv_html, height=510)
            
            # --- 4. 底部提醒 ---
            st.info(f"💡 **交易執行**：請在券商設定 **Stop Limit Order (觸價單)** 於 ${row['Entry']}。若股價未觸發直接下跌，則取消計畫。")

else:
    # 初始歡迎畫面
    st.markdown("""
    <div style="text-align:center; padding: 50px; opacity: 0.7;">
        <h1>等待指令...</h1>
        <p>請點擊左側 <b>[ 🚀 啟動 J Law 戰術掃描 ]</b> 開始尋找獲利機會。</p>
    </div>
    """, unsafe_allow_html=True)
