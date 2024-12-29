import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from groq import Groq
import google.generativeai as genai
import yt_dlp
import requests
import os
from dotenv import load_dotenv

# Load API keys from environment variables or .env file
load_dotenv()  # Load variables from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Validate API keys
if not GROQ_API_KEY or not GENAI_API_KEY:
    st.error("API keys are missing. Please set GROQ_API_KEY and GENAI_API_KEY in your environment variables or .env file.")
    st.stop()

# Initialize Groq client and GenAI
client = Groq(api_key=GROQ_API_KEY)
genai.configure(api_key=GENAI_API_KEY)
genai_model = genai.GenerativeModel("gemini-1.5-flash")

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
    unsafe_allow_html=True
)

# Helper functions
def get_llm_reply(prompt):
    """Get reply from the Groq AI model."""
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a career guidance assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=1,
            max_tokens=1024,
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        st.error(f"Error with LLM: {e}")
        return None


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
    """Fetch transcript from YouTube using yt-dlp."""
    options = {
        'quiet': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'skip_download': True,
        'subtitleslangs': ['en'],
        'outtmpl': '%(id)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subtitles = info.get("automatic_captions") or info.get("subtitles")
            
            if subtitles and 'en' in subtitles:
                srt_url = subtitles['en'][0]['url']
                response = requests.get(srt_url)
                if response.status_code == 200:
                    return response.text
                else:
                    return "Error fetching subtitles."
            else:
                return "No subtitles available for this video."
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
                    response = get_llm_reply(prompt)
                    if response:
                        st.subheader("Resume Feedback:")
                        st.write(response)

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
                response = get_llm_reply(prompt)
                if response:
                    st.subheader("Career Advice:")
                    st.write(response)
