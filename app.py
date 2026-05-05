import streamlit as st
import pandas as pd
from googleapiclient.discovery import build

# 1. 設定網頁基本資訊
st.set_page_config(page_title="季節性商品市場趨勢觀測站", page_icon="🎃", layout="wide")

st.title('🎃 季節性商品市場趨勢觀測站')
st.markdown("### 追蹤萬聖節派對小物 (Party Favors) 社群熱度")

# 2. 側邊欄設定區
st.sidebar.header("設定區")
# 為了資安，API Key 由介面輸入，不寫死在程式碼中
api_key = st.sidebar.text_input("請輸入 YouTube API Key", type="password")
search_query = st.sidebar.text_input("輸入觀測關鍵字", value="Halloween party favors trends")
max_results = st.sidebar.slider("抓取影片數量", min_value=10, max_value=50, value=20)

# 3. 執行抓取與展示
if st.sidebar.button("開始抓取最新趨勢"):
    if not api_key:
        st.sidebar.error("請先輸入 API Key！")
    else:
        with st.spinner('資料抓取中，請稍候...'):
            try:
                # 建立 YouTube API 請求
                youtube = build('youtube', 'v3', developerKey=api_key)
                request = youtube.search().list(
                    q=search_query,
                    part='snippet',
                    maxResults=max_results,
                    type='video',
                    order='viewCount' # 直接依觀看次數排序，找出熱門爆款
                )
                response = request.execute()

                # 整理 API 回傳的資料
                video_data = []
                for item in response.get('items', []):
                    title = item['snippet']['title']
                    channel = item['snippet']['channelTitle']
                    publish_date = item['snippet']['publishedAt'][:10] # 只取 YYYY-MM-DD
                    video_id = item['id']['videoId']
                    video_link = f"https://www.youtube.com/watch?v={video_id}"

                    video_data.append({
                        '發布日期': publish_date,
                        '頻道名稱': channel,
                        '影片標題': title,
                        '影片連結': video_link
                    })

                # 將資料轉為表格 (DataFrame)
                df = pd.DataFrame(video_data)

                st.success("抓取完成！以下為目前市場熱度最高的相關影片：")

                # 在網頁上繪製互動式表格
                st.dataframe(
                    df,
                    column_config={
                        "影片連結": st.column_config.LinkColumn("點擊觀看影片")
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # 提供 CSV 下載按鈕 (使用 utf-8-sig 確保 Excel 打開中文不會亂碼)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載資料匯入 Power Query (CSV)",
                    data=csv,
                    file_name='halloween_trend_data.csv',
                    mime='text/csv',
                )

            except Exception as e:
                st.error(f"發生錯誤，請檢查 API Key 是否正確或配額已滿。錯誤訊息：{e}")
else:
    st.info("👈 請在左側設定區貼上你的 API Key，並點擊「開始抓取最新趨勢」")