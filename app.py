import streamlit as st
import yfinance as yf
import pandas as pd

# --- 新增功能：自動獲取股票名單 ---
@st.cache_data
def get_index_tickers(index_name):
    try:
        if index_name == "S&P 500":
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            # Wikipedia S&P 500 通常係第 1 張表
            df = pd.read_html(url)[0] 
            return df['Symbol'].tolist()
            
        elif index_name == "Nasdaq 100":
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            # Wikipedia Nasdaq 100 表格位置可能會變，所以搵包含 'Ticker' 嗰張表
            tables = pd.read_html(url)
            for table in tables:
                if 'Ticker' in table.columns:
                    return table['Ticker'].tolist()
            st.error("搵唔到 Nasdaq 100 名單，請重試。")
            return []
    except Exception as e:
        st.error(f"獲取名單時發生錯誤: {e}")
        return []

# --- 側邊欄設定 ---
st.sidebar.header("⚙️ 設定")

# 俾用家揀模式
input_method = st.sidebar.radio(
    "選擇股票來源：",
    ("手動輸入", "S&P 500 (全成份股)", "Nasdaq 100 (全成份股)")
)

tickers = []

if input_method == "手動輸入":
    default_tickers = "NVDA, TSLA, PLTR, AMD, SMCI, META, MSFT, AAPL, COIN, MSTR, GOOG, AMZN, AVGO, COST, NET, CRWD"
    user_input = st.sidebar.text_area("輸入股票代號 (逗號隔開)", value=default_tickers, height=150)
    if user_input:
        tickers = [x.strip().upper() for x in user_input.split(',')]

elif input_method == "S&P 500 (全成份股)":
    st.sidebar.info("正在從 Wikipedia 下載 S&P 500 名單...")
    tickers = get_index_tickers("S&P 500")
    st.sidebar.success(f"已載入 {len(tickers)} 隻股票")

elif input_method == "Nasdaq 100 (全成份股)":
    st.sidebar.info("正在從 Wikipedia 下載 Nasdaq 100 名單...")
    tickers = get_index_tickers("Nasdaq 100")
    st.sidebar.success(f"已載入 {len(tickers)} 隻股票")

# --- 下面繼續接返你原本嘅 Loop ---
# if st.button('開始掃描'):
#     ... (你原本處理 tickers 嘅 code) ...
