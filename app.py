import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import requests
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
# 1. 旗艦級 Cyberpunk CSS 注入
# ==========================================
def inject_cyber_theme():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* 頁面頂部微調 */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }

        .stApp {
            background: linear-gradient(180deg, rgba(6, 9, 14, 0.95) 0%, rgba(10, 14, 22, 0.98) 100%),
                        radial-gradient(circle at 50% 0%, rgba(232, 33, 39, 0.12) 0%, transparent 60%);
            background-attachment: fixed;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* 側邊欄玻璃擬態 */
        section[data-testid="stSidebar"] {
            background: rgba(11, 15, 25, 0.95) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        
        /* 導航 Radio 改造成 Cyber 膠囊按鈕 */
        div[role="radiogroup"] {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            background: rgba(15, 23, 42, 0.6) !important;
            padding: 6px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            margin-bottom: 18px !important;
        }
        div[role="radiogroup"] > label {
            background: rgba(22, 30, 46, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            color: #94A3B8 !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12.5px !important;
            font-weight: 600 !important;
        }
        div[role="radiogroup"] > label:hover {
            border-color: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 12px rgba(232, 33, 39, 0.3) !important;
        }
        /* 隱藏原生圓點 */
        div[role="radiogroup"] input[type="radio"] {
            display: none !important;
        }
        div[role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.35) 0%, rgba(18, 24, 38, 0.95) 100%) !important;
            border-color: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 15px rgba(232, 33, 39, 0.5) !important;
        }

        /* Cyberpunk 卡片與解決 Badge 折行 */
        .cyber-card {
            background: rgba(18, 24, 38, 0.82);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 16px 18px;
            margin-bottom: 14px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            min-height: 195px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .cyber-card:hover {
            border-color: rgba(232, 33, 39, 0.8);
            box-shadow: 0 12px 30px rgba(232, 33, 39, 0.25);
            transform: translateY(-2px);
        }
        
        /* 標籤防斷行修復 */
        .badge {
            display: inline-flex;
            align-items: center;
            white-space: nowrap;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
        }
        .badge-diamond { background: rgba(6, 182, 212, 0.2); color: #22D3EE; border: 1px solid #06B6D4; }
        .badge-gold { background: rgba(234, 179, 8, 0.2); color: #FACC15; border: 1px solid #EAB308; }
        .badge-green { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
        .badge-red { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
        .badge-cyan { background: rgba(14, 165, 233, 0.2); color: #38BDF8; border: 1px solid #0284C7; }
        .badge-tesla { background: rgba(232, 33, 39, 0.25); color: #FF6B6B; border: 1px solid #E82127; }

        /* Cyber HUD 指標面板 */
        .hud-metric-box {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 12px 16px;
            text-align: left;
            border-left: 3px solid #38BDF8;
        }
        .hud-metric-label {
            font-size: 11.5px;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
        }
        .hud-metric-val {
            font-size: 26px;
            font-weight: 800;
            color: #FFFFFF;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 4px;
        }

        .section-header {
            background: rgba(15, 23, 42, 0.85);
            border-left: 4px solid #E82127;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 14px;
            backdrop-filter: blur(10px);
        }
        
        .action-box {
            background: rgba(12, 17, 29, 0.95);
            border: 1px solid rgba(232, 33, 39, 0.35);
            border-radius: 8px;
            padding: 18px;
            font-family: 'JetBrains Mono', monospace;
        }

        .tesla-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(18, 24, 38, 0.85);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 14px 20px;
            margin-bottom: 14px;
            backdrop-filter: blur(16px);
        }

        @keyframes pulse-red {
            0% { box-shadow: 0 0 0 0 rgba(232, 33, 39, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(232, 33, 39, 0); }
            100% { box-shadow: 0 0 0 0 rgba(232, 33, 39, 0); }
        }
        .alert-banner {
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%);
            border: 1px solid #E82127;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 14px;
            animation: pulse-red 2s infinite;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 標的清單與表格配置
# ==========================================
CORE_PORTFOLIO_SYMBOLS = ["TSLA", "AAOI", "NVDA", "MU", "BE", "NBIS", "DDOG"]

DEFAULT_UNIVERSE = list(dict.fromkeys(CORE_PORTFOLIO_SYMBOLS + [
    "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "AVGO", "ARM", "QCOM", "TSM", "ASML", 
    "LRCX", "KLAC", "SMCI", "MRVL", "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", 
    "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI", "CEG", "VST", "GE", "CAT", 
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON"
]))

GRID_COLUMN_CONFIG = {
    "Symbol": st.column_config.TextColumn("代碼"),
    "Rank": st.column_config.TextColumn("評級"),
    "Price": st.column_config.NumberColumn("最新價 ($)", format="$%.2f"),
    "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
    "Score": st.column_config.ProgressColumn("評分", min_value=0, max_value=100, format="%d"),
    "RS": st.column_config.ProgressColumn("RS 強度", min_value=1, max_value=99, format="%d"),
    "Setup_Type": st.column_config.TextColumn("戰術型態"),
    "Entry": st.column_config.NumberColumn("樞紐買入 ($)", format="$%.2f"),
    "Entry_Diff": st.column_config.NumberColumn("距買點 (%)", format="%.2f%%"),
    "Stop": st.column_config.NumberColumn("結構止損 ($)", format="$%.2f"),
    "Stop_Pct": st.column_config.NumberColumn("止損幅 (%)", format="%.2f%%"),
    "Target_2R": st.column_config.NumberColumn("第一目標 (2R)", format="$%.2f"),
    "Target_3R": st.column_config.NumberColumn("第二目標 (3R)", format="$%.2f"),
    "RVOL": st.column_config.NumberColumn("量比", format="%.2fx")
}

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
            else:
                df = raw_data.copy()
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
# 4. 核心量化評分與定價邏輯
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

        # 1. Stage 2 範式檢驗
        is_stage2 = False
        if curr_price > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 15
            if sma200 >= sma200_20d_ago: score += 5
            if dist_h52 >= -25.0 and dist_l52 >= 25.0:
                score += 5
                is_stage2 = True
                reasons.append("Stage 2 完美多頭範式")
        elif curr_price > sma50:
            score += 8
            if dist_h52 >= -20.0: reasons.append("50SMA 上方強勢整理")

        # 2. RS 評級計算
        def perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        stock_w = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, min(252, len(c)-1))
        spy_w = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_rating = int(np.clip(50 + ((stock_w - spy_w) * 100 * 1.5), 1, 99))

        if rs_rating >= 80:
            score += 25
            reasons.append(f"領頭羊 (RS {rs_rating})")
        elif rs_rating >= 65:
            score += 18
            reasons.append(f"強於大盤 (RS {rs_rating})")
        elif rs_rating >= 50: score += 10

        # 3. VCP 波動收斂檢測
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 10
            reasons.append("VCP 波動收窄蓄勢")
        if float(c.iloc[-5:].std() / curr_price) < 0.025:
            score += 5
            reasons.append("緊密收市 (Tight Closes)")

        # 4. DRSI 隨機強弱買點
        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss.replace(0, 1e-9)))))
        stoch_k = 100 * (rsi - rsi.rolling(14).min()) / ((rsi.rolling(14).max() - rsi.rolling(14).min()).replace(0, 1e-9))
        stoch_d = stoch_k.rolling(3).mean()
        k_val, d_val = float(stoch_k.iloc[-1]), float(stoch_d.iloc[-1])
        prev_k, prev_d = float(stoch_k.iloc[-2]), float(stoch_d.iloc[-2])

        drsi_status = "中性"
        is_drsi_bullish = False
        if prev_k <= prev_d and k_val > d_val:
            is_drsi_bullish = True
            if k_val < 35:
                score += 15
                drsi_status = "超賣金叉"
                reasons.append("DRSI 超賣金叉")
            else:
                score += 12
                drsi_status = "多頭金叉"
                reasons.append("DRSI 多頭金叉")
        elif k_val > d_val:
            score += 8
            drsi_status = "多頭維持"
        elif k_val < 25: score += 6

        # 5. 20 EMA 支撐位
        dist_ema20 = ((curr_price - ema20) / ema20) * 100
        if 0 <= dist_ema20 <= 2.5:
            score += 10
            reasons.append("回踩 20 EMA")
        elif -2.0 <= dist_ema20 < 0:
            score += 6
            reasons.append("回測 20 EMA")
        elif 2.5 < dist_ema20 <= 6.0: score += 5

        # 6. 量比 RVOL
        v_50 = float(v.rolling(50).mean().iloc[-1])
        rvol = float(v.iloc[-1]) / (v_50 if v_50 > 0 else 1)
        if change_pct > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"放量突破 ({rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("量能乾涸 (VDU)")
        else: score += 4

        total_score = int(np.clip(score, 0, 100))
        rank = "Diamond" if (total_score >= 80 and is_stage2) else ("Gold" if total_score >= 65 else ("Silver" if total_score >= 50 else "Bronze"))

        # 7. 結構點位計算
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

        is_all_rules_met = (is_stage2 and rs_rating >= 80 and is_drsi_bullish and abs(entry_diff) <= 3.0)

        return {
            "Symbol": symbol,
            "Rank": rank,
            "Score": total_score,
            "Price": round(curr_price, 2),
            "Change": round(change_pct, 2),
            "RS": rs_rating,
            "Stage2": "符合" if is_stage2 else "否",
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
# 5. 主應用渲染
# ==========================================
inject_cyber_theme()

with st.sidebar:
    st.markdown("## ⚡ TESLA CYBER")
    st.caption("Autonomous Swing Trading Desk")
    st.markdown("---")

    st.markdown("""
    <div style="background:rgba(232, 33, 39, 0.1); border:1px solid #E82127; border-radius:6px; padding:12px; margin-bottom:14px;">
        <div style="font-weight:700; color:#FF6B6B; font-size:12.5px;">🤖 OPTIMUS QUANT CORE</div>
        <div style="font-size:11px; color:#CBD5E1; margin-top:3px; line-height:1.5;">
            已啟動形態測算引擎，全自動對齊富途指標、計算結構性樞紐點位。
        </div>
    </div>
    """, unsafe_allow_html=True)

    custom_add = st.text_area("增補美股代碼 (逗號隔開)", value="")
    custom_tickers = [x.strip().upper() for x in custom_add.split(",") if x.strip()]
    full_scan_list = list(dict.fromkeys(DEFAULT_UNIVERSE + custom_tickers))
    st.caption(f"全天候監測標的總數：**{len(full_scan_list)}** 隻")
    
    if st.button("⚡ 重新掃描市場 (RE-SCAN)"):
        st.session_state.pop('scan_data', None)
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔔 Telegram 推播配置")
    tg_token = st.text_input("Bot Token", type="password", placeholder="填入 Telegram Bot Token")
    tg_chat_id = st.text_input("Chat ID", placeholder="填入 Chat ID")
    
    if tg_token and tg_chat_id:
        if st.button("📤 發送測試通知"):
            try:
                msg = "⚡ [Tesla Cyber Terminal] 系統連線成功！即時突破信號已就緒。"
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                r = requests.post(url, json={"chat_id": tg_chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=5)
                if r.status_code == 200: st.success("發送成功！")
                else: st.error("發送失敗，請確認 Token 及 Chat ID")
            except Exception as e:
                st.error(f"連線異常: {e}")

# 獲取市場數據
if 'scan_data' not in st.session_state:
    with st.spinner("⚡ Optimus 正在執行量化計算，同步美股行情中..."):
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

# 頂部 Cyber Banner
st.markdown("""
<div class="tesla-banner">
    <div>
        <span style="font-size:22px; font-weight:900; font-family:'JetBrains Mono'; color:#FFF; letter-spacing:1px;">
            ⚡ J LAW ALPHA HUNTER <span style="color:#E82127;">// TERMINAL</span>
        </span>
        <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">
            INSTITUTIONAL RESEARCH & SWING TRADING • POWERED BY OPTIMUS QUANT CORE
        </div>
    </div>
    <div style="display:flex; gap:8px;">
        <span class="badge badge-tesla">CYBERCAB ONLINE</span>
        <span class="badge badge-diamond">OPTIMUS V3</span>
    </div>
</div>
""", unsafe_allow_html=True)

if df_results.empty:
    st.error("暫未獲取到市場數據，請檢查網絡連線或點擊側邊欄重新掃描。")
    st.stop()

# 警報橫幅
perfect_matches = df_results[df_results['All_Rules_Met'] == True] if ('All_Rules_Met' in df_results.columns) else pd.DataFrame()
if not perfect_matches.empty:
    alert_symbols = ", ".join(perfect_matches['Symbol'].tolist())
    st.markdown(f"""
    <div class="alert-banner">
        <div style="font-size:15px; font-weight:800; color:#FF4D4D;">
            🚨 OPTIMUS 實時強勢警報觸發！完全符合 J LAW 7 大核心規則標的：<span style="color:#FFF; font-size:17px;">{alert_symbols}</span>
        </div>
        <div style="font-size:11.5px; color:#E2E8F0; margin-top:3px;">
            達成條件：Stage 2 多頭 · RS ≥ 80 · DRSI 金叉 · 現價距規劃買入點 ≤ 3%！
        </div>
    </div>
    """, unsafe_allow_html=True)

# 導航（透過 CSS 隱藏 Radio 圓點並自適應膠囊排版）
nav_selection = st.radio(
    "導航模式",
    [
        "🌐 大盤宏觀體檢",
        "🛡️ 核心持倉情報",
        "01 // ⚡ 領頭羊即時機會庫",
        "02 // 🔍 7 維技術診斷雷達",
        "03 // 🎯 1% 風險下單執行矩陣"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ----------------------------------------------------
# 模組 1: 大盤宏觀體檢
# ----------------------------------------------------
if nav_selection == "🌐 大盤宏觀體檢":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800; letter-spacing:0.5px;">
            🌐 每日美股市場追蹤 • 三大官方基準指數與體檢
        </h4>
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
    macro_verdict = "【強勢多頭・主升波段】：科技權重與大盤均站穩 20 EMA 上方，資金擴散，可積極佈局高勝率樞紐。" if is_healthy else "【震盪整理・防守為王】：指數測試關鍵均線支撐，市場分化，嚴格控制倉位，嚴禁盲目追高。"

    st.markdown(f"""
    <div class="cyber-card" style="min-height:auto; border-left:4px solid {'#10B981' if is_healthy else '#F59E0B'};">
        <div style="font-size:15px; font-weight:700; color:{'#10B981' if is_healthy else '#F59E0B'};">
            📊 置頂定調結論：{macro_verdict}
        </div>
        <div style="font-size:12.5px; color:#CBD5E1; margin-top:6px; line-height:1.6;">
            • <b>流動性風向</b>：標普 500 與納指 100 維持支撐架構，承接力穩定。<br>
            • <b>賺錢效應判斷</b>：領頭羊板塊（半導體、AI 硬件、雲計算）呈現良性輪動。
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_idx1, col_idx2, col_idx3 = st.columns(3)

    def display_index_panel(sym, title, df, col):
        if df is None or len(df) < 50:
            col.info(f"{sym} 數據加載中...")
            return
        c = df['Close']
        curr, prev = float(c.iloc[-1]), float(c.iloc[-2])
        chg = ((curr - prev) / prev) * 100
        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma50
        atr14 = float((df['High'] - df['Low']).rolling(14).mean().iloc[-1])
        r1, s1 = curr + atr14, curr - atr14
        status_tag = "Stage 2 多頭" if curr > ema20 and ema20 > sma50 else "回踩測試"
        b_color = "badge-green" if curr > ema20 else "badge-gold"

        with col:
            st.markdown(f"""
            <div class="cyber-card" style="min-height:auto;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:800; font-size:16px; color:#FFF;">{sym} · {title}</span>
                    <span class="badge {b_color}">{status_tag}</span>
                </div>
                <div style="font-size:26px; font-weight:800; font-family:'JetBrains Mono'; margin:8px 0; color:#FFF;">
                    ${curr:.2f} <span style="font-size:15px; color:{'#10B981' if chg>=0 else '#EF4444'};">({'+' if chg>=0 else ''}{chg:.2f}%)</span>
                </div>
                <div style="font-size:12px; color:#94A3B8; font-family:'JetBrains Mono'; line-height:1.7;">
                    • 20 EMA: <b style="color:#FFF;">${ema20:.2f}</b><br>
                    • 50 SMA: <b style="color:#FFF;">${sma50:.2f}</b> | 200 SMA: <b style="color:#FFF;">${sma200:.2f}</b><br>
                    • 阻力 (R1): <b style="color:#38BDF8;">${r1:.2f}</b> | 支撐 (S1): <b style="color:#EF4444;">${s1:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    display_index_panel("QQQ", "納斯達克 100", qqq_df, col_idx1)
    display_index_panel("SPY", "標普 500", spy_df, col_idx2)
    display_index_panel("DIA", "道瓊斯工業", dia_df, col_idx3)

# ----------------------------------------------------
# 模組 2: 核心持倉情報
# ----------------------------------------------------
elif nav_selection == "🛡️ 核心持倉情報":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            🛡️ 核心持倉戰術情報 (TSLA · AAOI · NVDA · MU · BE · NBIS · DDOG)
        </h4>
    </div>
    """, unsafe_allow_html=True)

    df_core = df_results[df_results['Symbol'].isin(CORE_PORTFOLIO_SYMBOLS)].copy()
    if not df_core.empty:
        st.dataframe(
            df_core[['Symbol', 'Rank', 'Price', 'Change', 'RS', 'Score', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R', 'RVOL']],
            use_container_width=True,
            hide_index=True,
            column_config=GRID_COLUMN_CONFIG
        )

# ----------------------------------------------------
# 模組 3: 領頭羊即時機會庫 (含過濾 Bar)
# ----------------------------------------------------
elif nav_selection == "01 // ⚡ 領頭羊即時機會庫":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            01 // ⚡ ALPHA SCREENER • J LAW 領頭羊即時機會庫
        </h4>
    </div>
    """, unsafe_allow_html=True)

    # 4 塊 Cyber HUD 指標
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="hud-metric-box">
            <div class="hud-metric-label">SCAN POOL</div>
            <div class="hud-metric-val">{len(df_results)} <span style="font-size:14px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="hud-metric-box" style="border-left-color:#06B6D4;">
            <div class="hud-metric-label">DIAMOND ALPHA</div>
            <div class="hud-metric-val" style="color:#22D3EE;">{len(df_results[df_results['Rank'] == 'Diamond'])} <span style="font-size:14px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="hud-metric-box" style="border-left-color:#FACC15;">
            <div class="hud-metric-label">GOLD TIER</div>
            <div class="hud-metric-val" style="color:#FACC15;">{len(df_results[df_results['Rank'] == 'Gold'])} <span style="font-size:14px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="hud-metric-box" style="border-left-color:#10B981;">
            <div class="hud-metric-label">AVERAGE RS</div>
            <div class="hud-metric-val" style="color:#34D399;">{int(df_results['RS'].mean())} <span style="font-size:14px; color:#94A3B8;">/ 99</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 快捷篩選區
    f_c1, f_c2 = st.columns([1.5, 2.5])
    with f_c1:
        filter_tier = st.selectbox("🎯 評級篩選", ["全部評級", "只睇 💎 Diamond", "只睇 💎 Diamond + 🥇 Gold"], index=0)
    with f_c2:
        only_near_entry = st.checkbox("🎯 只顯示現價距離買入點 ≤ 3%（隨時可啟動）", value=False)

    df_filtered = df_results.copy()
    if filter_tier == "只睇 💎 Diamond":
        df_filtered = df_filtered[df_filtered['Rank'] == 'Diamond']
    elif filter_tier == "只睇 💎 Diamond + 🥇 Gold":
        df_filtered = df_filtered[df_filtered['Rank'].isin(['Diamond', 'Gold'])]

    if only_near_entry:
        df_filtered = df_filtered[df_filtered['Entry_Diff'].abs() <= 3.0]

    # 機會卡片展示
    display_cards = df_filtered.head(4)
    if not display_cards.empty:
        card_cols = st.columns(len(display_cards))
        for i, (_, row_q) in enumerate(display_cards.iterrows()):
            b_class = "badge-diamond" if row_q['Rank'] == 'Diamond' else "badge-gold"
            with card_cols[i]:
                st.markdown(f"""
                <div class="cyber-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="badge {b_class}">{row_q['Rank']} TIER</span>
                            <span style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8; font-size:13px;">SCORE {row_q['Score']}</span>
                        </div>
                        <div style="font-size:26px; font-weight:800; font-family:'JetBrains Mono'; margin:6px 0 2px 0; color:#FFF;">
                            {row_q['Symbol']}
                        </div>
                        <div style="font-size:15px; font-family:'JetBrains Mono'; font-weight:600; color:{'#10B981' if row_q['Change'] >= 0 else '#EF4444'};">
                            ${row_q['Price']:.2f} ({'+' if row_q['Change']>0 else ''}{row_q['Change']:.2f}%)
                        </div>
                    </div>
                    <div style="margin-top:10px; font-size:11.5px; color:#CBD5E1; font-family:'JetBrains Mono'; line-height:1.6; border-top:1px solid rgba(255,255,255,0.06); padding-top:8px;">
                        型態: <span style="color:#38BDF8;">{row_q['Setup_Type']}</span><br>
                        樞紐買點: <b style="color:#FFF;">${row_q['Entry']:.2f}</b><br>
                        防守止損: <b style="color:#EF4444;">${row_q['Stop']:.2f} ({row_q['Stop_Pct']}%)</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("當前篩選條件下無符合的標的。")

    with st.expander("📋 展開查看完整合格標的清單", expanded=True):
        st.dataframe(
            df_filtered[['Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Stage2', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R']],
            use_container_width=True,
            hide_index=True,
            column_config=GRID_COLUMN_CONFIG
        )

# ----------------------------------------------------
# 模組 4: 7 維技術診斷雷達
# ----------------------------------------------------
elif nav_selection == "02 // 🔍 7 維技術診斷雷達":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            02 // 🔍 DEEP RADAR • 7 維技術形態診斷與 TRADINGVIEW 雷達
        </h4>
    </div>
    """, unsafe_allow_html=True)

    selected_stock = st.selectbox("🎯 選擇要深度診斷的標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == selected_stock].iloc[0]

    c_r1, c_r2 = st.columns([1.1, 1.9])

    with c_r1:
        st.markdown(f"#### 📋 **{selected_stock}** J Law 7 維檢核")
        checklist = [
            ("1. Stage 2 趨勢範式", stock_row['Stage2'] == "符合", "股價 > 50SMA > 150SMA > 200SMA，均線呈現多頭排列。"),
            ("2. RS 領頭羊地位 (≥80)", stock_row['RS'] >= 80, f"當前 RS 為 {stock_row['RS']} 分，大幅跑贏 80% 以上大盤股票。"),
            ("3. VCP 波動收窄", any("VCP" in r for r in stock_row['Reasons']), "ATR 收窄蓄勢，籌碼逐步鎖定。"),
            ("4. DRSI 動能買點", "金叉" in stock_row['DRSI_Status'], f"DRSI 處於「{stock_row['DRSI_Status']}」，動能轉強。"),
            ("5. 20 EMA 動態支撐", abs(stock_row['Dist_20EMA']) <= 3.0, f"距 20 EMA 僅 {stock_row['Dist_20EMA']}%，處於黃金回踩買區。"),
            ("6. 量能蓄勢與突破", stock_row['RVOL'] >= 1.2 or stock_row['RVOL'] < 0.8, f"相對量比 (RVOL) 為 {stock_row['RVOL']}x。"),
            ("7. 結構點位設定", True, f"型態為「{stock_row['Setup_Type']}」，規劃買入價 ${stock_row['Entry']:.2f}。")
        ]
        for title, passed, desc in checklist:
            s_icon = "✅" if passed else "⚠️"
            b_color = "#10B981" if passed else "#F59E0B"
            st.markdown(f"""
            <div style="background:rgba(18, 24, 38, 0.85); border-left:3px solid {b_color}; padding:8px 12px; margin-bottom:8px; border-radius:4px;">
                <div style="font-weight:700; color:#FFF; font-size:13px;">{s_icon} {title}</div>
                <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with c_r2:
        tv_code = f"""
        <div class="tradingview-widget-container" style="height:480px;width:100%;">
          <div id="tv_{selected_stock}" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{"autosize": true, "symbol": "{selected_stock}", "interval": "D", "timezone": "America/New_York", "theme": "dark", "style": "1", "locale": "zh_TW", "toolbar_bg": "#0B0E14", "enable_publishing": false, "container_id": "tv_{selected_stock}"}});
          </script>
        </div>
        """
        components.html(tv_code, height=490)

# ----------------------------------------------------
# 模組 5: 1% 風險下單執行矩陣 (含券商指令生成)
# ----------------------------------------------------
elif nav_selection == "03 // 🎯 1% 風險下單執行矩陣":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            03 // 🎯 EXECUTION MATRIX • 樞紐買點、階梯止盈與 1% 倉位精算
        </h4>
    </div>
    """, unsafe_allow_html=True)

    target_calc_sym = st.selectbox("選擇計算下單標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == target_calc_sym].iloc[0]

    inp_c1, inp_c2, inp_c3 = st.columns(3)
    with inp_c1:
        account_capital = st.number_input("賬戶總資產 ($)", min_value=1000, max_value=10000000, value=50000, step=5000)
    with inp_c2:
        risk_pct = st.slider("單筆最大承受風險 (%)", min_value=0.5, max_value=2.5, value=1.0, step=0.1)
    with inp_c3:
        max_pos_cap = st.slider("單一持倉上限 (%)", min_value=10, max_value=40, value=25, step=5)

    max_risk_dollars = account_capital * (risk_pct / 100.0)
    target_entry = stock_row['Entry']
    target_stop = stock_row['Stop']
    target_risk_per_share = stock_row['Risk_Per_Share']
    target_stop_pct = stock_row['Stop_Pct']
    target_2r = stock_row['Target_2R']
    target_3r = stock_row['Target_3R']

    calc_shares = int(max_risk_dollars / target_risk_per_share) if target_risk_per_share > 0 else 0
    total_pos_cost = calc_shares * target_entry
    max_allowed_cost = account_capital * (max_pos_cap / 100.0)
    
    adj_msg = ""
    if total_pos_cost > max_allowed_cost:
        calc_shares = int(max_allowed_cost / target_entry)
        total_pos_cost = calc_shares * target_entry
        adj_msg = f"⚠️ 受限於持倉上限 ({max_pos_cap}%)，股數已自動調整為安全上限。"

    pos_pct_of_capital = (total_pos_cost / account_capital) * 100

    plan_c1, plan_c2 = st.columns(2)

    with plan_c1:
        st.markdown(f"""
        <div class="action-box">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h4 style="margin:0; color:#38BDF8;">🎯 {target_calc_sym} 結構進出場點位</h4>
                <span class="badge badge-cyan">{stock_row['Setup_Type']}</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🔵 樞紐進場 (Entry):</span><br>
                    <b style="font-size:20px; color:#38BDF8;">${target_entry:.2f}</b><br>
                    <span style="font-size:10.5px; color:#CBD5E1;">現價: ${stock_row['Price']:.2f}</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🔴 結構止損 (Stop):</span><br>
                    <b style="font-size:20px; color:#EF4444;">${target_stop:.2f} ({target_stop_pct}%)</b><br>
                    <span style="font-size:10.5px; color:#EF4444;">每股風險: ${target_risk_per_share:.2f}</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🟢 1st 目標 (2R):</span><br>
                    <b style="font-size:20px; color:#10B981;">${target_2r:.2f}</b><br>
                    <span style="font-size:10.5px; color:#6EE7B7;">平半倉 + 止損移至成本</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🌟 2nd 目標 (3R+):</span><br>
                    <b style="font-size:20px; color:#F59E0B;">${target_3r:.2f}</b><br>
                    <span style="font-size:10.5px; color:#FCD34D;">沿 20 EMA 順勢移停</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with plan_c2:
        st.markdown(f"""
        <div class="action-box" style="border-color: rgba(16, 185, 129, 0.4);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h4 style="margin:0; color:#10B981;">🛡️ 1% 風險倉位精算</h4>
                <span class="badge badge-green">風控鎖定中</span>
            </div>
            <div style="line-height:1.9; font-size:13.5px;">
                • 賬戶總額: <b>${account_capital:,.2f}</b><br>
                • 最大承擔虧損 (1R): <b style="color:#EF4444;">${max_risk_dollars:,.2f}</b> ({risk_pct}%)<br>
                • 每股風險金: <b>${target_risk_per_share:.2f}</b><br>
                <hr style="border:0; border-top:1px solid rgba(255,255,255,0.08); margin:8px 0;">
                • <b>推薦進場股數:</b> <span style="font-size:22px; color:#10B981; font-weight:800;">{calc_shares} 股</span><br>
                • <b>預計持倉成本:</b> <b>${total_pos_cost:,.2f}</b> ({pos_pct_of_capital:.1f}% 倉位)<br>
                • <b>觸發止損虧損:</b> <b style="color:#EF4444;">-${calc_shares * target_risk_per_share:,.2f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if adj_msg:
        st.info(adj_msg)

    # 券商下單指令一鍵複製區
    st.write("")
    order_script = (
        f"【富途 / IB 下單草稿 - {target_calc_sym}】\n"
        f"買入指令: 限價單 (Limit) @ ${target_entry:.2f} | 數量: {calc_shares} 股\n"
        f"條件止損: 止損單 (Stop Loss) @ ${target_stop:.2f}\n"
        f"止盈目標: 2R 止盈 @ ${target_2r:.2f} (半倉: {calc_shares // 2} 股) | 3R 止盈 @ ${target_3r:.2f}"
    )
    st.text_area("📋 券商下單指令草稿 (可直接複製至交易筆記或下單窗口)", value=order_script, height=105)
