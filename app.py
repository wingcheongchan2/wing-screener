import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime
import time

# ==========================================
# 0. 系統核心配置 (J Law Institutional)
# ==========================================
st.set_page_config(page_title="J Law: Institutional Scanner", layout="wide", page_icon="🏦")

# 檔案路徑
PORTFOLIO_FILE = 'quant_portfolio.csv'
TRADE_LOG_FILE = 'quant_tradelog.csv'

# ==========================================
# 1. 華爾街黑金風格 CSS
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
        
        .stApp { background-color: #000000; color: #E0E0E0; font-family: 'Inter', sans-serif; }
        div[data-testid="stDataFrame"] { border: 1px solid #333; }
        section[data-testid="stSidebar"] { background-color: #0F0F0F; border-right: 1px solid #222; }
        
        /* 專業指標卡片 */
        .metric-card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 4px; }
        .metric-title { font-size: 11px; color: #888; text-transform: uppercase; font-family: 'Roboto Mono'; }
        .metric-value { font-size: 20px; font-weight: bold; color: #fff; font-family: 'Roboto Mono'; margin-top: 5px; }
        .metric-sub { font-size: 11px; margin-top: 5px; }
        
        /* 狀態標籤 */
        .status-badge { padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .bull { background: #064E3B; color: #34D399; border: 1px solid #059669; }
        .bear { background: #450a0a; color: #FCA5A5; border: 1px solid #B91C1C; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據庫與交易系統
# ==========================================
def init_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target', 'Status']).to_csv(PORTFOLIO_FILE, index=False)

def execute_order(symbol, entry, stop, target, capital_allocation):
    init_db()
    df = pd.read_csv(PORTFOLIO_FILE)
    if not df.empty and symbol in df[df['Status']=='OPEN']['Symbol'].values:
        return False, "⚠️ 錯誤：倉位已存在"
    
    qty = int(capital_allocation / entry)
    if qty < 1: return False, "⚠️ 資金不足以購買 1 股"
    
    new_trade = {
        'Date': datetime.date.today(), 'Symbol': symbol,
        'Entry': float(entry), 'Qty': int(qty),
        'Stop': float(stop), 'Target': float(target), 'Status': 'OPEN'
    }
    pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
    return True, f"✅ 買單成交: {symbol} | {qty}股 @ ${entry:.2f}"

# ==========================================
# 3. 數據源與穩健下載 (Robust Fetch)
# ==========================================
@st.cache_data
def get_full_universe():
    # S&P 500 + Nasdaq 100 重點股 (去除重複)
    top_stocks = [
        "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "COST", "NFLX",
        "AMD", "PEP", "LIN", "CSCO", "TMUS", "INTU", "QCOM", "TXN", "CMCSA", "AMGN",
        "HON", "INTC", "ISRG", "BKNG", "AMAT", "SBUX", "VRTX", "GILD", "MDLZ", "ADP",
        "LRCX", "REGN", "ADI", "PANW", "MU", "KLAC", "SNPS", "PDD", "CDNS", "MELI",
        "MNST", "CSX", "MAR", "PYPL", "ORLY", "CTAS", "ROP", "ASML", "NXPI", "LULU",
        "FTNT", "ADSK", "PCAR", "DXCM", "PAYX", "MCHP", "KDP", "CHTR", "MRVL", "IDXX",
        "ABNB", "AEP", "SGEN", "ODFL", "AZN", "CPRT", "ROST", "BKR", "EA", "FAST",
        "EXC", "XEL", "VRSK", "CSGP", "CTSH", "GEHC", "BIIB", "WBD", "GFS", "DLTR",
        "ON", "CDW", "ANSS", "TTD", "CEG", "ALGN", "WBA", "ILMN", "ZM", "LCID",
        "PLTR", "COIN", "MSTR", "SMCI", "ARM", "APP", "HOOD", "AFRM", "UPST", "JPM", 
        "V", "LLY", "WMT", "XOM", "UNH", "MA", "HD", "PG", "JNJ", "ABBV", "MRK", "CVX", 
        "CRM", "BAC", "KO", "TMO", "ACN", "MCD", "DIS", "ABT", "VZ", "IBM", "PFE", "UBER", 
        "CAT", "SPGI", "GE", "PM", "UNP", "GS", "LOW", "COP", "RTX", "T", "AXP", "NEE", 
        "ELV", "ETN", "BLK", "SYK", "PGR", "TJX", "MS", "C", "BA", "MMC", "CB", "GILD", 
        "AMT", "LMT", "CI", "CVS", "SCHW", "SNOW", "SQ", "DKNG", "RIVN", "CELH", "ELF", "ONON", "MARA", "CLSK", "RIOT"
    ]
    return sorted(list(set(top_stocks)))

# 這裡不緩存，避免下載失敗後卡死
def fetch_data_robust(tickers):
    data_map = {}
    
    # 分批下載，每批 50 隻，防止 Yahoo 封鎖
    chunk_size = 50
    chunks = [tickers[i:i + chunk_size] for i in range(0, len(tickers), chunk_size)]
    
    # 下載 Benchmark (SPY, QQQ)
    try:
        bench = yf.download(['SPY', 'QQQ'], period="1y", group_by='ticker', threads=True, progress=False)
        if bench.empty: return None, None, None
    except: return None, None, None

    # 合併數據
    all_data = pd.DataFrame()
    for chunk in chunks:
        try:
            temp = yf.download(chunk, period="1y", group_by='ticker', threads=True, progress=False)
            if not temp.empty:
                if all_data.empty: all_data = temp
                else: all_data = pd.concat([all_data, temp], axis=1)
        except: pass
    
    return all_data, bench['SPY'], bench['QQQ']

# ==========================================
# 4. J Law 專業分析核心
# ==========================================
def analyze_stock_safe(ticker, df_stock, df_spy, df_qqq):
    try:
        # 數據檢查
        if df_stock is None or len(df_stock) < 200: return None
        if 'Close' not in df_stock.columns: return None # 防止空數據
        
        close = df_stock['Close']
        if close.isnull().all(): return None # 防止全 NaN
        
        high = df_stock['High']
        low = df_stock['Low']
        vol = df_stock['Volume']
        curr = float(close.iloc[-1])
        
        # --- 1. J Law RS Rating ---
        def get_perf(s, window): 
            try: return (s.iloc[-1]/s.iloc[-window]) - 1
            except: return 0
        
        stock_score = get_perf(close, 63)*0.4 + get_perf(close, 126)*0.2 + get_perf(close, 252)*0.4
        spy_score = get_perf(df_spy['Close'], 63)*0.4 + get_perf(df_spy['Close'], 126)*0.2 + get_perf(df_spy['Close'], 252)*0.4
        
        rs_rating = 50 + (stock_score - spy_score) * 100 
        rs_rating = min(99, max(1, int(rs_rating)))
        
        # --- 2. Stage Analysis ---
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        stage = "弱勢 (Stage 4)"
        if curr > ma200: stage = "蓄勢 (Stage 1)"
        if curr > ma50 and ma50 > ma200: stage = "強勢 (Stage 2)"
        
        # --- 3. DRSI (Stoch RSI) ---
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        d = k.rolling(3).mean()
        k_val, d_val = float(k.iloc[-1]), float(d.iloc[-1])
        
        # --- 4. RVOL ---
        vol_avg = float(vol.rolling(50).mean().iloc[-1])
        rvol = float(vol.iloc[-1]) / vol_avg if vol_avg > 0 else 0
        
        # --- 5. 評分 ---
        score = 0
        if "Stage 2" in stage: score += 30
        if rs_rating > 70: score += 20
        if k_val > d_val: score += 20 # 金叉
        if rvol > 1.0: score += 10
        if curr > ma50: score += 20
        
        # --- 6. 交易點位 ---
        atr = float((high - low).rolling(14).mean().iloc[-1])
        entry = curr
        stop = curr - (2 * atr)
        target = entry + (3 * (entry - stop))
        
        return {
            "Symbol": ticker,
            "Price": curr,
            "Change%": ((curr - float(close.iloc[-2]))/float(close.iloc[-2]))*100,
            "Score": score,
            "RS_Rating": rs_rating,
            "Stage": stage,
            "DRSI_Signal": "金叉 (Bull)" if k_val > d_val else "中性",
            "RVOL": round(rvol, 1),
            "Entry": round(entry, 2),
            "Stop": round(stop, 2),
            "Target": round(target, 2),
            "R_Ratio": round((target-entry)/(entry-stop), 1) if (entry-stop)!=0 else 0
        }
    except Exception as e:
        return None

# ==========================================
# 5. 主程式介面
# ==========================================
inject_css()
init_db()

with st.sidebar:
    st.markdown("## 🏦 J LAW INSTITUTIONAL")
    st.caption("Stable Version (v2.1)")
    page = st.radio("導航", ["⚡ 市場掃描儀", "💼 投資組合"])
    st.divider()
    capital_input = st.number_input("單筆交易資金 ($)", value=10000, step=1000)

if page == "⚡ 市場掃描儀":
    st.title("⚡ 全市場深度掃描 (Stable)")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        run_scan = st.button("🚀 啟動安全掃描", use_container_width=True)
    
    if run_scan:
        st.session_state['scan_data'] = pd.DataFrame() # 清空舊數據
        progress_text = st.empty()
        bar = st.progress(0)
        
        tickers = get_full_universe()
        progress_text.text(f"正在連接交易所，下載 {len(tickers)} 隻股票數據 (分批下載中)...")
        
        # 執行穩健下載
        all_stock_data, spy_data, qqq_data = fetch_data_robust(tickers)
        
        if all_stock_data is None or all_stock_data.empty:
            progress_text.error("無法連接數據源 (Yahoo API Timeout)。請稍後再試。")
            bar.empty()
        else:
            results = []
            progress_text.text("正在執行 J Law 量化運算...")
            
            total_tickers = len(tickers)
            for i, t in enumerate(tickers):
                try:
                    # 處理 MultiIndex 列名
                    if isinstance(all_stock_data.columns, pd.MultiIndex):
                        if t in all_stock_data.columns.levels[0]:
                            df_t = all_stock_data[t].dropna()
                            res = analyze_stock_safe(t, df_t, spy_data, qqq_data)
                            if res: results.append(res)
                except: pass
                
                if i % 5 == 0: bar.progress((i+1)/total_tickers)
            
            bar.empty()
            
            # --- 關鍵修復：處理空結果 ---
            if not results:
                progress_text.warning("掃描完成，但沒有股票符合數據標準 (或市場數據異常)。")
                # 建立空 DataFrame 但帶有正確欄位，防止 KeyError
                cols = ['Symbol', 'Price', 'Change%', 'Score', 'RS_Rating', 'Stage', 'DRSI_Signal', 'RVOL', 'Entry', 'Stop', 'Target', 'R_Ratio', 'Setup']
                st.session_state['scan_data'] = pd.DataFrame(columns=cols)
            else:
                progress_text.success(f"分析完成！共處理 {len(results)} 隻標的。")
                st.session_state['scan_data'] = pd.DataFrame(results)

    # 結果展示邏輯 (加上防呆)
    if 'scan_data' in st.session_state:
        df = st.session_state['scan_data']
        
        if df.empty:
            st.info("暫無數據。請點擊上方按鈕開始掃描。")
        else:
            # 1. 篩選器
            c_filter1, c_filter2 = st.columns(2)
            with c_filter1:
                min_score = st.slider("最低技術評分 (Score)", 0, 100, 50) # 降低預設值，確保有結果
            with c_filter2:
                min_rs = st.slider("最低 RS 強度 (RS Rating)", 0, 99, 50)
                
            # 安全篩選
            try:
                filtered_df = df[(df['Score'] >= min_score) & (df['RS_Rating'] >= min_rs)].sort_values('Score', ascending=False)
            except KeyError:
                st.error("數據格式錯誤，請重新掃描。")
                st.stop()
            
            st.markdown(f"### 📋 篩選結果 ({len(filtered_df)} 隻)")
            
            # 2. 交互式表格
            st.dataframe(
                filtered_df[['Symbol', 'Price', 'Change%', 'Score', 'RS_Rating', 'Stage', 'DRSI_Signal', 'RVOL']],
                use_container_width=True,
                column_config={
                    "Score": st.column_config.ProgressColumn("Tech Score", min_value=0, max_value=100, format="%d"),
                    "RS_Rating": st.column_config.NumberColumn("RS Strength", help="Relative Strength (0-99)"),
                    "Change%": st.column_config.NumberColumn("Change%", format="%.2f%%"),
                },
                height=300
            )
            
            # 3. 深度分析面板
            if not filtered_df.empty:
                st.markdown("---")
                st.markdown("### 🔍 交易面板")
                selected_ticker = st.selectbox("選擇要交易的股票:", filtered_df['Symbol'].tolist())
                
                if selected_ticker:
                    row = filtered_df[filtered_df['Symbol'] == selected_ticker].iloc[0]
                    
                    # 頂部資訊
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#111; padding:20px; border:1px solid #333;">
                        <div>
                            <h1 style="margin:0; color:#fff;">{row['Symbol']} <span style="font-size:18px; color:{'#34D399' if row['Change%']>0 else '#FCA5A5'}">({row['Change%']:.2f}%)</span></h1>
                            <span style="color:#888;">{row['Stage']} | RS Rating: <b style="color:#fff">{row['RS_Rating']}</b></span>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-size:12px; color:#888;">J LAW SCORE</div>
                            <div style="font-size:42px; font-weight:bold; color:{'#34D399' if row['Score']>80 else '#FBBF24'}">{row['Score']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 交易執行區
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<div class='metric-card'><div class='metric-title'>DRSI SIGNAL</div><div class='metric-value' style='color:{'#34D399' if 'Bull' in row['DRSI_Signal'] else '#fff'}'>{row['DRSI_Signal']}</div></div>", unsafe_allow_html=True)
                    c2.markdown(f"<div class='metric-card'><div class='metric-title'>R:R RATIO</div><div class='metric-value'>1 : {row['R_Ratio']}</div></div>", unsafe_allow_html=True)
                    c3.markdown(f"<div class='metric-card'><div class='metric-title'>RVOL</div><div class='metric-value'>{row['RVOL']}x</div></div>", unsafe_allow_html=True)
                    
                    st.markdown("#### ⚡ 交易執行 (Execution)")
                    ec1, ec2, ec3 = st.columns(3)
                    ec1.info(f"🟢 **Entry:** ${row['Entry']}")
                    ec2.error(f"🔴 **Stop:** ${row['Stop']}")
                    ec3.success(f"🎯 **Target:** ${row['Target']}")
                    
                    if st.button(f"立即下單買入 {row['Symbol']} (${capital_input})", use_container_width=True):
                        success, msg = execute_order(row['Symbol'], row['Entry'], row['Stop'], row['Target'], capital_input)
                        if success: st.success(msg)
                        else: st.error(msg)
                    
                    # 圖表
                    st.markdown("#### 📈 技術圖表")
                    components.html(f"""
                    <div class="tradingview-widget-container" style="height:500px;width:100%">
                      <div id="tv_{row['Symbol']}" style="height:100%"></div>
                      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                      <script type="text/javascript">
                      new TradingView.widget({{
                        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
                        "toolbar_bg": "#000", "enable_publishing": false, 
                        "studies": ["StochasticRSI@tv-basicstudies", "MASimple@tv-basicstudies"],
                        "container_id": "tv_{row['Symbol']}"
                      }});
                      </script>
                    </div>
                    """, height=500)

elif page == "💼 投資組合":
    st.title("💼 模擬資產管理")
    
    if os.path.exists(PORTFOLIO_FILE):
        df = pd.read_csv(PORTFOLIO_FILE)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("目前沒有持倉。")
    else:
        st.info("數據庫初始化中...")
