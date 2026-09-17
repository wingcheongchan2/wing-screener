import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime

# ==========================================
# 0. 系統核心配置
# ==========================================
st.set_page_config(
    page_title="J Law Alpha Hunter • Tesla Cyber Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. Tesla 科技美學深色主題 (Tesla Cyber UI)
# ==========================================
def inject_tesla_theme():
    tesla_bg_url = "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=2000&q=80"
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Tesla 全局背景 */
        .stApp {{
            background: linear-gradient(180deg, rgba(8, 11, 16, 0.88) 0%, rgba(11, 14, 20, 0.94) 100%),
                        url('{tesla_bg_url}') no-repeat center center fixed;
            background-size: cover;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        
        /* 側邊欄磨砂黑風格 */
        section[data-testid="stSidebar"] {{
            background: rgba(10, 14, 23, 0.92) !important;
            backdrop-filter: blur(16px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        
        /* 玻璃磨砂卡片 (Tesla Frosted Glass) */
        .cyber-card {{
            background: rgba(18, 24, 38, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: all 0.25s ease;
        }}
        .cyber-card:hover {{
            border-color: rgba(56, 189, 248, 0.5);
            box-shadow: 0 8px 30px rgba(56, 189, 248, 0.15);
        }}
        
        /* 鑽石級與黃金級邊框 */
        .card-diamond {{
            border-left: 5px solid #06B6D4 !important;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
        }}
        .card-gold {{
            border-left: 5px solid #EAB308 !important;
            background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
        }}
        
        /* 徽章標籤 */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
            margin-right: 6px;
            margin-bottom: 4px;
        }}
        .badge-diamond {{ background: rgba(6, 182, 212, 0.25); color: #22D3EE; border: 1px solid #06B6D4; }}
        .badge-gold {{ background: rgba(234, 179, 8, 0.25); color: #FACC15; border: 1px solid #EAB308; }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }}
        .badge-red {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }}
        .badge-cyan {{ background: rgba(14, 165, 233, 0.2); color: #38BDF8; border: 1px solid #0284C7; }}

        /* 三大部分標題光條 */
        .section-header {{
            background: rgba(15, 23, 42, 0.85);
            border-left: 5px solid #E82127;
            padding: 14px 20px;
            border-radius: 8px;
            margin: 28px 0 16px 0;
            backdrop-filter: blur(10px);
        }}
        
        /* 進出場點位數據框 */
        .action-box {{
            background: rgba(10, 15, 26, 0.88);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 8px;
            padding: 18px;
            margin-top: 12px;
            font-family: 'JetBrains Mono', monospace;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 全市場覆蓋股票池 (Coverage Universe)
# ==========================================
DEFAULT_UNIVERSE = [
    # 科技巨頭
    "NVDA", "TSLA", "AAPL", "MSFT", "AMZN", "META", "GOOGL",
    # 算力與半導體
    "AMD", "AVGO", "ARM", "MU", "QCOM", "TSM", "ASML", "LRCX", "KLAC", "SMCI", "MRVL", "TXN",
    # 高動能成長股
    "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", "DDOG", "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI",
    # AI 能源與基礎設施
    "CEG", "VST", "BE", "GE", "CAT",
    # 消費與金融龍頭
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON", "JPM", "GS", "V", "MA", "AXP"
]

# ==========================================
# 3. 數據獲取引擎 (Data Engine)
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def get_all_market_data(tickers):
    needed_symbols = list(set(tickers + ['SPY', 'QQQ']))
    try:
        data = yf.download(needed_symbols, period="1y", interval="1d", progress=False, group_by='ticker', threads=True)
    except Exception:
        return None, None, None

    if data is None or data.empty:
        return None, None, None

    def extract_clean_df(raw_data, sym):
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                if sym in raw_data.columns.levels[0]:
                    df = raw_data[sym].copy()
                elif sym in raw_data.columns.levels:
                    df = raw_data.xs(sym, axis=1, level=1).copy()
                else:
                    return None
            else:
                df = raw_data.copy()
            df = df.dropna(subset=['Close'])
            return df if len(df) >= 120 else None
        except Exception:
            return None

    df_spy = extract_clean_df(data, 'SPY')
    df_qqq = extract_clean_df(data, 'QQQ')
    
    stocks = {}
    for s in tickers:
        df_s = extract_clean_df(data, s)
        if df_s is not None and len(df_s) >= 150:
            stocks[s] = df_s

    return stocks, df_spy, df_qqq

# ==========================================
# 4. J Law 7 大選股系統核心演算法
# ==========================================
def evaluate_jlaw_stock(symbol, df, df_spy):
    try:
        c = df['Close']
        h = df['High']
        l = df['Low']
        v = df['Volume']
        
        curr_price = float(c.iloc[-1])
        prev_price = float(c.iloc[-2])
        change_pct = ((curr_price - prev_price) / prev_price) * 100

        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma150 = float(c.rolling(150).mean().iloc[-1]) if len(c) >= 150 else sma50
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma150
        sma200_20d_ago = float(c.rolling(200).mean().iloc[-20]) if len(c) >= 220 else sma200

        roll_len = min(len(c), 252)
        h52 = float(h.iloc[-roll_len:].max())
        l52 = float(l.iloc[-roll_len:].min())
        dist_h52 = ((curr_price - h52) / h52) * 100
        dist_l52 = ((curr_price - l52) / l52) * 100

        reasons = []
        score = 0

        # 1. Stage 2 趨勢檢核 (滿分 25)
        is_stage2 = False
        if curr_price > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 15
            if sma200 >= sma200_20d_ago:
                score += 5
            if dist_h52 >= -25.0 and dist_l52 >= 25.0:
                score += 5
                is_stage2 = True
                reasons.append("Stage 2 完美多頭趨勢 (均線多頭排列且向上)")
        elif curr_price > sma50:
            score += 8
            if dist_h52 >= -20.0:
                reasons.append("處於 50SMA 上方強勢整理")

        # 2. RS 相對強度 Rating (滿分 25)
        def perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        stock_w_perf = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, min(252, len(c)-1))
        spy_w_perf = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_diff = (stock_w_perf - spy_w_perf) * 100
        rs_rating = int(np.clip(50 + (rs_diff * 1.5), 1, 99))

        if rs_rating >= 80:
            score += 25
            reasons.append(f"強勢領頭羊 (RS Rating {rs_rating}，大幅跑贏大盤)")
        elif rs_rating >= 65:
            score += 18
            reasons.append(f"優於大盤表現 (RS Rating {rs_rating})")
        elif rs_rating >= 50:
            score += 10

        # 3. VCP 波動收窄與緊密收市 (滿分 15)
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 10
            reasons.append("VCP 波動收窄 (近期波幅顯著收斂蓄勢)")
        if float(c.iloc[-5:].std() / curr_price) < 0.025:
            score += 5
            reasons.append("緊密收市 Tight Closes (籌碼高度沉澱)")

        # 4. DRSI (Stoch RSI) 買點 (滿分 15)
        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss.replace(0, 1e-9)))))
        stoch_k = 100 * (rsi - rsi.rolling(14).min()) / ((rsi.rolling(14).max() - rsi.rolling(14).min()).replace(0, 1e-9))
        stoch_d = stoch_k.rolling(3).mean()
        k_val = float(stoch_k.iloc[-1])
        d_val = float(stoch_d.iloc[-1])
        prev_k = float(stoch_k.iloc[-2])
        prev_d = float(stoch_d.iloc[-2])

        drsi_status = "中性"
        if prev_k <= prev_d and k_val > d_val:
            if k_val < 35:
                score += 15
                drsi_status = "超賣金叉 (絕佳買點)"
                reasons.append("DRSI 超賣區向上金叉 (買點成立)")
            else:
                score += 12
                drsi_status = "多頭金叉 (順勢買點)"
                reasons.append("DRSI 多頭動能金叉轉強")
        elif k_val > d_val:
            score += 8
            drsi_status = "多頭維持"
        elif k_val < 25:
            score += 6
            drsi_status = "超賣醞釀"

        # 5. 20 EMA 動態支撐 (滿分 10)
        dist_ema20 = ((curr_price - ema20) / ema20) * 100
        if 0 <= dist_ema20 <= 2.5:
            score += 10
            reasons.append("回踩 20 EMA 支撐不破 (黃金買區)")
        elif -2.0 <= dist_ema20 < 0:
            score += 6
            reasons.append("回測 20 EMA 關鍵支撐線")
        elif 2.5 < dist_ema20 <= 6.0:
            score += 5

        # 6. 量能分析 (滿分 10)
        v_50 = float(v.rolling(50).mean().iloc[-1])
        rvol = float(v.iloc[-1]) / (v_50 if v_50 > 0 else 1)
        if change_pct > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"爆量突破 (RVOL {rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("成交量乾涸 (Volume Dry-up 洗盤完成)")
        else:
            score += 4

        total_score = int(np.clip(score, 0, 100))
        
        if total_score >= 80 and is_stage2:
            rank = "Diamond"
        elif total_score >= 65:
            rank = "Gold"
        elif total_score >= 50:
            rank = "Silver"
        else:
            rank = "Bronze"

        # 7. 風控計算 (進出場點位)
        entry_price = round(curr_price, 2)
        calc_stop = max(entry_price - (1.5 * atr14), ema20 * 0.985)
        stop_price = round(min(max(calc_stop, entry_price * 0.93), entry_price * 0.97), 2)
        risk_per_share = round(entry_price - stop_price, 2)
        stop_pct = round(((stop_price - entry_price) / entry_price) * 100, 2)

        target_2r = round(entry_price + (2.0 * risk_per_share), 2)
        target_3r = round(entry_price + (3.0 * risk_per_share), 2)

        return {
            "Symbol": symbol,
            "Rank": rank,
            "Score": total_score,
            "Price": entry_price,
            "Change": round(change_pct, 2),
            "RS": rs_rating,
            "Stage2": "是 (符合)" if is_stage2 else "否",
            "DRSI_Status": drsi_status,
            "RVOL": round(rvol, 2),
            "Dist_20EMA": round(dist_ema20, 2),
            "Entry": entry_price,
            "Stop": stop_price,
            "Stop_Pct": stop_pct,
            "Target_2R": target_2r,
            "Target_3R": target_3r,
            "Risk_Per_Share": risk_per_share,
            "Reasons": reasons
        }
    except Exception:
        return None

# ==========================================
# 5. 主應用邏輯 (App Execution)
# ==========================================
inject_tesla_theme()

with st.sidebar:
    st.markdown("## ⚡ J LAW ALPHA HUNTER")
    st.caption("Tesla Cyberpunk Edition")
    st.markdown("---")

    st.markdown("### ⚙️ 風控參數設定")
    account_capital = st.number_input("總賬戶資產 ($)", min_value=1000, max_value=10000000, value=50000, step=5000)
    risk_pct = st.slider("單筆最大承受風險 (%)", min_value=0.5, max_value=2.5, value=1.0, step=0.1, help="J Law 紀律：每筆止損不超過總資產 1%")
    max_pos_cap = st.slider("單一持倉金額上限 (%)", min_value=10, max_value=40, value=25, step=5)

    max_risk_dollars = account_capital * (risk_pct / 100.0)
    st.markdown(f"""
    <div style="background:rgba(18, 24, 38, 0.85); border:1px solid rgba(255, 255, 255, 0.1); border-radius:6px; padding:12px; font-family:'JetBrains Mono'; font-size:13px;">
        <div>單筆最大風險額: <b style="color:#EF4444;">${max_risk_dollars:,.2f}</b></div>
        <div>單一持倉金額上限: <b style="color:#38BDF8;">${account_capital * (max_pos_cap/100):,.2f}</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 🌐 股票掃描池")
    custom_add = st.text_area("自訂增補代碼 (逗號隔開)", value="TSLA, NVDA, PLTR, AMD, BE, CEG")
    custom_tickers = [x.strip().upper() for x in custom_add.split(",") if x.strip()]
    full_scan_list = list(dict.fromkeys(DEFAULT_UNIVERSE + custom_tickers))
    st.caption(f"即將自動全量掃描 **{len(full_scan_list)}** 隻美股核心動能標的。")

# 自動掃描 (首次進入即自動執行)
if 'scan_data' not in st.session_state:
    with st.spinner("⚡ 正在全網自動掃描符合 J Law 選股標準的美股..."):
        stock_dict, df_spy, df_qqq = get_all_market_data(full_scan_list)
        if stock_dict is not None and df_spy is not None:
            results = []
            for sym, df_t in stock_dict.items():
                res = evaluate_jlaw_stock(sym, df_t, df_spy)
                if res is not None:
                    results.append(res)
            df_res = pd.DataFrame(results)
            if not df_res.empty:
                df_res = df_res.sort_values(by=['Score', 'RS'], ascending=[False, False]).reset_index(drop=True)
            st.session_state['scan_data'] = df_res
        else:
            st.session_state['scan_data'] = pd.DataFrame()

df_results = st.session_state.get('scan_data', pd.DataFrame())

# 頁面主標題
st.title("⚡ J LAW ALPHA HUNTER • TESLA CYBER EDITION")
st.caption("全自動 J Law 系統掃描器 • Stage 2 範式 • RS 領頭羊 • VCP 波動收窄 • 1% 風險模型")

if df_results.empty:
    st.error("暫未獲取到數據，請重試或檢查網絡連線。")
    st.stop()

# 僅過濾出符合 J Law 標準的標的 (Diamond & Gold，或 Score >= 60)
df_qualified = df_results[df_results['Score'] >= 60].copy()
if df_qualified.empty:
    df_qualified = df_results.head(5).copy()

# ==============================================================================
# 第一部分：自動搜尋符合的美股
# ==============================================================================
st.markdown("""
<div class="section-header">
    <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
        1️⃣ 第一部分：自動搜尋符合 J LAW 標準的美股 (Qualified Opportunities)
    </h3>
    <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
        系統已自動完成全市場掃描，按 J Law Alpha 分數與 RS 強度排名，以下是目前完全符合條件之候選名單。
    </div>
</div>
""", unsafe_allow_html=True)

# 頂部概覽卡片
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("全網掃描股票數", f"{len(df_results)} 隻")
m_col2.metric("💎 鑽石級 Alpha 領頭羊", f"{len(df_results[df_results['Rank'] == 'Diamond'])} 隻")
m_col3.metric("🥇 黃金級優質突破股", f"{len(df_results[df_results['Rank'] == 'Gold'])} 隻")
m_col4.metric("觀察池平均 RS 強度", f"{int(df_results['RS'].mean())} / 99")

st.write("")

# 快捷卡片展示前列標的
card_cols = st.columns(min(4, len(df_qualified)))
for i in range(min(4, len(df_qualified))):
    row_q = df_qualified.iloc[i]
    badge_style = "badge-diamond" if row_q['Rank'] == 'Diamond' else "badge-gold"
    with card_cols[i]:
        st.markdown(f"""
        <div class="cyber-card {'card-diamond' if row_q['Rank']=='Diamond' else 'card-gold'}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="badge {badge_style}">{row_q['Rank']}</span>
                <span style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8;">SCORE {row_q['Score']}</span>
            </div>
            <div style="font-size:32px; font-weight:800; font-family:'JetBrains Mono'; margin:8px 0; color:#FFF;">
                {row_q['Symbol']}
            </div>
            <div style="font-size:17px; font-family:'JetBrains Mono'; font-weight:600; color:{'#10B981' if row_q['Change'] >= 0 else '#EF4444'};">
                ${row_q['Price']:.2f} ({'+' if row_q['Change']>0 else ''}{row_q['Change']:.2f}%)
            </div>
            <div style="margin-top:8px; font-size:12px; color:#94A3B8; font-family:'JetBrains Mono';">
                RS: <b style="color:#FFF;">{row_q['RS']}</b> | Stage 2: <b style="color:#FFF;">{row_q['Stage2']}</b><br>
                DRSI: <b style="color:#FFF;">{row_q['DRSI_Status']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 完整符合清單表格
with st.expander("📋 查看所有符合 J Law 條件的美股完整數據表", expanded=True):
    st.dataframe(
        df_qualified[['Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Stage2', 'DRSI_Status', 'RVOL', 'Dist_20EMA', 'Entry', 'Stop', 'Stop_Pct', 'Target_2R']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
            "RS": st.column_config.ProgressColumn("RS 相對強度", min_value=1, max_value=99, format="%d"),
            "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
            "Price": st.column_config.NumberColumn("現價 ($)", format="$%.2f"),
            "Entry": st.column_config.NumberColumn("買入價 ($)", format="$%.2f"),
            "Stop": st.column_config.NumberColumn("止損價 ($)", format="$%.2f"),
            "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
            "Target_2R": st.column_config.NumberColumn("2R 目標 ($)", format="$%.2f"),
            "Dist_20EMA": st.column_config.NumberColumn("距 20EMA (%)", format="%.1f%%"),
            "RVOL": st.column_config.NumberColumn("量能放大", format="%.2fx")
        }
    )

# ==============================================================================
# 第二部分：解釋點解符合？
# ==============================================================================
st.markdown("""
<div class="section-header">
    <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
        2️⃣ 第二部分：深度剖析 —— 點解符合 J LAW 選股標準？ (Why It Matches)
    </h3>
    <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
        選取任一目標股票，系統將為你逐項拆解其在 J Law 7 大核心量化維度的具體表現，並展示 TradingView 即時走勢圖。
    </div>
</div>
""", unsafe_allow_html=True)

selected_stock = st.selectbox(
    "🎯 選擇要深度查看的股票：",
    df_qualified['Symbol'].tolist(),
    index=0
)

stock_row = df_qualified[df_qualified['Symbol'] == selected_stock].iloc[0]

c_exp1, c_exp2 = st.columns([1.1, 1.9])

with c_exp1:
    st.markdown(f"#### 🔍 **{selected_stock}** 符合 J Law 規則逐條解析")
    
    # 7 大維度檢核項目
    checklist = [
        ("1. Stage 2 趨勢範式", stock_row['Stage2'] == "是 (符合)", "股價 > 50SMA > 150SMA > 200SMA，長期趨勢向上，排除逆勢抄底股。"),
        ("2. RS 領頭羊地位 (≥80)", stock_row['RS'] >= 80, f"當前 RS 為 {stock_row['RS']} 分，大幅跑贏 80% 以上的市場股票。"),
        ("3. VCP 波動收窄 (Tightness)", any("VCP" in r for r in stock_row['Reasons']), "近期波動度 (ATR) 顯著收縮，籌碼被大資金鎖定。"),
        ("4. DRSI 動能買點", "金叉" in stock_row['DRSI_Status'], f"DRSI 處於「{stock_row['DRSI_Status']}」，給出順勢起爆點。"),
        ("5. 20 EMA 關鍵支撐", abs(stock_row['Dist_20EMA']) <= 3.0, f"距離 20 EMA 僅 {stock_row['Dist_20EMA']}%，處於低風險回踩或起跳買區。"),
        ("6. 量能蓄勢與突破", stock_row['RVOL'] >= 1.2 or stock_row['RVOL'] < 0.8, f"相對成交量 (RVOL) 為 {stock_row['RVOL']}x，量縮蓄勢或放量突破確認。"),
        ("7. 風險收益比 (≥ 2:1)", abs(stock_row['Stop_Pct']) <= 7.0, f"止損空間僅 {abs(stock_row['Stop_Pct'])}%，提供極佳的盈虧比空間。")
    ]

    for title, passed, desc in checklist:
        status_icon = "✅" if passed else "⚠️"
        border_color = "#10B981" if passed else "#F59E0B"
        st.markdown(f"""
        <div style="background:rgba(18, 24, 38, 0.8); border-left:4px solid {border_color}; padding:10px 14px; margin-bottom:10px; border-radius:6px;">
            <div style="font-weight:700; color:#FFF; font-size:14px;">{status_icon} {title}</div>
            <div style="font-size:12px; color:#94A3B8; margin-top:2px;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

with c_exp2:
    st.markdown(f"#### 📊 **{selected_stock}** TradingView 專業即時走勢圖")
    tv_code = f"""
    <div class="tradingview-widget-container" style="height:480px;width:100%;">
      <div id="tv_{selected_stock}" style="height:calc(100% - 32px);width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{selected_stock}",
        "interval": "D",
        "timezone": "America/New_York",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#0B0E14",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tv_{selected_stock}"
      }}
      );
      </script>
    </div>
    """
    components.html(tv_code, height=490)

# ==============================================================================
# 第三部分：計算進場點同離場點
# ==============================================================================
st.markdown("""
<div class="section-header">
    <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
        3️⃣ 第三部分：精準計算進場點、離場點與 1% 風險倉位 (Trade Execution & Risk)
    </h3>
    <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
        遵循 J Law 核心紀律：永遠先計算承受風險，再決定入場頭寸。嚴格執行 1% 賬戶最大虧損原則。
    </div>
</div>
""", unsafe_allow_html=True)

# 依據所選股票進行精準風控運算
target_entry = stock_row['Entry']
target_stop = stock_row['Stop']
target_risk_per_share = stock_row['Risk_Per_Share']
target_stop_pct = stock_row['Stop_Pct']
target_2r = stock_row['Target_2R']
target_3r = stock_row['Target_3R']

# 1% 風險股數計算
calc_shares = int(max_risk_dollars / target_risk_per_share) if target_risk_per_share > 0 else 0
total_pos_cost = calc_shares * target_entry
pos_pct_of_capital = (total_pos_cost / account_capital) * 100

# 檢查是否超出單一持倉上限
max_allowed_cost = account_capital * (max_pos_cap / 100.0)
adjusted_warning = ""
if total_pos_cost > max_allowed_cost:
    calc_shares = int(max_allowed_cost / target_entry)
    total_pos_cost = calc_shares * target_entry
    pos_pct_of_capital = (total_pos_cost / account_capital) * 100
    adjusted_warning = f"⚠️ 註：原股數超過單一持倉上限 ({max_pos_cap}%)，系統已自動調整至最高允許股數。"

plan_c1, plan_c2 = st.columns()

with plan_c1:
    st.markdown(f"""
    <div class="action-box">
        <h4 style="margin:0 0 12px 0; color:#38BDF8;">🎯 {selected_stock} 點位計算結果</h4>
        <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap: 14px; font-size:15px;">
            <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                <span style="color:#94A3B8; font-size:12px;">🔵 買入進場點 (Entry):</span><br>
                <b style="font-size:20px; color:#38BDF8;">${target_entry:.2f}</b>
            </div>
            <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                <span style="color:#94A3B8; font-size:12px;">🔴 防守離場止損 (Stop Loss):</span><br>
                <b style="font-size:20px; color:#EF4444;">${target_stop:.2f} ({target_stop_pct}%)</b>
            </div>
            <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                <span style="color:#94A3B8; font-size:12px;">🟢 第一離場目標 (2R Target):</span><br>
                <b style="font-size:20px; color:#10B981;">${target_2r:.2f}</b><br>
                <span style="font-size:11px; color:#6EE7B7;">平半倉鎖利 + 止損移至保本</span>
            </div>
            <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                <span style="color:#94A3B8; font-size:12px;">🌟 第二離場目標 (3R+ Target):</span><br>
                <b style="font-size:20px; color:#F59E0B;">${target_3r:.2f}</b><br>
                <span style="font-size:11px; color:#FCD34D;">讓利潤奔跑，捕捉主升浪</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with plan_c2:
    st.markdown(f"""
    <div class="action-box" style="border-color: rgba(16, 185, 129, 0.4);">
        <h4 style="margin:0 0 12px 0; color:#10B981;">🛡️ J Law 1% 風險倉位計算結果</h4>
        <div style="line-height:2.0; font-size:14px;">
            <div>• 賬戶總資金: <b>${account_capital:,.2f}</b></div>
            <div>• 承受最大虧損 (1R): <b style="color:#EF4444;">${max_risk_dollars:,.2f}</b> ({risk_pct}%)</div>
            <div>• 每股風險金額: <b>${target_risk_per_share:.2f}</b></div>
            <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:10px 0;">
            <div>• <b>推薦下單股數:</b> <span style="font-size:22px; color:#10B981; font-weight:800;">{calc_shares} 股</span></div>
            <div>• <b>總頭寸所需資金:</b> <b>${total_pos_cost:,.2f}</b> ({pos_pct_of_capital:.1f}% 賬戶倉位)</div>
            <div>• <b>觸發止損時總虧損:</b> <b style="color:#EF4444;">-${calc_shares * target_risk_per_share:,.2f}</b> (完全不傷元氣)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if adjusted_warning:
    st.info(adjusted_warning)
