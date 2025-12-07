import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# ==========================================
# 1. 系統設置 & 頁面配置
# ==========================================
st.set_page_config(page_title="J Law 冠軍操盤室 (Pro)", layout="wide", page_icon="⚔️")

# 自定義 CSS 美化
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; border-radius: 10px; padding: 15px; margin: 10px 0;}
    .stAlert {margin-top: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("⚔️ J Law 冠軍操盤室：智能戰術執行板 (Pro)")
st.markdown("""
> **核心戰法**：尋找上升趨勢中的 **「網球行為 (Tennis Ball Action)」**。
> **掃描標準**：股價 > 50MA (趨勢向上) + 拉回測試 10/20MA (支撐) + 量縮 (賣壓竭盡)。
""")

if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# ==========================================
# 2. 數據獲取 (股票池)
# ==========================================
@st.cache_data
def get_nasdaq100_tickers():
    # 常見強勢股清單
    return [
        "NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST",
        "AMD", "NFLX", "QCOM", "TXN", "AMAT", "BKNG", "ADP", "ADI", "MU", "LRCX",
        "INTC", "CSCO", "TMUS", "PEP", "LIN", "ADBE", "ISRG", "VRTX", "REGN",
        "PANW", "SNPS", "CDNS", "KLAC", "CRWD", "MSTR", "COIN", "PLTR", "ARM", "SMCI",
        "UBER", "ABNB", "DASH", "NET", "DDOG", "ZS", "APP", "CVNA", "HIMS"
    ]

# ==========================================
# 3. 核心運算引擎 (深度分析邏輯)
# ==========================================
def analyze_stock_deep(ticker, df):
    try:
        # 確保數據足夠
        if len(df) < 200: return None

        # 提取數據 (最新一筆)
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        close = curr['Close']
        high = curr['High']
        low = curr['Low']
        vol = curr['Volume']
        
        # 計算均線
        sma10 = df['Close'].rolling(10).mean().iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 計算平均成交量 (50日)
        avg_vol_50 = df['Volume'].rolling(50).mean().iloc[-1]
        if avg_vol_50 == 0: return None
        vol_ratio = vol / avg_vol_50 
        
        # 計算 RSI (14)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # --- 策略邏輯判斷 ---
        setup_found = False
        reasons = [] 
        setup_name = ""
        
        # 1. 大趨勢過濾 (必須在 200MA 之上)
        if close > sma200 and sma50 > sma200:
            
            # 2. 中期趨勢 (股價 > 50MA)
            if close > sma50:
                
                # 計算與均線的距離 (百分比)
                dist_10 = abs(low - sma10) / sma10
                dist_20 = abs(low - sma20) / sma20
                
                # A. 超級強勢 (Super Strength) - 測試 10MA
                if dist_10 <= 0.02 and low >= sma10 * 0.98: # 放寬一點容錯率
                    setup_found = True
                    setup_name = "🟢 10MA 強力支撐"
                    reasons.append("股價強勢整理，回測 10MA 未跌破。")
                
                # B. 標準波段 (Tennis Ball) - 測試 20MA
                elif dist_20 <= 0.02 and low >= sma20 * 0.98:
                    setup_found = True
                    setup_name = "🟡 20MA 網球反彈"
                    reasons.append("經典波段買點，回測 20MA 尋求支撐。")
            
            # C. 動能突破 (Momentum Breakout)
            if rsi > 60 and rsi < 80 and close > sma10 and close > prev['Close'] * 1.03:
                 setup_found = True
                 setup_name = "🔥 強力突破發動"
                 reasons.append("單日大漲 >3% 且 RSI 強勢，動能回歸。")

            # --- 綜合過濾 ---
            if setup_found:
                # 量能分析
                if vol_ratio < 0.75:
                    reasons.append(f"✅ **極致縮量**：量能僅平均 {int(vol_ratio*100)}%，賣壓枯竭。")
                elif vol_ratio > 1.5 and close > prev['Close']:
                    reasons.append(f"🚀 **放量攻擊**：量能放大至 {int(vol_ratio*100)}%，機構進場。")
                
                # 計算交易參數 (Setup Parameters)
                buy_trigger = high + 0.02  # 突破今日高點才買
                stop_loss = low - 0.02     # 跌破今日低點止損
                
                # 防止止損過窄
                atr = (df['High'] - df['Low']).rolling(14).mean().iloc[-1]
                if (buy_trigger - stop_loss) < atr * 0.5:
                    stop_loss = buy_trigger - atr # 至少給 1 ATR 的空間

                risk = buy_trigger - stop_loss
                target = buy_trigger + (risk * 3) # 3R

                return {
                    "代號": ticker,
                    "現價": round(close, 2),
                    "策略": setup_name,
                    "RSI": round(rsi, 1),
                    "漲跌幅": round(((close - prev['Close'])/prev['Close'])*100, 2),
                    "買入原因": reasons,
                    "買入觸發": round(buy_trigger, 2),
                    "止損": round(stop_loss, 2),
                    "目標": round(target, 2),
                    "風險益比": "1:3",
                    "成交量比": round(vol_ratio, 2)
                }
    except Exception as e:
        return None
    return None

# ==========================================
# 4. 輔助功能：獲取基本面與新聞
# ==========================================
def get_stock_info(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        
        # 處理財報日期 (嘗試獲取下一次財報)
        earnings_date = "N/A"
        try:
            cal = t.calendar
            if cal is not None and not cal.empty:
                # 兼容不同版本的 yfinance 輸出
                if 'Earnings Date' in cal.index:
                     earnings_date = cal.loc['Earnings Date'][0].strftime('%Y-%m-%d')
                elif 'Earnings Low' in cal: # 新版可能返回DataFrame
                     earnings_date = cal.iloc[0, 0] # 簡單取第一個日期
        except:
            pass
            
        return {
            "產業": info.get('sector', 'N/A'),
            "行業": info.get('industry', 'N/A'),
            "市值": f"{info.get('marketCap', 0) / 1000000000:.2f} B",
            "本益比": info.get('trailingPE', 'N/A'),
            "下季財報": earnings_date,
            "描述": info.get('longBusinessSummary', '無描述')[:200] + "..."
        }, t.news
    except:
        return None, []

# ==========================================
# 5. UI 顯示邏輯 (戰術板)
# ==========================================
def show_tactical_board(data):
    st.markdown("---")
    
    # 頂部標題與即時狀態
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.header(f"🦅 {data['代號']} 戰術儀表板")
        color = "green" if data['漲跌幅'] > 0 else "red"
        st.markdown(f"**現價**: ${data['現價']} (<span style='color:{color}'>{data['漲跌幅']}%</span>) | **策略**: {data['策略']}", unsafe_allow_html=True)
    
    with col_h2:
        st.markdown("#### 建議倉位")
        # 簡單的動態倉位建議
        if data['RSI'] > 70:
            st.warning("⚠️ RSI 過高，半倉嘗試")
        else:
            st.success("✅ 標準倉位")

    # 分頁功能：圖表 / 交易計劃 / 基本面 / 新聞
    tab1, tab2, tab3, tab4 = st.tabs(["📈 技術圖表", "📝 交易計劃", "🏢 基本面數據", "📰 相關新聞"])

    with tab1:
        # TradingView Widget
        html_code = f"""
        <div class="tradingview-widget-container">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
            "width": "100%",
            "height": 550,
            "symbol": "{data['代號']}",
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
              {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 10 }}, "title": "10 MA" }},
              {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 20 }}, "title": "20 MA" }},
              {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 50 }}, "title": "50 MA" }}
            ]
          }}
          );
          </script>
        </div>
        """
        components.html(html_code, height=560)

    with tab2:
        c1, c2, c3 = st.columns(3)
        c1.metric("🟢 買入觸發 (Stop Buy)", f"${data['買入觸發']}")
        c2.metric("🔴 止損價格 (Stop Loss)", f"${data['止損']}")
        c3.metric("🎯 獲利目標 (Target)", f"${data['目標']}")
        
        st.markdown("### 執行邏輯")
        st.info("此策略採用「突破確認」機制。不要直接市價買入，請設定 Stop Limit 單在「買入觸發」價位。")
        st.markdown("**符合條件原因：**")
        for r in data['買入原因']:
            st.write(f"- {r}")

    with tab3:
        with st.spinner("正在加載基本面數據..."):
            info, _ = get_stock_info(data['代號'])
            if info:
                i1, i2, i3 = st.columns(3)
                i1.write(f"**產業**: {info['產業']}")
                i2.write(f"**市值**: ${info['市值']}")
                i3.write(f"**本益比**: {info['本益比']}")
                
                st.write(f"**所屬行業**: {info['行業']}")
                st.warning(f"📅 **預計財報日**: {info['下季財報']} (交易前請確認是否接近)")
                st.caption(f"公司簡介: {info['描述']}")
            else:
                st.error("無法獲取基本面數據")

    with tab4:
        with st.spinner("正在搜索新聞..."):
            _, news_list = get_stock_info(data['代號'])
            if news_list:
                for n in news_list[:5]: # 只顯示前5則
                    # 嘗試獲取縮略圖，如果沒有則不顯示
                    try:
                        pub_time = datetime.fromtimestamp(n['providerPublishTime']).strftime('%Y-%m-%d %H:%M')
                        st.markdown(f"**[{n['title']}]({n['link']})**")
                        st.caption(f"來源: {n['publisher']} | 時間: {pub_time}")
                        st.divider()
                    except:
                        continue
            else:
                st.write("暫無相關新聞")

# ==========================================
# 6. 主程序邏輯
# ==========================================

# 側邊欄控制
st.sidebar.header("🔍 掃描設定")
source = st.sidebar.radio("股票池來源", ["Nasdaq 精選強勢股", "自定義輸入"])

custom_input = ""
if source == "自定義輸入":
    custom_input = st.sidebar.text_area("輸入代號 (逗號分隔)", "NVDA, TSLA, PLTR, COIN, MSTR")
    st.sidebar.caption("提示：支援美股代號")

if st.sidebar.button("🚀 啟動戰術掃描", type="primary"):
    target_list = []
    
    # 決定掃描列表
    if source == "Nasdaq 精選強勢股":
        target_list = get_nasdaq100_tickers()
    else:
        if custom_input:
            target_list = [x.strip().upper() for x in custom_input.split(',')]
        else:
            st.error("請輸入股票代號")

    if target_list:
        with st.spinner("正在進行多維度運算 (價格結構/RSI/量能)..."):
            # 批量下載數據優化 (避免多次請求)
            try:
                # yfinance 批量下載
                raw_data = yf.download(target_list, period="1y", group_by='ticker', threads=True, progress=False)
                
                results = []
                progress_bar = st.progress(0)
                
                for i, ticker in enumerate(target_list):
                    progress_bar.progress((i + 1) / len(target_list))
                    
                    # 處理單一股票與多股票的數據結構差異
                    try:
                        if len(target_list) == 1:
                            df_stock = raw_data
                        else:
                            # 提取特定股票的 DataFrame
                            df_stock = raw_data[ticker]
                        
                        # 清洗數據
                        df_stock = df_stock.dropna(how='all') 
                        
                        if not df_stock.empty:
                            res = analyze_stock_deep(ticker, df_stock)
                            if res:
                                results.append(res)
                    except KeyError:
                        continue # 略過無效代號
                    except Exception as e:
                        continue
                
                progress_bar.empty()
                
                if results:
                    st.session_state['scan_results'] = pd.DataFrame(results)
                    st.success(f"掃描完成！發現 {len(results)} 隻符合戰術型態的股票。")
                else:
                    st.warning("掃描完成，但沒有發現符合嚴格標準的股票。建議放寬篩選條件或等待機會。")
                    st.session_state['scan_results'] = None
            except Exception as e:
                st.error(f"數據下載發生錯誤: {str(e)}")

# 顯示結果區域
if st.session_state['scan_results'] is not None:
    df_res = st.session_state['scan_results']
    
    # 佈局：左側列表，右側詳情
    col_list, col_detail = st.columns([1, 2])
    
    with col_list:
        st.subheader("📋 候選清單")
        
        # 簡單過濾器
        sort_by = st.selectbox("排序方式", ["RSI", "成交量比", "漲跌幅"])
        df_res = df_res.sort_values(by=sort_by, ascending=False)
        
        # 互動表格
        st.dataframe(
            df_res[['代號', '策略', 'RSI', '成交量比']], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "成交量比": st.column_config.ProgressColumn(
                    "量能比 (1.0=均量)", min_value=0, max_value=2, format="%.2f"
                ),
                "RSI": st.column_config.NumberColumn("RSI 強度", format="%.0f")
            }
        )
        
        # 選擇器
        selected_ticker = st.selectbox("👇 選擇股票查看詳情：", df_res['代號'].unique())

    with col_detail:
        if selected_ticker:
            # 從 DataFrame 中獲取該股票的數據
            row_data = df_res[df_res['代號'] == selected_ticker].iloc[0].to_dict()
            show_tactical_board(row_data)

else:
    # 初始歡迎畫面
    st.info("👈 請在左側側邊欄選擇股票池並點擊「啟動戰術掃描」")
    st.markdown("""
    ### 🛠️ 使用說明
    1. **策略原理**：此系統自動過濾垃圾股，只尋找「強勢股回調」的機會。
    2. **買入觸發**：系統給出的價格是「突破買入價」，未突破前請勿進場。
    3. **風險控制**：嚴格遵守止損與 3R 獲利目標。
    """)
