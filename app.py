import base64
import os

# ... (其他的 import 保持不變)

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def inject_css():
    # 這裡讀取你剛剛上傳的 tesla_bg.jpg
    img_file = "tesla_bg.jpg"
    bin_str = get_base64_of_bin_file(img_file)

    # 如果讀取成功，用本地圖；失敗則用備用連結
    if bin_str:
        bg_image_css = f'url("data:image/jpg;base64,{bin_str}")'
    else:
        # 備用圖：如果讀不到你的檔案，會顯示這張
        bg_image_css = 'url("https://i.imgur.com/M8S4A3P.jpeg")' 

    overlay = "radial-gradient(circle, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.95) 90%)"

    style_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

        .stApp {{
            background-image: {overlay}, {bg_image_css};
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
            color: #E0E0E0;
            font-family: 'Noto Sans TC', sans-serif;
        }}
        
        /* ... 其他 CSS 樣式保持不變，直接複製之前的即可 ... */
        section[data-testid="stSidebar"] {{
            background: rgba(5, 5, 5, 0.9);
            border-right: 1px solid #333;
            backdrop-filter: blur(10px);
        }}
        /* 記得把剩下的 CSS 貼回來 */
    </style>
    """
    st.markdown(style_code, unsafe_allow_html=True)
