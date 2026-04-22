import streamlit as st
import yt_dlp
import os
import glob

st.set_page_config(page_title="YT Downloader", page_icon="🎬")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextInput > div > div > input { background-color: #262730; color: white; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 YT to MP4 Downloader")
st.write("Paste the link and wait for the magic.")

url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    if st.button("Start Download & Convert"):
        try:
            with st.spinner("Downloading and processing... this may take a minute."):
                # Setup options
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': 'downloaded_video.%(ext)s', # Fix name to make it easy to find
                }

                # Clear previous downloads
                if os.path.exists("downloaded_video.mp4"):
                    os.remove("downloaded_video.mp4")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Check if file exists
                if os.path.exists("downloaded_video.mp4"):
                    with open("downloaded_video.mp4", "rb") as file:
                        st.success("Conversion Finished!")
                        st.download_button(
                            label="💾 DOWNLOAD MP4",
                            data=file,
                            file_name="video_result.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                else:
                    st.error("File was not found after processing.")

        except Exception as e:
            st.error(f"Error: {str(e)}")

st.divider()
st.caption("Note: High-resolution videos (4K) might take longer to process on Streamlit Cloud.")
