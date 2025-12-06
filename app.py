import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components
from io import StringIO
from tradingview_ta import TA_Handler, Interval, Exchange

# ==========================================
# 1. 頁面設定
# ==========================================
st.set_page_config(page_title="J Law 冠軍操盤室", layout="wide", page_icon="🚀")

st.title("🚀 J Law (Mark Minervini) 冠軍操盤室")
st.markdown("""
此工具結合 **TradingView 技術分析** 與 **J Law 趨勢樣板 (Trend Template)** 策略。
目標：尋找 **多頭排列 (50 > 150 > 200)** 且 **動能強勁 (RSI 高 + 接近新高)** 的股票。
""")

# 初始化 Session State
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# ==========================================
# 2. 核心功能
# ==========================================

# --- 獲取 Nasdaq 100 ---
@st.cache_data
def get_nasdaq100():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            if 'Ticker' in table.columns:
                return table['Ticker'].tolist()
        return []
    except:
        return []

# --- 顯示 TradingView 實時圖表 (含 J Law 均線) ---
def show_tv_widget(symbol):
    # 這是一段 HTML+JS 代碼，用來嵌入 TradingView 官方 Widget
    # 我們設定了 studies (技術指標) 自動顯示 MASimple (均線)
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": 600,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Exchange",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart",
        "studies": [
          {{
            "id": "MASimple@tv-basicstudies",
            "inputs": {{ "length": 50 }},
            "title": "50 MA (中期)"
          }},
          {{
            "id": "MASimple@tv-basicstudies",
            "inputs": {{ "length": 150 }},
            "title": "150 MA (趨勢)"
          }},
          {{
            "id": "MASimple@tv-basicstudies",
            "inputs": {{ "length": 200 }},
            "title": "200 MA (長期)"
          }}
        ]
      }}
      );
      </script>
    </div>
    """
    components.html(html_code, height=600)

# --- J Law 掃描邏輯 ---
def scan_jlaw(tickers, strict_mode):
    results = []
    total = len(tickers)
    
    # 進度條
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        progress_bar.progress((i + 1) / total)
        status_text.text(f"正在分析 {ticker} ({i+1}/{total})...")
        
        try:
            handler = TA_Handler(
                symbol=ticker,
                screener="america",
                exchange="NASDAQ",
                interval=Interval.INTERVAL_1_DAY
            )
            analysis = handler.get_analysis()
            
            if analysis:
                # 獲取指標
                close = analysis.indicators['close']
                sma50 = analysis.indicators['SMA50']
                sma200 = analysis.indicators['SMA200']
                rsi = analysis.indicators['RSI']
                high52 = analysis.indicators.get('high52', close * 1.5) # 防呆
                low52 = analysis.indicators.get('low52', close * 0.5)
                
                # 計算 SMA 150 (TradingView TA 默認沒有 150，我們用 100 和 200 的中間值估算，或者簡化邏輯)
                # 為了準確，這裡我們用嚴格邏輯：股價 > 50 > 200
                
                # --- J Law 核心過濾條件 ---
                
                # 條件 1: 價格高於 50天線 和 200天線
                cond_trend = (close > sma50) and (close > sma200)
                
                # 條件 2: 50天線 高於 200天線 (黃金排列)
                cond_alignment = sma50 > sma200
                
                # 條件 3: 接近 52 週新高 (處於高位 25% 範圍內) - VCP 關鍵
                cond_near_high = close >= (high52 * 0.75)
                
                # 條件 4: 脫離 52 週低位 (升咗至少 30%)
                cond_above_low = close >= (low52 * 1.30)
                
                # 條件 5: 動能 RSI (J Law 喜歡 RSI > 70，但我哋設 55 做起點)
                cond_rsi = rsi > 55
                
                # 判斷是否符合
                is_match = False
                
                if strict_mode:
                    # 嚴格模式：必須全中
                    if cond_trend and cond_alignment and cond_near_high and cond_above_low and cond_rsi:
                        is_match = True
                else:
                    # 寬鬆模式：只要趨勢向上 + RSI OK 就得
                    if cond_trend and cond_rsi:
                        is_match = True
                
                if is_match:
                    results.append({
                        "代號": ticker,
                        "現價": round(close, 2),
                        "RSI": round(rsi, 2),
                        "離高位%": round((close - high52) / high52 * 100, 1),
                        "狀態": "✅ 符合"
                    })
                    
        except Exception as e:
            continue
            
    progress_bar.empty()
    status_text.empty()
    return results

# ==========================================
# 3. 主界面佈局
# ==========================================

# 側邊欄設定
st.sidebar.header("⚙️ 掃描設定")
mode = st.sidebar.radio("篩選模式", ["寬鬆模式 (更多結果)", "嚴格 J Law (Trend Template)"])
strict_mode = True if mode == "嚴格 J Law (Trend Template)" else False

if st.sidebar.button("🔍 開始掃描 Nasdaq 100", type="primary"):
    tickers = get_nasdaq100()
    if not tickers:
        st.error("無法下載名單")
    else:
        st.session_state['scan_results'] = scan_jlaw(tickers, strict_mode)

# 主畫面內容
col1, col2 = st.columns([1, 2])

# 左邊：結果列表
with col1:
    st.subheader(f"📋 掃描結果 ({mode})")
    
    if st.session_state['scan_results'] is not None:
        df = pd.DataFrame(st.session_state['scan_results'])
        
        if not df.empty:
            # 按 RSI 排序
            df = df.sort_values(by="RSI", ascending=False)
            st.write(f"共找到 {len(df)} 隻潛力股")
            
            # 互動表格，選取股票
            selected_row = st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun" # 點擊即刷新
            )
            
            # 獲取用戶點選的股票
            # (Streamlit 新版 selection 處理方法)
            # 簡單起見，我們用 Selectbox 輔助
            st.divider()
            target_stock = st.selectbox("👉 選擇要分析的股票：", df['代號'].tolist())
            
        else:
            st.warning("沒有股票符合條件。")
            target_stock = None
    else:
        st.info("👈 請在側邊欄點擊按鈕開始掃描")
        target_stock = None

# 右邊：實時圖表
with col2:
    st.subheader("📈 實時圖表分析")
    
    if target_stock:
        st.success(f"正在顯示 {target_stock} 實時走勢")
        st.caption("圖表已自動加載 J Law 關鍵均線：50MA, 150MA, 200MA")
        
        # 呼叫 TradingView Widget
        show_tv_widget(target_stock)
        
        st.info("""
        **🧐 J Law 圖表檢查重點：**
        1. **多頭排列**：股價是否在 50MA > 150MA > 200MA 之上？
        2. **200天線方向**：紅色那條 200MA 是否正在**向上**？(這是關鍵)
        3. **價格收縮 (VCP)**：股價是否經歷了波幅收窄？
        """)
    else:
        # 預設顯示 QQQ
        st.write("預覽 (QQQ)：")
        show_tv_widget("QQQ")
