import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. 系統設置
# ==========================================
st.set_page_config(page_title="J Law 自動戰術掃描器", layout="wide", page_icon="🦅")

st.title("🦅 J Law 冠軍操盤室：自動戰術掃描系統")
st.markdown("""
**系統邏輯**：此程式會自動遍歷股票清單，尋找符合 **M.E.T.A.** 標準的股票。
1.  **趨勢向上** (Price > 200MA)
2.  **回測支撐** (Price touching 10MA or 20MA)
3.  **成交量縮** (Volume < Average Volume)
""")

# ==========================================
# 2. 數據源與股票池
# ==========================================
def get_nasdaq_100():
    # 這裡列出部分 Nasdaq 100 及熱門股，為了速度演示，您可以自行增加
    return [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", 
        "AMD", "NFLX", "PEP", "CSCO", "TMUS", "QCOM", "TXN", "AMGN", "INTU", 
        "INTC", "ISRG", "HON", "AMAT", "BKNG", "SBUX", "MDLZ", "ADP", "GILD", 
        "LRCX", "ADI", "VRTX", "REGN", "PANW", "MU", "SNPS", "KLAC", "CDNS", 
        "CHTR", "CSX", "MAR", "PYPL", "ASML", "MNST", "ORLY", "ODFL", "LULU", 
        "MSTR", "COIN", "PLTR", "SOFI", "AFRM", "UPST", "DKNG", "HOOD", "RBLX",
        "UBER", "ABNB", "DASH", "NET", "DDOG", "ZS", "CRWD", "TTD", "APP"
    ]

# ==========================================
# 3. J Law 核心篩選演算法
# ==========================================
def check_jlaw_criteria(ticker, df):
    try:
        # 確保數據足夠計算 200MA
        if len(df) < 200:
            return None

        # 取得最新數據
        current_close = df['Close'].iloc[-1]
        current_low = df['Low'].iloc[-1]
        current_volume = df['Volume'].iloc[-1]
        
        # 計算均線
        sma10 = df['Close'].rolling(window=10).mean().iloc[-1]
        sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        sma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # 計算 50日平均成交量
        avg_vol_50 = df['Volume'].rolling(window=50).mean().iloc[-1]

        # --- J LAW 判斷邏輯 ---
        
        # 條件 1: 大趨勢必須向上 (Stage 2)
        # 股價 > 200MA 且 50MA > 200MA
        is_uptrend = current_close > sma200 and sma50 > sma200
        
        if not is_uptrend:
            return None # 趨勢不對，直接過濾掉

        # 條件 2: 量能枯竭 (Volume Dry Up)
        # 今日成交量 < 平均成交量的 85% (或者是更嚴格的 75%)
        # 這代表回調時沒有賣壓
        is_volume_dry = current_volume < (avg_vol_50 * 0.9) # 稍微放寬到 90% 以便捕捉更多機會

        # 條件 3: 網球行為 (Tennis Ball Action) - 回測支撐
        # 股價回落到 10MA 或 20MA 附近 (誤差範圍內)
        
        setup_type = ""
        
        # 檢查是否回測 10MA (強勢股)
        # 邏輯：最低價觸及 10MA 附近 (正負 1.5%) 且 收盤價最好在 10MA 之上或附近
        dist_10 = abs(current_low - sma10) / sma10
        if dist_10 <= 0.015 and current_close >= (sma10 * 0.99):
            setup_type = "🔥 10MA 超強勢回調"
        
        # 檢查是否回測 20MA (標準波段)
        dist_20 = abs(current_low - sma20) / sma20
        if not setup_type and dist_20 <= 0.015 and current_close >= (sma20 * 0.99):
            setup_type = "🟡 20MA 標準回調"

        # 最終判斷
        if setup_type and is_volume_dry:
            return {
                "代號": ticker,
                "現價": round(current_close, 2),
                "策略": setup_type,
                "成交量狀態": f"{int((current_volume/avg_vol_50)*100)}% (量縮)",
                "MA10": round(sma10, 2),
                "MA20": round(sma20, 2),
                "RSI": round(compute_rsi(df), 2)
            }
            
    except Exception as e:
        return None
    
    return None

