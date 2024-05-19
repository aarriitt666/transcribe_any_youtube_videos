from __future__ import unicode_literals
import yt_dlp as youtube_dl
import whisper
import streamlit as st
import os
import re

def sanitize_filename(filename):
    """Sanitize the filename to remove or replace unsafe characters."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_video(url):
    """Download a YouTube video and return the title and filename."""
    options = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(options) as downloader:
        info_dict = downloader.extract_info(url, download=True)
        title = sanitize_filename(info_dict.get('title', 'untitled'))
        filename = downloader.prepare_filename(info_dict)
        # Ensure the filename is absolute
        filename = os.path.abspath(filename)
    return title, filename

def transcribe_audio(filename):
    """Transcribe the audio file using Whisper."""
    model = whisper.load_model("base")
    try:
        result = model.transcribe(filename, fp16=False)
        return result['text']
    except Exception as e:
        st.error(f"Failed to transcribe audio: {e}")
        return None

def save_transcription(transcription, output_path):
    """Save the transcription to a text file."""
    with open(output_path, "w") as f:
        f.write(transcription)

st.title("YouTube Audio Downloader and Transcription")

# Section 1: Download YouTube Audio
st.header("Download YouTube Audio")
st.write("Enter a YouTube URL to download the audio as an .m4a file.")
youtube_url = st.text_input("Enter YouTube URL:")

if st.button("Download"):
    if youtube_url:
        st.write("Downloading and processing video...")
        try:
            title, video_filename = download_video(youtube_url)
            st.write(f"Downloaded and saved as: {video_filename}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.error(str(e))
    else:
        st.warning("Please enter a YouTube URL.")

# Section 2: Transcribe Audio
st.header("Transcribe Audio")
st.write("Upload an .m4a file to transcribe it to text using OpenAI's Whisper model.")
uploaded_file = st.file_uploader("Choose an .m4a file", type="m4a")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    temp_filename = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write(f"Uploaded file saved as: {temp_filename}")

    st.write("Transcribing audio...")
    transcription = transcribe_audio(temp_filename)
    if transcription:
        # Save the transcription to a text file
        output_txt_path = os.path.splitext(temp_filename)[0] + ".txt"
        save_transcription(transcription, output_txt_path)
        st.write(f"Transcription saved as: {output_txt_path}")
