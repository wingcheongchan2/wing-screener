import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime
import time

# ==========================================
# 0. 系統核心配置 (Auto-Pilot)
# ==========================================
st.set_page_config(page_title="J Law Alpha Hunter", layout="wide", page_icon="🦅")

# 檔案路徑
PORTFOLIO_FILE = 'auto_portfolio.csv'

# ==========================================
# 1. 視覺風格 (Elite Theme)
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;700&family=Inter:wght@400;700&display=swap');
        
        .stApp { background-color: #000; color: #fff; font-family: 'Inter', sans-serif; }
        section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
        
        /* 冠軍卡片 */
        .crown-card {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            border: 2px solid #D4AF37; /* 金色邊框 */
            padding: 20px; border-radius: 10px; text-align: center;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
            margin-bottom: 20px;
        }
        .crown-title { color: #D4AF37; font-size: 14px; letter-spacing: 2px; font-weight: bold; text-transform: uppercase; }
        .crown-symbol { font-size: 48px; font-weight: bold; font-family: 'Oswald'; color: #fff; margin: 10px 0; }
        .crown-score { background: #D4AF37; color: #000; padding: 2px 10px; border-radius: 4px; font-weight: bold; }
        
        /* 推薦等級標籤 */
        .rank-diamond { background: #06b6d4; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid #22d3ee; }
        .rank-gold { background: #eab308; color: #000; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .rank-silver { background: #4b5563; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        
        /* 交易建議框 */
        .action-box {
            background: #111; border-left: 5px solid #00E676; padding: 15px; margin-top: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 交易執行 (自動計算倉位)
# ==========================================
def init_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target']).to_csv(PORTFOLIO_FILE, index=False)

def execute_trade(symbol, entry, stop, target, capital):
    init_db()
    df = pd.read_csv(PORTFOLIO_FILE)
    if symbol in df['Symbol'].values: return False, "⚠️ 已經持有此股票"
    
    qty = int(capital / entry)
    new_trade = {
        'Date': datetime.date.today(), 'Symbol': symbol,
        'Entry': entry, 'Qty': qty, 'Stop': stop, 'Target': target
    }
    pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
    return True, f"✅ 自動買入 {symbol}: {qty}股"

# ==========================================
# 3. 數據源：鎖定最強流動性 (Top 150)
# ==========================================
@st.cache_data
def get_market_leaders():
    # 這是 S&P 500 + Nasdaq 100 中流動性最好、波動最大的 120 隻股票
    # 這是為了保證 "交易價值" (有波動才有錢賺)
    return [
        "NVDA", "TSLA", "MSTR", "COIN", "PLTR", "SMCI", "AMD", "AAPL", "MSFT", "AMZN", 
        "GOOGL", "META", "AVGO", "CRWD", "UBER", "ABNB", "DKNG", "MARA", "CLSK", "RIOT", 
        "SOFI", "AI", "ARM", "MU", "QCOM", "TSM", "HOOD", "NET", "PANW", "SNOW", "ONON", 
        "ELF", "CELH", "APP", "CVNA", "UPST", "JPM", "V", "LLY", "NFLX", "COST", "PEP",
        "ADBE", "INTU", "TXN", "AMGN", "ISRG", "BKNG", "LRCX", "REGN", "ADI", "KLAC",
        "SNPS", "CDNS", "MELI", "MNST", "ORLY", "ASML", "LULU", "FTNT", "PCAR", "DXCM",
        "MRVL", "IDXX", "ODFL", "AZN", "ROST", "EA", "FAST", "EXC", "XEL", "VRSK", "CSGP",
        "GEHC", "GFS", "ON", "TTD", "CEG", "ZM", "ENPH", "JD", "TEAM", "ZS", "DDOG", "SQ",
        "RIVN", "LCID", "AFRM", "GILD", "CVS", "MRK", "ABBV", "JNJ", "PG", "HD", "MA", "UNH",
        "XOM", "CVX", "BAC", "WMT", "KO", "MCD", "DIS", "CAT", "GE", "GS", "BA", "RTX"
    ]

def fetch_data_auto(tickers):
    # 分批下載，確保穩定
    data_frames = []
    chunk_size = 50
    chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    
    # 基準
    try:
        bench = yf.download(['SPY', 'QQQ'], period="1y", group_by='ticker', threads=True, progress=False)
    except: return None, None, None

    for chunk in chunks:
        try:
            d = yf.download(chunk, period="1y", group_by='ticker', threads=True, progress=False)
            if not d.empty: data_frames.append(d)
        except: pass
    
    if not data_frames: return None, None, None
    return pd.concat(data_frames, axis=1), bench['SPY'], bench['QQQ']

# ==========================================
# 4. J Law Alpha 算法 (自動評級系統)
# ==========================================
def analyze_opportunity(ticker, df_stock, df_spy, df_qqq):
    try:
        if len(df_stock) < 200: return None
        
        close = df_stock['Close']
        curr = float(close.iloc[-1])
        vol = df_stock['Volume']
        
        # --- 1. 計算 RS (相對強度) ---
        # 自動選擇基準：如果是科技股跟 QQQ 比，其他跟 SPY 比 (這裡簡化為取兩者較高者)
        def get_perf(s): return (s.iloc[-1]/s.iloc[-63]) - 1
        stock_perf = get_perf(close)
        spy_perf = get_perf(df_spy['Close'])
        qqq_perf = get_perf(df_qqq['Close'])
        
        benchmark = max(spy_perf, qqq_perf)
        rs_rating = 50 + (stock_perf - benchmark) * 100
        rs_rating = min(99, max(1, int(rs_rating)))
        
        # --- 2. 計算 DRSI (Stoch RSI) ---
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        d = k.rolling(3).mean()
        k_val, d_val = float(k.iloc[-1]), float(d.iloc[-1])
        
        # --- 3. 自動分級算法 (Auto-Ranking) ---
        score = 0
        reasons = []
        rank_tier = "Silver" # 預設
        
        # 條件 A: RS 必須強
        if rs_rating > 80: 
            score += 30
            reasons.append("RS 強度 > 80 (領頭羊)")
        elif rs_rating > 60:
            score += 15
        
        # 條件 B: DRSI 金叉 (進場訊號)
        if k_val > d_val: 
            score += 30
            reasons.append("DRSI 黃金交叉 (買點)")
        elif k_val < 20: # 超賣
            score += 10
            reasons.append("DRSI 超賣 (準備反彈)")
            
        # 條件 C: 趨勢 (Stage 2)
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        if curr > ma50 and ma50 > ma200: 
            score += 20
            reasons.append("Stage 2 強力多頭")
            
        # 條件 D: 量能
        vol_avg = float(vol.rolling(50).mean().iloc[-1])
        rvol = float(vol.iloc[-1]) / vol_avg
        if rvol > 1.2: 
            score += 20
            reasons.append(f"爆量 ({rvol:.1f}x)")
            
        # 最終定級
        if score >= 80: rank_tier = "Diamond" # 鑽石級 (Alpha)
        elif score >= 60: rank_tier = "Gold"    # 黃金級
        
        # 計算交易點位
        atr = float((df_stock['High'] - df_stock['Low']).rolling(14).mean().iloc[-1])
        entry = curr
        stop = curr - (2 * atr)
        target = entry + (3 * (entry - stop))
        
        return {
            "Symbol": ticker,
            "Score": score,
            "Rank": rank_tier,
            "RS": rs_rating,
            "Price": curr,
            "Change": ((curr - float(close.iloc[-2]))/float(close.iloc[-2]))*100,
            "Entry": entry, "Stop": stop, "Target": target,
            "Reason": " + ".join(reasons)
        }
    except: return None

# ==========================================
# 5. 主介面 (Auto-Pilot)
# ==========================================
inject_css()
init_db()

with st.sidebar:
    st.markdown("## 🦅 J LAW ALPHA HUNTER")
    st.caption("Auto-Pilot Mode")
    capital = st.number_input("每筆交易本金 ($)", value=10000)

st.title("🦅 全自動機會搜尋器 (Auto-Pilot)")
st.markdown("系統將自動掃描市場，並按 **「交易價值 (Opportunity Value)」** 排序。你不需要設置任何參數。")

start = st.button("🚀 啟動 AI 獵人 (Start Hunter)", use_container_width=True)

if start:
    status = st.empty()
    bar = st.progress(0)
    
    status.info("1. 正在鎖定 120 隻市場最熱門股票...")
    tickers = get_market_leaders()
    
    status.info("2. 下載數據並進行 J Law 策略運算...")
    stock_data, spy, qqq = fetch_data_auto(tickers)
    
    results = []
    if stock_data is not None:
        for i, t in enumerate(tickers):
            try:
                df_t = stock_data[t] if isinstance(stock_data.columns, pd.MultiIndex) else stock_data
                res = analyze_opportunity(t, df_t, spy, qqq)
                if res: results.append(res)
            except: pass
            if i % 10 == 0: bar.progress((i+1)/len(tickers))
    
    bar.empty()
    
    if not results:
        status.error("市場數據連接失敗，請重試。")
    else:
        # 自動排序：分數高 -> RS 高 -> 代碼
        df = pd.DataFrame(results).sort_values(['Score', 'RS'], ascending=[False, False])
        st.session_state['auto_results'] = df
        status.success(f"掃描完成！已自動為你找到 {len(df)} 個潛在機會，並按價值排序。")

# 結果展示區 (自動過濾模式)
if 'auto_results' in st.session_state:
    df = st.session_state['auto_results']
    
    # 1. 提取最頂級的股票 (Diamond & Gold)
    top_picks = df[df['Rank'].isin(['Diamond', 'Gold'])]
    if top_picks.empty:
        top_picks = df.head(5) # 如果沒有頂級，就顯示前5名
        st.warning("今日市場較弱，沒有發現「鑽石級」機會。以下是目前評分最高的股票：")
    
    st.markdown("### 🔥 最具交易價值 (Top Picks)")
    
    # 2. 自動展示前 3 名 (卡片式)
    for i in range(min(3, len(top_picks))):
        row = top_picks.iloc[i]
        
        # 決定顏色
        rank_class = "rank-diamond" if row['Rank'] == "Diamond" else "rank-gold"
        rank_color = "#06b6d4" if row['Rank'] == "Diamond" else "#eab308"
        
        # 佈局
        c_card, c_info = st.columns([1, 2])
        
        with c_card:
            # 冠軍卡片設計
            st.markdown(f"""
            <div class="crown-card" style="border-color:{rank_color}">
                <div class="crown-title">RANK #{i+1} OPPORTUNITY</div>
                <div class="crown-symbol">{row['Symbol']}</div>
                <span class="{rank_class}">{row['Rank']} TIER</span>
                <div style="margin-top:10px; font-size:24px; color:{'#00E676' if row['Change']>0 else '#FF1744'}">{row['Change']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with c_info:
            st.markdown(f"#### 📊 分析報告 ({row['Symbol']})")
            st.write(f"**入選理由:** {row['Reason']}")
            st.write(f"**J Law Score:** {row['Score']} | **RS 強度:** {row['RS']}")
            
            # 交易建議框
            st.markdown(f"""
            <div class="action-box">
                <div style="display:flex; justify-content:space-between;">
                    <span>🔵 <b>買入 Entry:</b> ${row['Entry']:.2f}</span>
                    <span>🔴 <b>止損 Stop:</b> ${row['Stop']:.2f}</span>
                    <span>🟢 <b>目標 Target:</b> ${row['Target']:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 一鍵買入
            if st.button(f"⚡ 自動下單 {row['Symbol']} (${capital})", key=f"btn_{row['Symbol']}", use_container_width=True):
                success, msg = execute_trade(row['Symbol'], row['Entry'], row['Stop'], row['Target'], capital)
                if success: st.success(msg)
                else: st.warning(msg)
        
        st.divider()

    # 3. 查看全部列表
    with st.expander("📋 查看完整排行榜 (All Opportunities)"):
        st.dataframe(
            df[['Symbol', 'Rank', 'Score', 'RS', 'Price', 'Change', 'Reason']],
            use_container_width=True,
            column_config={
                "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
            }
        )

# 投資組合區
st.markdown("---")
st.markdown("### 💼 我的持倉")
if os.path.exists(PORTFOLIO_FILE):
    port = pd.read_csv(PORTFOLIO_FILE)
    if not port.empty:
        st.dataframe(port, use_container_width=True)
    else:
        st.info("暫無持倉。請點擊上方「自動下單」按鈕建立倉位。")
