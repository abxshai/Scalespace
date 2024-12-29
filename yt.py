import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from yt_dlp import YoutubeDL
from google.generativeai import GenerativeModel, configure

# Embed API Keys directly
GROQ_API_KEY = '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'
GENAI_API_KEY = 'AIzaSyDghQB-hpVMNhdd2Fd4JPgRNr_eZ-1GMp0'

# Initialize Generative AI
configure(api_key=GENAI_API_KEY)
genai_model = GenerativeModel("gemini-1.5-flash")

# Streamlit layout styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #000000, #000000, #063970);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Helper functions
def extract_text_from_pdf(file):
    """Extract text from an uploaded PDF."""
    try:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def get_youtube_transcript(video_url):
    """Fetch transcript using yt-dlp."""
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "skip_download": True,
            "writeautomaticsub": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subtitles = info.get("subtitles") or {}
            if "en" in subtitles:
                url = subtitles["en"][0]["url"]
                with YoutubeDL({}) as ydl_sub:
                    transcript = ydl_sub.urlopen(url).read().decode("utf-8")
                    return transcript
            else:
                raise ValueError("No subtitles found for the video.")
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

def summarize_text(text):
    """Summarize text using GenAI."""
    try:
        response = genai_model.generate_content(f"Summarize this:\n{text}")
        return response.text
    except Exception as e:
        st.error(f"Error summarizing text: {e}")
        return None

# Main App Layout
st.title("Copilot for Your Career")

# Tabs for navigation
tabs = st.tabs(["Resume Review", "YouTube Summarizer", "Career Counseling"])

# Resume Review Tab
with tabs[0]:
    st.header("Resume Review")
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
    if uploaded_file:
        pdf_text = extract_text_from_pdf(uploaded_file)
        if pdf_text:
            st.write("Extracted Resume Content:")
            st.text_area("Resume Text", pdf_text, height=300)
            if st.button("Analyze Resume"):
                with st.spinner("Analyzing resume..."):
                    prompt = f"Review the following resume and provide feedback:\n{pdf_text}"
                    try:
                        response = genai_model.generate_content(prompt)
                        if response:
                            st.subheader("Resume Feedback:")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"Error analyzing resume: {e}")

# YouTube Summarizer Tab
with tabs[1]:
    st.header("YouTube Video Summarizer")
    video_url = st.text_input("Enter YouTube Video URL")
    if st.button("Summarize Video"):
        if video_url:
            with st.spinner("Fetching and summarizing video transcript..."):
                transcript = get_youtube_transcript(video_url)
                if transcript:
                    summary = summarize_text(transcript)
                    if summary:
                        st.subheader("Video Summary:")
                        st.write(summary)

# Career Counseling Tab
with tabs[2]:
    st.header("Career Counseling")
    prompt = st.text_input("Enter your career-related query")
    if st.button("Get Advice"):
        if prompt:
            with st.spinner("Fetching advice..."):
                try:
                    response = genai_model.generate_content(prompt)
                    if response:
                        st.subheader("Career Advice:")
                        st.write(response.text)
                except Exception as e:
                    st.error(f"Error fetching career advice: {e}")
