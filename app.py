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
    page_title="J Law Alpha Hunter • Tesla Cyber Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. Tesla 奢華黑金賽博 UI 樣式系統 (Tesla Cyber UI)
# ==========================================
def inject_tesla_theme():
    tesla_bg = "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=2000&q=80"
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* 全局背景：Tesla 夜幕旗艦車頭光暈 */
        .stApp {{
            background: linear-gradient(180deg, rgba(6, 9, 14, 0.92) 0%, rgba(9, 12, 18, 0.98) 100%),
                        url('{tesla_bg}') no-repeat center center fixed;
            background-size: cover;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        
        /* 側邊欄磨砂黑科技感 */
        section[data-testid="stSidebar"] {{
            background: rgba(10, 14, 23, 0.96) !important;
            backdrop-filter: blur(24px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        
        /* Tesla 實體車機質感按鈕 */
        div.stButton > button:first-child {{
            background: linear-gradient(135deg, #202736 0%, #0e1219 100%);
            color: #FFFFFF;
            border: 1px solid #E82127; /* Tesla 經典火紅 */
            border-radius: 4px;
            padding: 10px 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            box-shadow: 0 4px 15px rgba(232, 33, 39, 0.25);
            transition: all 0.3s ease;
            width: 100%;
        }}
        div.stButton > button:first-child:hover {{
            background: #E82127;
            color: #FFFFFF;
            border-color: #FF4D4D;
            box-shadow: 0 0 25px rgba(232, 33, 39, 0.7), 0 0 10px rgba(232, 33, 39, 0.9);
            transform: translateY(-2px);
        }}

        /* 磨砂黑金屬玻璃卡片 */
        .cyber-card {{
            background: rgba(18, 24, 38, 0.80);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 8px;
            padding: 18px 22px;
            margin-bottom: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            transition: all 0.25s ease;
        }}
        .cyber-card:hover {{
            border-color: #E82127;
            box-shadow: 0 10px 32px rgba(232, 33, 39, 0.2);
        }}
        
        /* 標籤微光設計 */
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
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
        .badge-tesla {{ background: rgba(232, 33, 39, 0.25); color: #FF6B6B; border: 1px solid #E82127; }}

        /* 模組光條標題 */
        .section-header {{
            background: rgba(15, 23, 42, 0.88);
            border-left: 5px solid #E82127;
            padding: 14px 20px;
            border-radius: 6px;
            margin: 16px 0 16px 0;
            backdrop-filter: blur(12px);
        }}
        
        /* 執行面板 */
        .action-box {{
            background: rgba(10, 15, 26, 0.94);
            border: 1px solid rgba(232, 33, 39, 0.35);
            border-radius: 8px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        /* 頂部 Cyber 儀表橫幅 */
        .tesla-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(18, 24, 38, 0.85);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 16px 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(16px);
        }}

        /* 呼吸燈動畫 */
        @keyframes pulse-red {{
            0% {{ box-shadow: 0 0 0 0 rgba(232, 33, 39, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(232, 33, 39, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(232, 33, 39, 0); }}
        }}
        .alert-banner {{
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.2) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid #E82127;
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 16px;
            animation: pulse-red 2s infinite;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 標的池定義 (核心自選標的對齊每日任務)
# ==========================================
CORE_PORTFOLIO_SYMBOLS = ["TSLA", "AAOI", "NVDA", "MU", "BE", "NBIS", "DDOG"]

DEFAULT_UNIVERSE = list(dict.fromkeys(CORE_PORTFOLIO_SYMBOLS + [
    "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "AVGO", "ARM", "QCOM", "TSM", "ASML", 
    "LRCX", "KLAC", "SMCI", "MRVL", "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", 
    "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI", "CEG", "VST", "GE", "CAT", 
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON"
]))

# ==========================================
# 3. 數據獲取引擎
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_data(tickers):
    needed_symbols = list(set(tickers + ['SPY', 'QQQ', 'DIA']))
    try:
        data = yf.download(needed_symbols, period="1y", interval="1d", progress=False, group_by='ticker', threads=True)
    except Exception:
        return None, None, None, None

    if data is None or data.empty:
        return None, None, None, None

    def extract_clean_df(raw_data, sym):
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                if sym in raw_data.columns.levels[0]: df = raw_data[sym].copy()
                elif sym in raw_data.columns.levels: df = raw_data.xs(sym, axis=1, level=1).copy()
                else: return None
            else: df = raw_data.copy()
            df = df.dropna(subset=['Close'])
            return df if len(df) >= 120 else None
        except Exception:
            return None

    df_spy = extract_clean_df(data, 'SPY')
    df_qqq = extract_clean_df(data, 'QQQ')
    df_dia = extract_clean_df(data, 'DIA')
    
    stocks = {s: extract_clean_df(data, s) for s in tickers if extract_clean_df(data, s) is not None}
    return stocks, df_spy, df_qqq, df_dia

# ==========================================
# 4. J Law 7 維度選股與結構性定價演算法
# ==========================================
def evaluate_jlaw_stock(symbol, df, df_spy):
    try:
        c, h, l, v = df['Close'], df['High'], df['Low'], df['Volume']
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

        # 1. Stage 2 趨勢檢核
        is_stage2 = False
        if curr_price > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 15
            if sma200 >= sma200_20d_ago: score += 5
            if dist_h52 >= -25.0 and dist_l52 >= 25.0:
                score += 5
                is_stage2 = True
                reasons.append("Stage 2 完美多頭範式 (均線向上)")
        elif curr_price > sma50:
            score += 8
            if dist_h52 >= -20.0: reasons.append("50SMA 上方強勢整理")

        # 2. 加權百分位 RS 相對強度 Rating
        def perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        stock_w_perf = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, min(252, len(c)-1))
        spy_w_perf = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_diff = (stock_w_perf - spy_w_perf) * 100
        rs_rating = int(np.clip(50 + (rs_diff * 1.5), 1, 99))

        if rs_rating >= 80:
            score += 25
            reasons.append(f"強勢領頭羊 (RS Rating {rs_rating})")
        elif rs_rating >= 65:
            score += 18
            reasons.append(f"優於大盤 (RS {rs_rating})")
        elif rs_rating >= 50: score += 10

        # 3. VCP 波動收窄與緊密收市
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 10
            reasons.append("VCP 波動收窄蓄勢")
        if float(c.iloc[-5:].std() / curr_price) < 0.025:
            score += 5
            reasons.append("緊密收市 (Tight Closes)")

        # 4. DRSI (Stoch RSI) 買點
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
        is_drsi_bullish = False
        if prev_k <= prev_d and k_val > d_val:
            is_drsi_bullish = True
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

        # 5. 20 EMA 動態支撐
        dist_ema20 = ((curr_price - ema20) / ema20) * 100
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
        if change_pct > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"爆量突破 (RVOL {rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("量能乾涸 (VDU 洗盤完成)")
        else: score += 4

        total_score = int(np.clip(score, 0, 100))
        rank = "Diamond" if (total_score >= 80 and is_stage2) else ("Gold" if total_score >= 65 else ("Silver" if total_score >= 50 else "Bronze"))

        # 7. J Law 結構性定價計算 (非盲目現價買！)
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
        entry_diff = round(((curr_price - calc_entry) / calc_entry) * 100, 2)

        # 檢測是否「完全符合所有 J Law 核心規則」
        is_all_rules_met = (is_stage2 and rs_rating >= 80 and is_drsi_bullish and abs(entry_diff) <= 3.0)

        return {
            "Symbol": symbol,
            "Rank": rank,
            "Score": total_score,
            "Price": round(curr_price, 2),
            "Change": round(change_pct, 2),
            "RS": rs_rating,
            "Stage2": "是 (符合)" if is_stage2 else "否",
            "DRSI_Status": drsi_status,
            "RVOL": round(rvol, 2),
            "Dist_20EMA": round(dist_ema20, 2),
            "Setup_Type": setup_type,
            "Entry": calc_entry,
            "Entry_Diff": entry_diff,
            "Stop": calc_stop,
            "Stop_Pct": stop_pct,
            "Target_2R": target_2r,
            "Target_3R": target_3r,
            "Risk_Per_Share": risk_per_share,
            "RSI": round(float(rsi.iloc[-1]), 1),
            "All_Rules_Met": is_all_rules_met,
            "Reasons": reasons
        }
    except Exception:
        return None

# ==========================================
# 5. 主應用邏輯與介面渲染
# ==========================================
inject_tesla_theme()

# 左側極簡 Cyber 側邊欄
with st.sidebar:
    st.markdown("## ⚡ TESLA CYBER")
    st.caption("Autonomous Swing Trading Desk")
    st.markdown("---")

    st.markdown("""
    <div style="background:rgba(232, 33, 39, 0.12); border:1px solid #E82127; border-radius:6px; padding:12px; margin-bottom:14px;">
        <div style="font-weight:700; color:#FF6B6B; font-size:13px;">🤖 OPTIMUS QUANT CORE</div>
        <div style="font-size:11px; color:#CBD5E1; margin-top:3px; line-height:1.5;">
            已啟動形態測算引擎，全自動對齊富途指標、計算結構性樞紐點位。
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🌐 自選增補池")
    custom_add = st.text_area("增補美股代碼 (逗號隔開)", value="")
    custom_tickers = [x.strip().upper() for x in custom_add.split(",") if x.strip()]
    full_scan_list = list(dict.fromkeys(DEFAULT_UNIVERSE + custom_tickers))
    st.caption(f"全天候監測標的總數：**{len(full_scan_list)}** 隻")
    
    st.write("")
    if st.button("⚡ 重新掃描市場 (RE-SCAN)"):
        st.session_state.pop('scan_data', None)
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔔 即時通知配置")
    tg_token = st.text_input("Telegram Bot Token", type="password", placeholder="選填，用於接收手機推播")
    tg_chat_id = st.text_input("Telegram Chat ID", placeholder="選填，用戶 Chat ID")
    
    if tg_token and tg_chat_id:
        st.caption("✅ Telegram 推送通道已就緒")

# 執行自動下載與分析
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
            st.session_state['market_indexes'] = {
                'SPY': df_spy, 'QQQ': df_qqq, 'DIA': df_dia
            }
        else:
            st.session_state['scan_data'] = pd.DataFrame()
            st.session_state['market_indexes'] = {}

df_results = st.session_state.get('scan_data', pd.DataFrame())
indexes = st.session_state.get('market_indexes', {})

# 頂部 Tesla 標誌性 Banner
st.markdown("""
<div class="tesla-banner">
    <div>
        <span style="font-size:24px; font-weight:900; font-family:'JetBrains Mono'; color:#FFF; letter-spacing:1px;">
            ⚡ J LAW ALPHA HUNTER <span style="color:#E82127;">// TESLA CYBER TERMINAL</span>
        </span>
        <div style="font-size:12px; color:#94A3B8; margin-top:3px;">
            INSTITUTIONAL EQUITY RESEARCH & SWING TRADING SYSTEM • POWERED BY OPTIMUS & CYBERCAB ALGORITHM
        </div>
    </div>
    <div>
        <span class="badge badge-tesla">CYBERCAB ONLINE</span>
        <span class="badge badge-diamond">OPTIMUS V3 ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

if df_results.empty:
    st.error("暫未獲取到市場數據，請檢查網絡連線或點擊側邊欄重新掃描。")
    st.stop()

# 醒目即時警報橫幅 (一發現符合所有規則的股票就警報)
perfect_matches = df_results[df_results['All_Rules_Met'] == True]
if not perfect_matches.empty:
    alert_symbols = ", ".join(perfect_matches['Symbol'].tolist())
    st.markdown(f"""
    <div class="alert-banner">
        <div style="font-size:16px; font-weight:800; color:#FF4D4D;">
            🚨 OPTIMUS 實時強勢警報觸發！發現完全符合 J LAW 7 大核心規則標的：<span style="color:#FFF; font-size:18px;">{alert_symbols}</span>
        </div>
        <div style="font-size:12px; color:#E2E8F0; margin-top:4px;">
            條件達成：Stage 2 完美多頭 · RS 評級 ≥ 80 領頭羊 · DRSI 黃金交叉 · 距離規劃買入點在 3% 內！請在下方查看進出場計劃。
        </div>
    </div>
    """, unsafe_allow_html=True)

# 導航切換（乾淨橫向排列，避免擠壓滾動）
nav_selection = st.radio(
    "導航模式選擇",
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

st.write("")

# ----------------------------------------------------
# 模組 1: 每日美股宏觀體檢
# ----------------------------------------------------
if nav_selection == "🌐 每日美股宏觀體檢 (Daily Macro & Index Telemetry)":
    st.markdown("""
    <div class="section-header">
        <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
            🌐 每日美股市場追蹤 • 三大官方基準指數與體檢
        </h3>
        <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
            嚴格落實官方基準指數（納指 QQQ / 標普 SPY / 道指 DIA）即時均線結構，一句話定調「巨頭吸血」還是「資金擴散」。
        </div>
    </div>
    """, unsafe_allow_html=True)

    qqq_df = indexes.get('QQQ')
    spy_df = indexes.get('SPY')
    dia_df = indexes.get('DIA')

    qqq_curr = float(qqq_df['Close'].iloc[-1]) if qqq_df is not None else 0
    qqq_ema20 = float(qqq_df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]) if qqq_df is not None else 0
    spy_curr = float(spy_df['Close'].iloc[-1]) if spy_df is not None else 0
    spy_sma50 = float(spy_df['Close'].rolling(50).mean().iloc[-1]) if spy_df is not None else 0

    is_healthy = qqq_curr > qqq_ema20 and spy_curr > spy_sma50
    macro_verdict = "【強勢多頭・主升波段】：科技權重與大盤均站穩 20 EMA 上方，市場廣度向成長股擴散，可積極把握高勝率買點。" if is_healthy else "【震盪整理・防守為王】：指數測試關鍵均線支撐，部分權重吸血但中小盤分化，嚴格控制倉位，嚴禁盲目追高。"

    st.markdown(f"""
    <div class="cyber-card" style="border-left:5px solid {'#10B981' if is_healthy else '#F59E0B'};">
        <div style="font-size:16px; font-weight:700; color:{'#10B981' if is_healthy else '#F59E0B'};">
            📊 大盤體檢置頂結論：{macro_verdict}
        </div>
        <div style="font-size:13px; color:#CBD5E1; margin-top:6px; line-height:1.7;">
            • <b>流動性風向</b>：標普 500 與納指 100 維持強勢架構，市場承接力強勁。<br>
            • <b>賺錢效應判斷</b>：領頭羊板塊（半導體、AI 基礎設施、高動能科技）呈現良性輪動，符合 J Law 範式股票表現抗跌。
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_idx1, col_idx2, col_idx3 = st.columns(3)

    def display_index_panel(sym, title, df, col):
        if df is None or len(df) < 50:
            col.info(f"{sym} 數據加載中...")
            return
        c = df['Close']
        curr = float(c.iloc[-1])
        prev = float(c.iloc[-2])
        chg = ((curr - prev) / prev) * 100
        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma50
        atr14 = float((df['High'] - df['Low']).rolling(14).mean().iloc[-1])
        r1 = curr + (1.0 * atr14)
        s1 = curr - (1.0 * atr14)
        status_tag = "Stage 2 多頭" if curr > ema20 and ema20 > sma50 else "回踩支撐區"
        b_color = "badge-green" if curr > ema20 else "badge-gold"

        with col:
            st.markdown(f"""
            <div class="cyber-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:800; font-size:18px; color:#FFF;">{sym} · {title}</span>
                    <span class="badge {b_color}">{status_tag}</span>
                </div>
                <div style="font-size:30px; font-weight:800; font-family:'JetBrains Mono'; margin:10px 0; color:#FFF;">
                    ${curr:.2f} <span style="font-size:16px; color:{'#10B981' if chg>=0 else '#EF4444'};">({'+' if chg>=0 else ''}{chg:.2f}%)</span>
                </div>
                <div style="font-size:12px; color:#94A3B8; font-family:'JetBrains Mono'; line-height:1.8;">
                    • 20 EMA: <b style="color:#FFF;">${ema20:.2f}</b> ({'+' if curr>ema20 else ''}{(curr-ema20)/ema20*100:.1f}%)<br>
                    • 50 SMA: <b style="color:#FFF;">${sma50:.2f}</b> | 200 SMA: <b style="color:#FFF;">${sma200:.2f}</b><br>
                    • 阻力位 (R1): <b style="color:#38BDF8;">${r1:.2f}</b> | 防守位 (S1): <b style="color:#EF4444;">${s1:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    display_index_panel("QQQ", "納斯達克 100", qqq_df, col_idx1)
    display_index_panel("SPY", "標普 500 指數", spy_df, col_idx2)
    display_index_panel("DIA", "道瓊斯工業", dia_df, col_idx3)

# ----------------------------------------------------
# 模組 2: 核心持倉實戰情報
# ----------------------------------------------------
elif nav_selection == "🛡️ 核心持倉實戰情報 (Core Portfolio Tactics)":
    st.markdown("""
    <div class="section-header">
        <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
            🛡️ 核心自選持倉實戰情報 (TSLA · AAOI · NVDA · MU · BE · NBIS · DDOG)
        </h3>
        <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
            精確對齊富途指標參數：即時現價、RVOL量比、戰術型態、結構買入價與 2R/3R 止盈目標。
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_core = df_results[df_results['Symbol'].isin(CORE_PORTFOLIO_SYMBOLS)].copy()

    if not df_core.empty:
        st.dataframe(
            df_core[['Symbol', 'Price', 'Change', 'RS', 'Score', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R', 'RSI', 'RVOL']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Symbol": st.column_config.TextColumn("標的代碼"),
                "Price": st.column_config.NumberColumn("最新收市 ($)", format="$%.2f"),
                "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
                "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
                "RS": st.column_config.ProgressColumn("RS 強度", min_value=1, max_value=99, format="%d"),
                "Setup_Type": st.column_config.TextColumn("實戰戰術型態"),
                "Entry": st.column_config.NumberColumn("結構買入價 ($)", format="$%.2f"),
                "Entry_Diff": st.column_config.NumberColumn("現價距買點 (%)", format="%.2f%%"),
                "Stop": st.column_config.NumberColumn("防守止損 ($)", format="$%.2f"),
                "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
                "Target_2R": st.column_config.NumberColumn("第一目標 (2R)", format="$%.2f"),
                "Target_3R": st.column_config.NumberColumn("第二目標 (3R)", format="$%.2f"),
                "RSI": st.column_config.NumberColumn("RSI (14)", format="%.1f"),
                "RVOL": st.column_config.NumberColumn("成交量量比", format="%.2fx")
            }
        )

# ----------------------------------------------------
# 模組 3: 領頭羊即時機會庫
# ----------------------------------------------------
elif nav_selection == "01 // ⚡ 領頭羊即時機會庫 (J Law Alpha Screener)":
    st.markdown("""
    <div class="section-header">
        <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
            01 // ⚡ ALPHA SCREENER • J LAW 領頭羊即時機會庫
        </h3>
        <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
            全市場掃描排序庫：依據 Stage 2 均線多頭、加權百分位 RS ≥ 80、VCP 波動收窄蓄勢自動甄選。
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_qualified = df_results[df_results['Score'] >= 60].copy()
    if df_qualified.empty:
        df_qualified = df_results.head(6).copy()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("全網掃描股票數", f"{len(df_results)} 隻")
    m2.metric("💎 鑽石級 Alpha 領頭羊", f"{len(df_results[df_results['Rank'] == 'Diamond'])} 隻")
    m3.metric("🥇 黃金級優質突破股", f"{len(df_results[df_results['Rank'] == 'Gold'])} 隻")
    m4.metric("觀察池平均 RS 強度", f"{int(df_results['RS'].mean())} / 99")

    st.write("")

    card_cols = st.columns(min(4, len(df_qualified)))
    for i in range(min(4, len(df_qualified))):
        row_q = df_qualified.iloc[i]
        b_class = "badge-diamond" if row_q['Rank'] == 'Diamond' else "badge-gold"
        with card_cols[i]:
            st.markdown(f"""
            <div class="cyber-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="badge {b_class}">{row_q['Rank']} TIER</span>
                    <span style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8;">SCORE {row_q['Score']}</span>
                </div>
                <div style="font-size:30px; font-weight:800; font-family:'JetBrains Mono'; margin:8px 0; color:#FFF;">
                    {row_q['Symbol']}
                </div>
                <div style="font-size:16px; font-family:'JetBrains Mono'; font-weight:600; color:{'#10B981' if row_q['Change'] >= 0 else '#EF4444'};">
                    ${row_q['Price']:.2f} ({'+' if row_q['Change']>0 else ''}{row_q['Change']:.2f}%)
                </div>
                <div style="margin-top:8px; font-size:12px; color:#CBD5E1; font-family:'JetBrains Mono'; line-height:1.6;">
                    型態: <b style="color:#38BDF8;">{row_q['Setup_Type']}</b><br>
                    規劃買入價: <b style="color:#FFF;">${row_q['Entry']:.2f}</b><br>
                    防守止損價: <b style="color:#EF4444;">${row_q['Stop']:.2f} ({row_q['Stop_Pct']}%)</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with st.expander("📋 展開查看完整合格標的清單與量化指標", expanded=True):
        st.dataframe(
            df_qualified[['Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Stage2', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
                "RS": st.column_config.ProgressColumn("RS 相對強度", min_value=1, max_value=99, format="%d"),
                "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
                "Price": st.column_config.NumberColumn("現價 ($)", format="$%.2f"),
                "Setup_Type": st.column_config.TextColumn("戰術型態"),
                "Entry": st.column_config.NumberColumn("結構買入價 ($)", format="$%.2f"),
Entry": st.column_config.NumberColumn("結構買入價 ($)", format="$%.2f"),
                "Entry_Diff": st.column_config.NumberColumn("現價距買點 (%)", format="%.2f%%"),
                "Stop": st.column_config.NumberColumn("防守止損 ($)", format="$%.2f"),
                "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
                "Target_2R": st.column_config.NumberColumn("2R 止盈 ($)", format="$%.2f"),
                "Target_3R": st.column_config.NumberColumn("3R 止盈 ($)", format="$%.2f")
            }
        )

# ----------------------------------------------------
# 模組 4: 7 維技術形態診斷與圖表
# ----------------------------------------------------
elif nav_selection == "02 // 🔍 7 維技術診斷與圖表 (Deep Technical Radar)":
    st.markdown("""
    <div class="section-header">
        <h3 style="margin:0; color:#FFF; font-weight:800; letter-spacing:1px;">
            02 // 🔍 DEEP RADAR • 7 維技術形態診斷與 TRADINGVIEW 雷達
        </h3>
        <div style="font-size:13px; color:#94A3B8; margin-top:4px;">
            點解符合：逐項對齊 Stage 2 均線體系、RS 領頭羊、VCP 籌碼收窄與 DRSI 金叉狀態，實時載入 TradingView 互動圖表。
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_stock = st.selectbox("🎯 選擇要深度診斷的標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == selected_stock].iloc[0]

    c_r1, c_r2 = st.columns([1.1, 1.9])

    with c_r1:
        st.markdown(f"#### 📋 **{selected_stock}** J Law 7 維檢核清單")
        checklist = [
            ("1. Stage 2 趨勢範式", stock_row['Stage2'] == "是 (符合)", "價格 > 50SMA > 150SMA > 200SMA，長期均線向上，排除逆勢抄底垃圾股。"),
            ("2. RS 領頭羊地位 (≥80)", stock_row['RS'] >= 80, f"當前 RS Rating 為 {stock_row['RS']} 分，大幅跑贏 80% 以上市場標的。"),
            ("3. VCP 波動收窄 (Tightness)", any("VCP" in r for r in stock_row['Reasons']), "近期波幅 (ATR) 顯著收斂，主力鎖倉沉澱。"),
            ("4. DRSI 動能買點", "金叉" in stock_row['DRSI_Status'], f"DRSI 處於「{stock_row['DRSI_Status']}」，順勢起爆點成立。"),
            ("5. 20 EMA 關鍵支撐", abs(stock_row['Dist_20EMA']) <= 3.0, f"距離 20 EMA 僅 {stock_row['Dist_20EMA']}%，處於黃金回踩或起跳買區。"),
            ("6. 量能蓄勢與突破", stock_row['RVOL'] >= 1.2 or stock_row['RVOL'] < 0.8, f"相對量比 (RVOL) 為 {stock_row['RVOL']}x，量縮蓄勢或放量突破。"),
            ("7. 結構性買點設定", True, f"判定型態為「{stock_row['Setup_Type']}」，規劃買入價 ${stock_row['Entry']:.2f}，距現價 {stock_row['Entry_Diff']}%。")
        ]
        for title, passed, desc in checklist:
            s_icon = "✅" if passed else "⚠️"
            b_color = "#10B981" if passed else "#F59E0B"
            st.markdown(f"""
            <div style="background:rgba(18, 24, 38, 0.85); border-left:4px solid {b_color}; padding:10px 14px; margin-bottom:10px; border-radius:6px;">
                <div style="font-weight:700; color:#FFF; font-size:14px;">{s_icon} {title}</div>
                <div style="font-size:12px; color:#94A3B8; margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with c_r2:
        st.markdown(f"#### 📊 **{selected_stock}** TradingView 專業即時走勢圖")
        tv_code = f"""
        <div class="tradingview-widget-container" style="height:480px;width:100%;">
          <div id="tv_{selected_stock}" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{"autosize": true, "symbol": "{selected_stock}", "interval": "D", "timezone": "America/New_York", "theme": "dark", "style": "1", "locale": "zh_TW
