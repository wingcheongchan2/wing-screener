import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ==========================================
# 0. 系統核心配置
# ==========================================
st.set_page_config(
    page_title="J Law Alpha Hunter • Tesla Cyber Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. Tesla 旗艦級科技美學主題 (Tesla Cyber UI)
# ==========================================
def inject_tesla_theme():
    tesla_bg = "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=2000&q=80"
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');
        .stApp {{
            background: linear-gradient(180deg, rgba(8, 11, 16, 0.90) 0%, rgba(11, 14, 20, 0.97) 100%),
                        url('{tesla_bg}') no-repeat center center fixed;
            background-size: cover; color: #E2E8F0; font-family: 'Inter', sans-serif;
        }}
        section[data-testid="stSidebar"] {{
            background: rgba(10, 14, 23, 0.95) !important;
            backdrop-filter: blur(20px); border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        div.stButton > button:first-child {{
            background: linear-gradient(135deg, #1e2430 0%, #0d1017 100%);
            color: #FFFFFF; border: 1px solid #E82127; border-radius: 4px;
            padding: 10px 24px; font-family: 'JetBrains Mono', monospace;
            font-size: 13px; font-weight: 700; letter-spacing: 1.5px;
            box-shadow: 0 4px 15px rgba(232, 33, 39, 0.25); transition: all 0.3s ease; width: 100%;
        }}
        div.stButton > button:first-child:hover {{
            background: #E82127; color: #FFFFFF; border-color: #FF4D4D;
            box-shadow: 0 0 25px rgba(232, 33, 39, 0.7); transform: translateY(-2px);
        }}
        .cyber-card {{
            background: rgba(18, 24, 38, 0.78); backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px;
            padding: 18px; margin-bottom: 14px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}
        .card-diamond {{ border-left: 4px solid #06B6D4 !important; }}
        .card-gold {{ border-left: 4px solid #EAB308 !important; }}
        .badge {{
            display: inline-block; padding: 2px 7px; border-radius: 4px;
            font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono'; margin-right: 6px;
        }}
        .badge-diamond {{ background: rgba(6, 182, 212, 0.25); color: #22D3EE; border: 1px solid #06B6D4; }}
        .badge-gold {{ background: rgba(234, 179, 8, 0.25); color: #FACC15; border: 1px solid #EAB308; }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }}
        .badge-red {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }}
        .badge-tesla {{ background: rgba(232, 33, 39, 0.25); color: #FF6B6B; border: 1px solid #E82127; }}
        .section-header {{
            background: rgba(15, 23, 42, 0.88); border-left: 5px solid #E82127;
            padding: 12px 18px; border-radius: 6px; margin: 18px 0 14px 0;
        }}
        .action-box {{
            background: rgba(10, 15, 26, 0.92); border: 1px solid rgba(232, 33, 39, 0.35);
            border-radius: 8px; padding: 18px; font-family: 'JetBrains Mono', monospace;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 核心標的池 (對齊每日任務)
# ==========================================
CORE_PORTFOLIO_SYMBOLS = ["TSLA", "AAOI", "NVDA", "MU", "BE", "NBIS", "DDOG"]

DEFAULT_UNIVERSE = list(dict.fromkeys(CORE_PORTFOLIO_SYMBOLS + [
    "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "AVGO", "ARM", "QCOM", "TSM", "ASML", 
    "LRCX", "KLAC", "SMCI", "MRVL", "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", 
    "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI", "CEG", "VST", "GE", "CAT", 
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON"
]))

# ==========================================
# 3. 數據引擎
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_data(tickers):
    needed = list(set(tickers + ['SPY', 'QQQ', 'DIA']))
    try:
        data = yf.download(needed, period="1y", interval="1d", progress=False, group_by='ticker', threads=True)
    except Exception:
        return None, None, None, None
    if data is None or data.empty:
        return None, None, None, None

    def get_df(raw, sym):
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                if sym in raw.columns.levels[0]: df = raw[sym].copy()
                elif sym in raw.columns.levels: df = raw.xs(sym, axis=1, level=1).copy()
                else: return None
            else: df = raw.copy()
            df = df.dropna(subset=['Close'])
            return df if len(df) >= 120 else None
        except Exception: return None

    stocks = {s: get_df(data, s) for s in tickers if get_df(data, s) is not None}
    return stocks, get_df(data, 'SPY'), get_df(data, 'QQQ'), get_df(data, 'DIA')

# ==========================================
# 4. J Law 7 維度選股與結構性定價演算法
# ==========================================
def evaluate_jlaw_stock(symbol, df, df_spy):
    try:
        c, h, l, v = df['Close'], df['High'], df['Low'], df['Volume']
        curr = float(c.iloc[-1])
        prev = float(c.iloc[-2])
        chg = ((curr - prev) / prev) * 100

        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma150 = float(c.rolling(150).mean().iloc[-1]) if len(c) >= 150 else sma50
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma150
        sma200_prev = float(c.rolling(200).mean().iloc[-20]) if len(c) >= 220 else sma200

        h52 = float(h.iloc[-min(len(c), 252):].max())
        l52 = float(l.iloc[-min(len(c), 252):].min())
        dist_h52 = ((curr - h52) / h52) * 100
        dist_l52 = ((curr - l52) / l52) * 100

        reasons = []
        score = 0

        # 1. Stage 2 趨勢
        is_stage2 = False
        if curr > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 15
            if sma200 >= sma200_prev: score += 5
            if dist_h52 >= -25.0 and dist_l52 >= 25.0:
                score += 5
                is_stage2 = True
                reasons.append("Stage 2 均線完美多頭")
        elif curr > sma50:
            score += 8
            if dist_h52 >= -20.0: reasons.append("50SMA 上方強勢整理")

        # 2. RS Rating
        def perf(s, d): return (s.iloc[-1] / s.iloc[-min(len(s)-1, d)]) - 1
        stk_perf = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, 252)
        spy_perf = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_rating = int(np.clip(50 + (stk_perf - spy_perf) * 150, 1, 99))
        if rs_rating >= 80:
            score += 25
            reasons.append(f"強勢領頭羊 (RS {rs_rating})")
        elif rs_rating >= 65:
            score += 18
            reasons.append(f"優於大盤 (RS {rs_rating})")
        elif rs_rating >= 50: score += 10

        # 3. VCP 波動收窄
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 10
            reasons.append("VCP 波動收窄蓄勢")
        if float(c.iloc[-5:].std() / curr) < 0.025:
            score += 5
            reasons.append("緊密收市 (Tight Closes)")

        # 4. DRSI 買點
        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss.replace(0, 1e-9)))))
        stoch_k = 100 * (rsi - rsi.rolling(14).min()) / ((rsi.rolling(14).max() - rsi.rolling(14).min()).replace(0, 1e-9))
        stoch_d = stoch_k.rolling(3).mean()
        k_val, d_val = float(stoch_k.iloc[-1]), float(stoch_d.iloc[-1])
        prev_k, prev_d = float(stoch_k.iloc[-2]), float(stoch_d.iloc[-2])

        drsi_status = "中性"
        if prev_k <= prev_d and k_val > d_val:
            if k_val < 35:
                score += 15
                drsi_status = "超賣金叉 (絕佳買點)"
                reasons.append("DRSI 超賣金叉")
            else:
                score += 12
                drsi_status = "多頭金叉 (順勢買點)"
                reasons.append("DRSI 多頭金叉")
        elif k_val > d_val:
            score += 8
            drsi_status = "多頭維持"
        elif k_val < 25: score += 6

        # 5. 20 EMA 支撐
        dist_ema20 = ((curr - ema20) / ema20) * 100
        if 0 <= dist_ema20 <= 2.5:
            score += 10
            reasons.append("回踩 20 EMA 支撐買區")
        elif -2.0 <= dist_ema20 < 0:
            score += 6
            reasons.append("回測 20 EMA 關鍵均線")
        elif 2.5 < dist_ema20 <= 6.0: score += 5

        # 6. 量能分析
        v_50 = float(v.rolling(50).mean().iloc[-1])
        rvol = float(v.iloc[-1]) / (v_50 if v_50 > 0 else 1)
        if chg > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"放量突破 (RVOL {rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("量能乾涸 (VDU)")
        else: score += 4

        total_score = int(np.clip(score, 0, 100))
        rank = "Diamond" if (total_score >= 80 and is_stage2) else ("Gold" if total_score >= 65 else ("Silver" if total_score >= 50 else "Bronze"))

        # 7. 結構性買點定價 (非盲目現價買)
        recent_10d_high = float(h.iloc[-10:].max())
        recent_10d_low = float(l.iloc[-10:].min())
        if dist_ema20 <= 3.0:
            setup_type = "20 EMA 回踩低吸點"
            calc_entry = round(ema20 * 1.003, 2)
            calc_stop = round(min(ema20 * 0.965, calc_entry - (1.5 * atr14)), 2)
        else:
            setup_type = "VCP 阻力樞紐突破點"
            calc_entry = round(recent_10d_high * 1.002, 2)
            calc_stop = round(max(recent_10d_low * 0.99, calc_entry - (1.5 * atr14)), 2)

        calc_stop = min(calc_stop, round(calc_entry * 0.97, 2))
        calc_stop = max(calc_stop, round(calc_entry * 0.925, 2))
        risk_per_share = round(calc_entry - calc_stop, 2)
        stop_pct = round(((calc_stop - calc_entry) / calc_entry) * 100, 2)

        target_2r = round(calc_entry + (2.0 * risk_per_share), 2)
        target_3r = round(calc_entry + (3.0 * risk_per_share), 2)
        entry_diff = round(((curr - calc_entry) / calc_entry) * 100, 2)

        return {
            "Symbol": symbol, "Rank": rank, "Score": total_score, "Price": round(curr, 2),
            "Change": round(chg, 2), "RS": rs_rating, "Stage2": "是 (符合)" if is_stage2 else "否",
            "DRSI_Status": drsi_status, "RVOL": round(rvol, 2), "Dist_20EMA": round(dist_ema20, 2),
            "Setup_Type": setup_type, "Entry": calc_entry, "Entry_Diff": entry_diff,
            "Stop": calc_stop, "Stop_Pct": stop_pct, "Target_2R": target_2r, "Target_3R": target_3r,
            "Risk_Per_Share": risk_per_share, "RSI": round(float(rsi.iloc[-1]), 1),
            "Reasons": reasons
        }
    except Exception:
        return None

# ==========================================
# 5. 主應用渲染
# ==========================================
inject_tesla_theme()

with st.sidebar:
    st.markdown("## ⚡ TESLA CYBER")
    st.caption("J Law Alpha Hunter • Autonomous Desk")
    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(232, 33, 39, 0.12); border:1px solid #E82127; border-radius:6px; padding:10px; margin-bottom:12px;">
        <div style="font-weight:700; color:#FF6B6B; font-size:12px;">🤖 OPTIMUS QUANT CORE</div>
        <div style="font-size:11px; color:#CBD5E1; margin-top:2px;">
            全自動加權 RS · 樞紐阻力測算 · 1% 資金防護矩陣
        </div>
    </div>
    """, unsafe_allow_html=True)
    custom_add = st.text_area("增補美股代碼 (逗號隔開)", value="")
    custom_tickers = [x.strip().upper() for x in custom_add.split(",") if x.strip()]
    full_scan_list = list(dict.fromkeys(DEFAULT_UNIVERSE + custom_tickers))
    st.caption(f"監測標的總數：**{len(full_scan_list)}** 隻")
    st.write("")
    if st.button("⚡ 重新掃描市場 (RE-SCAN)"):
        st.session_state.pop('scan_data', None)
        st.rerun()

if 'scan_data' not in st.session_state:
    with st.spinner("⚡ Optimus 正在執行全網自動量化計算，掃描符合 J Law 標準的美股..."):
        stock_dict, df_spy, df_qqq, df_dia = fetch_all_data(full_scan_list)
        if stock_dict is not None and df_spy is not None:
            results = [evaluate_jlaw_stock(sym, df_t, df_spy) for sym, df_t in stock_dict.items()]
            results = [r for r in results if r is not None]
            df_res = pd.DataFrame(results)
            if not df_res.empty:
                df_res = df_res.sort_values(by=['Score', 'RS'], ascending=[False, False]).reset_index(drop=True)
            st.session_state['scan_data'] = df_res
            st.session_state['market_indexes'] = {'SPY': df_spy, 'QQQ': df_qqq, 'DIA': df_dia}
        else:
            st.session_state['scan_data'] = pd.DataFrame()
            st.session_state['market_indexes'] = {}

df_results = st.session_state.get('scan_data', pd.DataFrame())
indexes = st.session_state.get('market_indexes', {})

# 頂部 Tesla 標誌橫幅
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; background:rgba(18,24,38,0.85); border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:14px 20px; margin-bottom:18px;">
    <div>
        <span style="font-size:22px; font-weight:900; font-family:'JetBrains Mono'; color:#FFF; letter-spacing:1px;">
            ⚡ J LAW ALPHA HUNTER <span style="color:#E82127;">// TESLA CYBER TERMINAL</span>
        </span>
        <div style="font-size:12px; color:#94A3B8; margin-top:2px;">
            AUTONOMOUS SWING TRADING DESK • POWERED BY OPTIMUS & CYBERCAB ALGORITHM
        </div>
    </div>
    <div>
        <span class="badge badge-tesla">CYBERCAB ONLINE</span>
        <span class="badge badge-diamond">OPTIMUS V3 ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

if df_results.empty:
    st.error("暫未獲取到市場數據，請檢查網絡連線。")
    st.stop()

# 導航切換
nav_mode = st.radio(
    "導航模式",
    [
        "🌐 每日美股宏觀體檢 (Daily Macro & Index Telemetry)",
        "🛡️ 核心持倉實戰情報 (Core Portfolio Tactics)",
        "01 // ⚡ 領頭羊即時機會庫 (J Law Alpha Screener)",
        "02 // 🔍 7 維技術診斷與圖表 (Deep Technical Radar)",
        "03 // 🎯 OPTIMUS 1% 風險倉位與執行矩陣 (Execution Matrix)"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ----------------------------------------------------
# 模組 1: 每日美股宏觀體檢
# ----------------------------------------------------
if nav_mode == "🌐 每日美股宏觀體檢 (Daily Macro & Index Telemetry)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">🌐 每日美股市場追蹤 • 三大官方基準指數與體檢</h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
            落實官方指數均線結構與市場廣度，一句話定調「巨頭吸血」還是「資金擴散」。
        </div>
    </div>
    """, unsafe_allow_html=True)

    qqq_df, spy_df, dia_df = indexes.get('QQQ'), indexes.get('SPY'), indexes.get('DIA')
    qqq_curr = float(qqq_df['Close'].iloc[-1]) if qqq_df is not None else 0
    qqq_ema20 = float(qqq_df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]) if qqq_df is not None else 0
    is_healthy = qqq_curr > qqq_ema20

    st.markdown(f"""
    <div class="cyber-card" style="border-left:4px solid {'#10B981' if is_healthy else '#F59E0B'};">
        <b style="color:{'#10B981' if is_healthy else '#F59E0B'}; font-size:15px;">
            📊 大盤體檢置頂結論：{'【強勢多頭・主升波段】：納指與標普站穩 20 EMA 上方，領頭羊板塊健康輪動，可積極把握突破與回踩機會。' if is_healthy else '【震盪整理・防守為王】：指數測試關鍵支撐，嚴格控制倉位，嚴禁盲目追高。'}
        </b>
        <div style="font-size:12px; color:#CBD5E1; margin-top:4px;">
            • 流動性風向：納指 100 維持多頭排列，地緣與通脹數據影響處於可控消化期。<br>
            • 賺錢效應判斷：高動能標的呈現籌碼沉澱蓄勢特徵，符合 J Law 範式股票表現抗跌。
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    def render_idx(sym, name, df, col):
        if df is None: return
        c = df['Close']
        curr, prev = float(c.iloc[-1]), float(c.iloc[-2])
        chg = ((curr - prev) / prev) * 100
        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma50
        atr14 = float((df['High'] - df['Low']).rolling(14).mean().iloc[-1])
        r1, s1 = curr + atr14, curr - atr14
        is_bull = curr > ema20
        with col:
            st.markdown(f"""
            <div class="cyber-card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="font-weight:700; color:#FFF;">{sym} ({name})</span>
                    <span class="badge {'badge-green' if is_bull else 'badge-red'}">{'Stage 2 多頭' if is_bull else '回調防守'}</span>
                </div>
                <div style="font-size:26px; font-weight:800; font-family:'JetBrains Mono'; margin:6px 0; color:#FFF;">
                    ${curr:.2f} <span style="font-size:14px; color:{'#10B981' if chg>=0 else '#EF4444'};">({'+' if chg>=0 else ''}{chg:.2f}%)</span>
                </div>
                <div style="font-size:11px; color:#94A3B8; font-family:'JetBrains Mono'; line-height:1.7;">
                    • 20 EMA: <b style="color:#FFF;">${ema20:.2f}</b> ({'+' if curr>ema20 else ''}{(curr-ema20)/ema20*100:.1f}%)<br>
                    • 50 SMA: <b style="color:#FFF;">${sma50:.2f}</b> | 200 SMA: <b style="color:#FFF;">${sma200:.2f}</b><br>
                    • 阻力 R1: <b style="color:#38BDF8;">${r1:.2f}</b> | 支撐 S1: <b style="color:#EF4444;">${s1:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    render_idx("QQQ", "納斯達克 100", qqq_df, c1)
    render_idx("SPY", "標普 500", spy_df, c2)
    render_idx("DIA", "道瓊斯工業", dia_df, c3)

# ----------------------------------------------------
# 模組 2: 核心持倉實戰情報
# ----------------------------------------------------
elif nav_mode == "🛡️ 核心持倉實戰情報 (Core Portfolio Tactics)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">🛡️ 核心自選持倉實戰情報 (TSLA · AAOI · NVDA · MU · BE · NBIS · DDOG)</h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
            對齊富途指標參數：現價、RVOL量比、結構買入價、止損價與 2R/3R 止盈目標。
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_core = df_results[df_results['Symbol'].isin(CORE_PORTFOLIO_SYMBOLS)].copy()
    if not df_core.empty:
        st.dataframe(
            df_core[['Symbol', 'Price', 'Change', 'RS', 'Score', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R', 'RSI', 'RVOL']],
            use_container_width=True, hide_index=True,
            column_config={
                "Symbol": st.column_config.TextColumn("代碼"),
                "Price": st.column_config.NumberColumn("收市價 ($)", format="$%.2f"),
                "Change": st.column_config.NumberColumn("漲跌 (%)", format="%.2f%%"),
                "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
                "RS": st.column_config.ProgressColumn("RS 強度", min_value=1, max_value=99, format="%d"),
                "Setup_Type": st.column_config.TextColumn("戰術型態"),
                "Entry": st.column_config.NumberColumn("結構買入價 ($)", format="$%.2f"),
                "Entry_Diff": st.column_config.NumberColumn("距買點 (%)", format="%.2f%%"),
                "Stop": st.column_config.NumberColumn("防守止損 ($)", format="$%.2f"),
                "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
                "Target_2R": st.column_config.NumberColumn("第一目標 (2R)", format="$%.2f"),
                "Target_3R": st.column_config.NumberColumn("第二目標 (3R)", format="$%.2f"),
                "RSI": st.column_config.NumberColumn("RSI (14)", format="%.1f"),
                "RVOL": st.column_config.NumberColumn("量比 RVOL", format="%.2fx")
            }
        )

# ----------------------------------------------------
# 模組 3: 領頭羊即時機會庫
# ----------------------------------------------------
elif nav_mode == "01 // ⚡ 領頭羊即時機會庫 (J Law Alpha Screener)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">01 // ⚡ ALPHA SCREENER • J LAW 領頭羊即時機會庫</h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
            全市場掃描排序庫：依據 Stage 2、加權百分位 RS ≥ 80、VCP 波動收窄甄選潛力標的。
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_qualified = df_results[df_results['Score'] >= 60].copy()
    if df_qualified.empty: df_qualified = df_results.head(6).copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("掃描總股票數", f"{len(df_results)} 隻")
    m2.metric("💎 鑽石級領頭羊", f"{len(df_results[df_results['Rank'] == 'Diamond'])} 隻")
    m3.metric("🥇 黃金級突破股", f"{len(df_results[df_results['Rank'] == 'Gold'])} 隻")
    m4.metric("平均 RS 強度", f"{int(df_results['RS'].mean())} / 99")

    st.write("")
    card_cols = st.columns(min(4, len(df_qualified)))
    for i in range(min(4, len(df_qualified))):
        row_q = df_qualified.iloc[i]
        b_class = "badge-diamond" if row_q['Rank'] == 'Diamond' else "badge-gold"
        with card_cols[i]:
            st.markdown(f"""
            <div class="cyber-card {'card-diamond' if row_q['Rank']=='Diamond' else 'card-gold'}">
                <div style="display:flex; justify-content:space-between;">
                    <span class="badge {b_class}">{row_q['Rank']}</span>
                    <span style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8;">SCORE {row_q['Score']}</span>
                </div>
                <div style="font-size:30px; font-weight:800; font-family:'JetBrains Mono'; margin:6px 0; color:#FFF;">
                    {row_q['Symbol']}
                </div>
                <div style="font-size:15px; font-family:'JetBrains Mono'; font-weight:600; color:{'#10B981' if row_q['Change'] >= 0 else '#EF4444'};">
                    ${row_q['Price']:.2f} ({'+' if row_q['Change']>0 else ''}{row_q['Change']:.2f}%)
                </div>
                <div style="margin-top:6px; font-size:11px; color:#CBD5E1; font-family:'JetBrains Mono'; line-height:1.6;">
                    型態: <b style="color:#38BDF8;">{row_q['Setup_Type']}</b><br>
                    買入價: <b style="color:#FFF;">${row_q['Entry']:.2f}</b> | 止損: <b style="color:#EF4444;">${row_q['Stop']:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📋 查看所有合格標的數據清單", expanded=True):
        st.dataframe(
            df_qualified[['Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Stage2', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R']],
            use_container_width=True, hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
                "RS": st.column_config.ProgressColumn("RS 相對強度", min_value=1, max_value=99, format="%d"),
                "Change": st.column_config.NumberColumn("漲跌 (%)", format="%.2f%%"),
                "Price": st.column_config.NumberColumn("現價 ($)", format="$%.2f"),
                "Setup_Type": st.column_config.TextColumn("戰術型態"),
                "Entry": st.column_config.NumberColumn("結構買入價 ($)", format="$%.2f"),
                "Entry_Diff": st.column_config.NumberColumn("距買點 (%)", format="%.2f%%"),
                "Stop": st.column_config.NumberColumn("防守止損 ($)", format="$%.2f"),
                "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
                "Target_2R": st.column_config.NumberColumn("2R 止盈 ($)", format="$%.2f"),
                "Target_3R": st.column_config.NumberColumn("3R 止盈 ($)", format="$%.2f")
            }
        )

# ----------------------------------------------------
# 模組 4: 7 維技術形態診斷與圖表
# ----------------------------------------------------
elif nav_mode == "02 // 🔍 7 維技術診斷與圖表 (Deep Technical Radar)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">02 // 🔍 DEEP RADAR • 7 維技術形態診斷與 TRADINGVIEW 雷達</h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
            點解符合：對齊 Stage 2 均線、RS 領頭羊、VCP 籌碼收窄與 DRSI 金叉狀態，實時載入 TradingView 互動圖表。
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_stock = st.selectbox("選擇要深度診斷的標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == selected_stock].iloc[0]

    c_r1, c_r2 = st.columns([1.1, 1.9])
    with c_r1:
        st.markdown(f"#### 📋 **{selected_stock}** J Law 7 維檢核清單")
        checklist = [
            ("1. Stage 2 趨勢範式", stock_row['Stage2'] == "是 (符合)", "價格 > 50SMA > 150SMA > 200SMA，長期均線向上，排除逆勢垃圾股。"),
            ("2. RS 領頭羊地位 (≥80)", stock_row['RS'] >= 80, f"當前 RS Rating 為 {stock_row['RS']} 分，大幅跑贏 80% 以上市場標的。"),
            ("3. VCP 波動收窄 (Tightness)", any("VCP" in r for r in stock_row['Reasons']), "近期波幅 (ATR) 顯著收斂，主力鎖倉沉澱。"),
            ("4. DRSI 動能買點", "金叉" in stock_row['DRSI_Status'], f"DRSI 處於「{stock_row['DRSI_Status']}」，順勢買點成立。"),
            ("5. 20 EMA 關鍵支撐", abs(stock_row['Dist_20EMA']) <= 3.0, f"距離 20 EMA 僅 {stock_row['Dist_20EMA']}%，處於黃金回踩或起跳買區。"),
            ("6. 量能蓄勢與突破", stock_row['RVOL'] >= 1.2 or stock_row['RVOL'] < 0.8, f"相對量比 (RVOL) 為 {stock_row['RVOL']}x，量縮蓄勢或放量突破。"),
            ("7. 結構性買點設定", True, f"判定型態為「{stock_row['Setup_Type']}」，規劃買入價 ${stock_row['Entry']:.2f} (距現價 {stock_row['Entry_Diff']}%)。")
        ]
        for title, passed, desc in checklist:
            st.markdown(f"""
            <div style="background:rgba(18, 24, 38, 0.85); border-left:4px solid {'#10B981' if passed else '#F59E0B'}; padding:9px 12px; margin-bottom:8px; border-radius:5px;">
                <div style="font-weight:700; color:#FFF; font-size:13px;">{'✅' if passed else '⚠️'} {title}</div>
                <div style="font-size:11px; color:#94A3B8; margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with c_r2:
        st.markdown(f"#### 📊 **{selected_stock}** TradingView 專業即時走勢圖")
        tv_widget = f"""
        <div class="tradingview-widget-container" style="height:460px;width:100%;">
          <div id="tv_{selected_stock}" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{"autosize": true, "symbol": "{selected_stock}", "interval": "D", "timezone": "America/New_York", "theme": "dark", "style": "1", "locale": "zh_TW", "toolbar_bg": "#0B0E14", "enable_publishing": false, "container_id": "tv_{selected_stock}"}});
          </script>
        </div>
        """
        components.html(tv_widget, height=480)

# ----------------------------------------------------
# 模組 5: OPTIMUS 1% 風險倉位與執行矩陣
# ----------------------------------------------------
elif nav_mode == "03 // 🎯 OPTIMUS 1% 風險倉位與執行矩陣 (Execution Matrix)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">03 // 🎯 EXECUTION MATRIX • 樞紐買點、階梯止盈與 1% 倉位矩陣</h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
            買入價由圖表結構決定（樞紐突破或 20 EMA 回踩），股數由 Optimus 1% 賬戶最大風險額嚴格鎖定。
        </div>
    </div>
    """, unsafe_allow_html=True)

    calc_sym = st.selectbox("選擇要計算下單的標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == calc_sym].iloc[0]

    ic1, ic2, ic3 = st.columns(3)
    with ic1: account_capital = st.number_input("賬戶總資產 ($)", min_value=1000, max_value=10000000, value=50000, step=5000)
    with ic2: risk_pct = st.slider("單筆最大承受風險 (%)", min_value=0.5, max_value=2.5, value=1.0, step=0.1)
    with ic3: max_pos_cap = st.slider("單一持倉金額上限 (%)", min_value=10, max_value=40, value=25, step=5)

    max_risk_dollars = account_capital * (risk_pct / 100.0)
    target_entry = stock_row['Entry']
    target_stop = stock_row['Stop']
    target_risk = stock_row['Risk_Per_Share']
    target_2r = stock_row['Target_2R']
    target_3r = stock_row['Target_3R']

    calc_shares = int(max_risk_dollars / target_risk) if target_risk > 0 else 0
    total_pos_cost = calc_shares * target_entry
    pos_pct = (total_pos_cost / account_capital) * 100
    max_cost = account_capital * (max_pos_cap / 100.0)
    if total_pos_cost > max_cost:
        calc_shares = int(max_cost / target_entry)
        total_pos_cost = calc_shares * target_entry
        pos_pct = (total_pos_cost / account_capital) * 100

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown(f"""
        <div class="action-box">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <b style="color:#38BDF8; font-size:16px;">🎯 {calc_sym} 結構性進出場點位</b>
                <span class="badge badge-cyan">{stock_row['Setup_Type']}</span>
            </div>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size:13px;">
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:5px;">
                    <span style="color:#94A3B8; font-size:11px;">🔵 樞紐買入進場 (Entry):</span><br>
                    <b style="font-size:20px; color:#38BDF8;">${target_entry:.2f}</b><br>
                    <span style="font-size:11px; color:#CBD5E1;">現價: ${stock_row['Price']:.2f} (距買點 {stock_row['Entry_Diff']}%)</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:5px;">
                    <span style="color:#94A3B8; font-size:11px;">🔴 防守止損 (Stop Loss):</span><br>
                    <b style="font-size:20px; color:#EF4444;">${target_stop:.2f} ({stock_row['Stop_Pct']}%)</b><br>
                    <span style="font-size:11px; color:#EF4444;">每股承擔風險: ${target_risk:.2f}</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:5px;">
                    <span style="color:#94A3B8; font-size:11px;">🟢 第一離場目標 (2R Target):</span><br>
                    <b style="font-size:20px; color:#10B981;">${target_2r:.2f}</b><br>
                    <span style="font-size:10px; color:#6EE7B7;">平半倉鎖利 + 止損上移保本</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:5px;">
                    <span style="color:#94A3B8; font-size:11px;">🌟 第二離場目標 (3R+ Target):</span><br>
                    <b style="font-size:20px; color:#F59E0B;">${target_3r:.2f}</b><br>
                    <span style="font-size:10px; color:#FCD34D;">讓利潤奔跑，捕捉主升浪</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with p_col2:
        st.markdown(f"""
        <div class="action-box" style="border-color: rgba(16, 185, 129, 0.4);">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <b style="color:#10B981; font-size:16px;">🛡️ OPTIMUS 1% 風險倉位精算</b>
                <span class="badge badge-green">嚴格風控啟用</span>
            </div>
            <div style="line-height:2.0; font-size:13px;">
                <div>• 總賬戶資金: <b>${account_capital:,.2f}</b></div>
                <div>• 允許最大虧損 (1R): <b style="color:#EF4444;">${max_risk_dollars:,.2f}</b> ({risk_pct}%)</div>
                <div>• 每股承受風險金額: <b>${target_risk:.2f}</b></div>
                <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:8px 0;">
                <div>• <b>推薦下單股數:</b> <span style="font-size:22px; color:#10B981; font-weight:800;">{calc_shares} 股</span></div>
                <div>• <b>總頭寸所需資金:</b> <b>${total_pos_cost:,.2f}</b> ({pos_pct:.1f}% 倉位)</div>
                <div>• <b>觸發止損時總虧損:</b> <b style="color:#EF4444;">-${calc_shares * target_risk:,.2f}</b> (鎖定在 1R 內)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
