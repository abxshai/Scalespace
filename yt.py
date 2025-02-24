import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from groq import Groq
from pytube import YouTube

# API key
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  
# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

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
            model="llama-3.3-70b-versatile",
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
    """Fetch transcript from YouTube using pytube."""
    try:
        yt = YouTube(video_url)
        # Try to get English captions first; if not, use the first available caption.
        if 'en' in yt.captions:
            caption = yt.captions['en']
        elif yt.captions:
            caption = list(yt.captions.values())[0]
        else:
            st.error("No captions available.")
            return None
        
        transcript = caption.generate_srt_captions()
        # Remove timestamps and sequence numbers
        lines = []
        for line in transcript.splitlines():
            if not line.isdigit() and '-->' not in line:
                lines.append(line)
        return " ".join(lines)
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

def summarize_text(text):
    """Summarize text using Llama-3 via Groq."""
    try:
        prompt = f"Summarize this:\n{text}"
        response = get_llm_reply(prompt)
        return response
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
