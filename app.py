import streamlit as st
import yfinance as yf
import pandas as pd

# --- 頁面設定 ---
st.set_page_config(page_title="J Law 冠軍選股神器", page_icon="🚀", layout="wide")

# --- 標題 ---
st.title("🚀 J Law (USIC 2024冠軍) 選股掃描器")
st.markdown("""
此工具自動掃描美股，尋找符合 **M.E.T.S. 策略** (趨勢向上 + 動能強勁 + 跑贏大盤) 的股票。
*數據來源: Yahoo Finance (免費延遲數據)*
""")

# --- 側邊欄 ---
st.sidebar.header("⚙️ 設定")
default_tickers = "NVDA, TSLA, PLTR, AMD, SMCI, META, MSFT, AAPL, COIN, MSTR, GOOG, AMZN, AVGO, COST, NET, CRWD"
tickers_input = st.sidebar.text_area("輸入股票代號 (逗號隔開)", default_tickers, height=200)

# --- 分析函數 ---
def analyze_stock(ticker):
    try:
        # 下載數據
        df = yf.download(ticker, period="1y", progress=False)
        if len(df) < 200: return None
        
        # 處理多層索引
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 取得數據
        close = float(df['Close'].iloc[-1])
        sma10 = float(df['Close'].rolling(10).mean().iloc[-1])
        sma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        sma50 = float(df['Close'].rolling(50).mean().iloc[-1])
        sma200 = float(df['Close'].rolling(200).mean().iloc[-1])
        
        # --- J Law 策略判斷 ---
        # 1. 長期趨勢: 價格 > 200MA
        trend = close > sma200
        # 2. 短期動能: 10MA > 20MA > 50MA (多頭排列)
        momentum = (sma10 > sma20) and (sma20 > sma50)
        
        # 3. 相對強度 (RS) - 過去3個月漲幅
        p3m = df['Close'].iloc[-63]
        rs_score = ((close - p3m) / p3m) * 100
        
        status = "✅ 強勢" if trend and momentum and rs_score > 0 else "❌ 觀察"
        
        return {
            "代號": ticker,
            "現價": round(close, 2),
            "狀態": status,
            "RS強度(3月)": f"{rs_score:.2f}%",
            "10MA": round(sma10, 2),
            "20MA": round(sma20, 2),
            "50MA": round(sma50, 2),
            "200MA": round(sma200, 2),
            "raw_rs": rs_score
        }
    except:
        return None

# --- 主按鈕 ---
if st.button("🔍 開始掃描", type="primary"):
    # 清理輸入的清單
    ticker_list = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    if not ticker_list:
        st.warning("請輸入股票代號！")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for i, ticker in enumerate(ticker_list):
            status_text.text(f"正在分析: {ticker}...")
            progress_bar.progress((i + 1) / len(ticker_list))
            
            res = analyze_stock(ticker)
            if res:
                results.append(res)
        
        progress_bar.empty()
        status_text.empty()
        
        if results:
            df = pd.DataFrame(results)
            # 排序：把強勢的放前面，RS高的放前面
            df = df.sort_values(by=["狀態", "raw_rs"], ascending=[True, False])
            # 移除排序用的 raw_rs 欄位，不顯示出來
            final_df = df.drop(columns=["raw_rs"])
            
            st.success(f"掃描完成！分析了 {len(ticker_list)} 支股票。")
            st.dataframe(final_df, use_container_width=True)
        else:
            st.error("無法取得數據，請檢查代號是否正確。")