def compute_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]

# ==========================================
# 4. 前端顯示與控制
# ==========================================

# 側邊欄
st.sidebar.header("🔍 掃描設定")
scan_list = st.sidebar.radio("選擇掃描範圍", ["Nasdaq 精選 (速度快)", "自定義股票池"])

custom_tickers = ""
if scan_list == "自定義股票池":
    custom_tickers = st.sidebar.text_area("輸入股票代碼 (逗號分隔)", "PLTR, SOFI, COIN, MARA, RIOT, TSLA")

start_btn = st.sidebar.button("🚀 啟動 J Law 戰術掃描", type="primary")

# 主畫面
if start_btn:
    # 決定要掃描的列表
    target_tickers = []
    if scan_list == "Nasdaq 精選 (速度快)":
        target_tickers = get_nasdaq_100()
    else:
        target_tickers = [x.strip().upper() for x in custom_tickers.split(',')]
    
    if not target_tickers:
        st.error("股票列表為空！")
    else:
        st.write(f"正在掃描 {len(target_tickers)} 隻股票，請稍候...")
        
        # 進度條
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 批量下載數據 (大幅提升速度)
        # 使用 threads 加速
        data = yf.download(target_tickers, period="1y", group_by='ticker', threads=True, progress=False)
        
        valid_setups = []
        
        for i, ticker in enumerate(target_tickers):
            # 更新進度
            progress = (i + 1) / len(target_tickers)
            progress_bar.progress(progress)
            status_text.text(f"分析中: {ticker} ...")
            
            try:
                # 處理 yfinance 多股票數據結構
                if len(target_tickers) > 1:
                    df = data[ticker].dropna()
                else:
                    df = data.dropna()
                
                if not df.empty:
                    result = check_jlaw_criteria(ticker, df)
                    if result:
                        valid_setups.append(result)
            except Exception as e:
                continue
                
        progress_bar.empty()
        status_text.empty()
        
        # 顯示結果
        if valid_setups:
            st.success(f"🎯 掃描完成！發現 {len(valid_setups)} 隻符合 J Law 標準的股票。")
            
            # 轉換為 DataFrame 展示
            df_results = pd.DataFrame(valid_setups)
            st.dataframe(df_results, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📊 戰術圖表檢視")
            
            # 讓用戶選擇查看哪一隻
            selected_stock = st.selectbox("選擇股票查看詳細圖表", df_results['代號'].tolist())
            
            if selected_stock:
                # 獲取該股票數據畫圖
                if len(target_tickers) > 1:
                    stock_data = data[selected_stock]
                else:
                    stock_data = data
                
                # 使用 Plotly 畫交互式 K 線圖
                fig = go.Figure()
                
                # K線
                fig.add_trace(go.Candlestick(x=stock_data.index,
                                open=stock_data['Open'],
                                high=stock_data['High'],
                                low=stock_data['Low'],
                                close=stock_data['Close'],
                                name='Price'))
                
                # 均線
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].rolling(10).mean(), line=dict(color='orange', width=1.5), name='10 MA'))
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].rolling(20).mean(), line=dict(color='purple', width=1.5), name='20 MA'))
                fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'].rolling(50).mean(), line=dict(color='blue', width=1), name='50 MA'))

                fig.update_layout(
                    title=f"{selected_stock} - J Law 戰術圖表",
                    yaxis_title="Price",
                    xaxis_rangeslider_visible=False,
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 顯示 J Law 的操作提示
                row = df_results[df_results['代號'] == selected_stock].iloc[0]
                st.info(f"""
                **💡 J Law 操作提示：**
                這隻股票目前處於 **{row['策略']}** 狀態。
                1. **確認**：請等待股價**突破今日高點**才進場 (Confirmation)。
                2. **止損**：設定在今日低點下方。
                3. **量能**：今日成交量為均量的 {row['成交量狀態']}，顯示賣壓減輕。
                """)
                
        else:
            st.warning("⚠️ 掃描完成，但沒有發現符合嚴格標準的股票。這可能代表目前市場處於調整期，不適合積極做多。")

else:
    st.info("👈 請點擊左側「啟動 J Law 戰術掃描」按鈕開始。")
