import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime

# ==========================================
# 1. 介面與 CSS (保持專業暗黑風)
# ==========================================
st.set_page_config(page_title="J Law Pro Radar", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    
    /* 表格樣式優化 */
    div[data-testid="stDataFrame"] {
        border: 1px solid #333;
        border-radius: 5px;
    }
    
    /* 評分標籤 */
    .rank-gold { color: #FFD700; font-weight: bold; padding: 2px 6px; border: 1px solid #FFD700; border-radius: 4px; }
    .rank-silver { color: #C0C0C0; font-weight: bold; padding: 2px 6px; border: 1px solid #C0C0C0; border-radius: 4px; }
    .rank-watch { color: #00D084; font-weight: bold; padding: 2px 6px; border: 1px solid #00D084; border-radius: 4px; }
    
    /* 頂部數據卡 */
    .stat-card { background-color: #1F2937; padding: 15px; border-radius: 8px; border-top: 4px solid #3B82F6; text-align: center; }
    .stat-val { font-size: 20px; font-weight: bold; color: white; }
    .stat-lbl { font-size: 12px; color: #9CA3AF; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 J Law 戰術雷達：全天候作戰版")

# ==========================================
# 2. 擴大股票池 (確保有魚可釣)
# ==========================================
@st.cache_data
def get_expanded_tickers():
    # 這裡包含了科技巨頭、半導體、軟體、金融、消費強勢股，共約 80+ 檔
    tickers = [
        "NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "TSLA", "AMD", "AVGO", "COST", 
        "NFLX", "SMCI", "ARM", "PLTR", "COIN", "MSTR", "HOOD", "CRWD", "PANW", "SNPS", 
        "CDNS", "ADBE", "CRM", "INTU", "NOW", "UBER", "ABNB", "DASH", "SPOT", "SHOP",
        "QCOM", "TXN", "ADI", "MRVL", "LRCX", "KLAC", "AMAT", "MU", "INTC", "TSM",
        "JPM", "V", "MA", "GS", "MS", "BLK", "BAC", "WFC", "C", "AXP",
        "LLY", "NVO", "UNH", "JNJ", "ABBV", "MRK", "PFE", "AMGN", "ISRG", "SYK",
        "WMT", "HD", "PG", "KO", "PEP", "MCD", "SBUX", "NKE", "LULU", "CMG",
        "CAT", "DE", "GE", "HON", "UNP", "UPS", "RTX", "LMT", "BA", "MMM"
    ]
    return list(set(tickers)) # 去重

# ==========================================
# 3. 寬鬆但精準的邏輯 (分級篩選)
# ==========================================
def analyze_market_breadth(df_results):
    if df_results is None or df_results.empty:
        return "無數據", 0
    bulls = len(df_results[df_results['Trend'] == 'Bull'])
    bears = len(df_results) - bulls
    ratio = (bulls / len(df_results)) * 100 if len(df_results) > 0 else 0
    
    status = "🔴 空頭主導"
    if ratio > 60: status = "🟢 多頭主導"
    elif ratio > 40: status = "🟡 震盪盤整"
    
    return status, round(ratio)

def analyze_stock_tiered(ticker, df):
    try:
        if len(df) < 200: return None
        
        curr = df.iloc[-1]
        close = curr['Close']
        vol = curr['Volume']
        
        # 均線
        ma10 = df['Close'].rolling(10).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        ma50 = df['Close'].rolling(50).mean().iloc[-1]
        ma200 = df['Close'].rolling(200).mean().iloc[-1]
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1.0
        
        # 1. 大趨勢判斷 (Trend Filter)
        trend = "Bull" if close > ma200 else "Bear"
        
        # 如果是空頭趨勢，直接標記並返回（可以在列表中過濾掉）
        if trend == "Bear":
            return {
                "Symbol": ticker, "Rank": "❌", "Score": 0, "Price": close, 
                "Support": "Under 200MA", "Vol": round(vol_ratio, 1), "Trend": "Bear",
                "Dist_20MA": 999
            }

        # 2. 距離計算 (Distance from Support)
        dist_20 = (close - ma20) / ma20
        dist_50 = (close - ma50) / ma50
        
        rank = ""
        score = 0
        support_loc = ""
        action = ""
        
        # 邏輯 A: 黃金機會 (Golden Setup) - 完美回測且縮量
        # 條件：距離 20MA 或 50MA 在 3% 以內，且縮量 (<1.2x)
        if (abs(dist_20) < 0.03 or abs(dist_50) < 0.03) and vol_ratio < 1.2:
            rank = "⭐⭐⭐ Gold"
            score = 95
            support_loc = "20MA" if abs(dist_20) < abs(dist_50) else "50MA"
            action = "準備進場 (Buy Stop)"
            
        # 邏輯 B: 白銀機會 (Silver Setup) - 位置對了，但量能沒縮
        elif (abs(dist_20) < 0.04 or abs(dist_50) < 0.04):
            rank = "⭐⭐ Silver"
            score = 80
            support_loc = "Near Support"
            action = "觀察 K 線確認"
            
        # 邏輯 C: 觀察名單 (Watchlist) - 稍微有點遠，但趨勢很強
        elif 0 < dist_20 < 0.08: # 在 20MA 上方 8% 以內 (沒有噴太遠)
            rank = "👀 Watch"
            score = 60
            support_loc = "Trend OK"
            action = "等待回調"
            
        else:
            rank = "💨 Extended" # 噴太遠了，別追
            score = 40
            support_loc = "Far from MA"
            action = "勿追高"

        return {
            "Symbol": ticker,
            "Rank": rank,
            "Score": score,
            "Price": round(close, 2),
            "Support": support_loc,
            "Vol": f"{round(vol_ratio, 1)}x",
            "Action": action,
            "MA20": round(ma20, 2),
            "Trend": trend,
            "Dist_20MA": round(dist_20 * 100, 1)
        }
    except:
        return None

# ==========================================
# 4. 主程序
# ==========================================

# 側邊欄控制
with st.sidebar:
    st.header("⚙️ 掃描控制台")
    force_scan = st.button("🚀 開始深度掃描", type="primary")
    st.info("系統會掃描 80+ 檔熱門美股，並根據距離均線的位置進行分級。")
    
    show_bear = st.checkbox("顯示空頭趨勢股票 (Under 200MA)", value=False)
    show_extended = st.checkbox("顯示已噴飛股票 (Extended)", value=False)

# 初始化 Session State
if 'market_data' not in st.session_state:
    st.session_state['market_data'] = None

if force_scan:
    tickers = get_expanded_tickers()
    progress_text = st.empty()
    bar = st.progress(0)
    
    progress_text.text("正在下載市場數據...")
    # 批量下載
    data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
    
    results = []
    
    for i, t in enumerate(tickers):
        bar.progress((i+1) / len(tickers))
        try:
            if len(tickers) == 1: df = data
            else: 
                if t not in data.columns.levels[0]: continue
                df = data[t].dropna()
                
            res = analyze_stock_tiered(t, df)
            if res: results.append(res)
        except: continue
        
    bar.empty()
    progress_text.empty()
    
    if results:
        st.session_state['market_data'] = pd.DataFrame(results)
    else:
        st.error("數據獲取失敗，請稍後再試。")

# ==========================================
# 5. 結果顯示區 (儀表板)
# ==========================================

if st.session_state['market_data'] is not None:
    df = st.session_state['market_data']
    
    # 1. 市場廣度分析
    status, bull_ratio = analyze_market_breadth(df)
    
    # 頂部數據
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-lbl">市場狀態</div><div class="stat-val">{status}</div></div>', unsafe_allow_html=True)
    with c2:
        gold_count = len(df[df['Rank'].str.contains("Gold")])
        st.markdown(f'<div class="stat-card"><div class="stat-lbl">黃金機會 (Gold)</div><div class="stat-val" style="color:#FFD700">{gold_count} 檔</div></div>', unsafe_allow_html=True)
    with c3:
        silver_count = len(df[df['Rank'].str.contains("Silver")])
        st.markdown(f'<div class="stat-card"><div class="stat-lbl">白銀機會 (Silver)</div><div class="stat-val" style="color:#C0C0C0">{silver_count} 檔</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 2. 篩選過濾
    final_df = df.copy()
    if not show_bear:
        final_df = final_df[final_df['Trend'] == 'Bull']
    if not show_extended:
        final_df = final_df[~final_df['Rank'].str.contains("Extended")]
        
    # 排序：分數高 -> 低
    final_df = final_df.sort_values(by=['Score', 'Vol'], ascending=[False, True])
    
    # 3. 互動式佈局
    col_table, col_chart = st.columns([4, 6])
    
    with col_table:
        st.subheader("📋 戰術清單 (點擊代號查看)")
        
        # 製作顯示用表格 (美化)
        display_cols = ['Symbol', 'Rank', 'Price', 'Support', 'Vol', 'Action']
        
        # 使用 Streamlit 的選單功能來當作觸發器
        selected_ticker_with_rank = st.radio(
            "選擇股票進行分析：",
            options=final_df.apply(lambda x: f"{x['Symbol']} | {x['Rank']} | ${x['Price']}", axis=1).tolist(),
            label_visibility="collapsed"
        )
        
        # 顯示完整表格供參考
        st.dataframe(
            final_df[display_cols].style.applymap(
                lambda x: 'color: #FFD700' if 'Gold' in str(x) else ('color: #C0C0C0' if 'Silver' in str(x) else ''), 
                subset=['Rank']
            ),
            use_container_width=True,
            height=400
        )

    with col_chart:
        if selected_ticker_with_rank:
            sel_symbol = selected_ticker_with_rank.split(" | ")[0]
            sel_row = final_df[final_df['Symbol'] == sel_symbol].iloc[0]
            
            st.markdown(f"## 🔭 {sel_symbol} 深度分析")
            
            # 策略建議卡
            rank_color = "#FFD700" if "Gold" in sel_row['Rank'] else "#FFFFFF"
            st.markdown(f"""
            <div style="background-color:#262730; padding:15px; border-radius:10px; border-left: 5px solid {rank_color}">
                <h3 style="margin:0; color:{rank_color}">{sel_row['Rank']} Setup</h3>
                <p style="margin:5px 0 0 0; font-size:16px;">
                <b>位置：</b> {sel_row['Support']} <br>
                <b>量能：</b> {sel_row['Vol']} (縮量最佳) <br>
                <b>建議行動：</b> {sel_row['Action']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            
            # TradingView 圖表
            tv_code = f"""
            <div class="tradingview-widget-container">
              <div id="tv_chart_{sel_symbol}"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
                "width": "100%", "height": 500, "symbol": "{sel_symbol}",
                "interval": "D", "timezone": "Exchange", "theme": "dark",
                "style": "1", "locale": "zh_TW", "toolbar_bg": "#f1f3f6",
                "enable_publishing": false, "hide_side_toolbar": false,
                "allow_symbol_change": true, "container_id": "tv_chart_{sel_symbol}",
                "studies": [
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 20 }}, "title": "20 MA" }},
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 50 }}, "title": "50 MA" }},
                  {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 200 }}, "title": "200 MA" }}
                ]
              }}
              );
              </script>
            </div>
            """
            components.html(tv_code, height=510)
            
            # 簡單的風控計算
            with st.expander("💰 計算這筆交易該買幾股？"):
                account = st.number_input("帳戶總金額", value=10000, step=1000)
                risk_p = st.number_input("風險 %", value=1.0, step=0.1)
                
                # 自動抓取 20MA 當作止損參考
                ma20_price = sel_row['MA20']
                stop_loss_input = st.number_input("止損價格 (預設 20MA)", value=ma20_price)
                
                if sel_row['Price'] > stop_loss_input:
                    risk_per_share = sel_row['Price'] - stop_loss_input
                    total_risk = account * (risk_p / 100)
                    shares = int(total_risk / risk_per_share)
                    st.success(f"👉 建議買入： **{shares} 股** (單筆虧損限制在 ${total_risk})")
                else:
                    st.warning("止損價格必須低於現價")

else:
    st.info("👈 請點擊左側「🚀 開始深度掃描」來獲取今日戰術清單。")
