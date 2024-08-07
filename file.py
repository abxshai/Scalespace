import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from groq import Groq
from typing import Generator
import time
import io
import logging

logging.basicConfig(level=logging.DEBUG)

# Replace 'your_api_key_here' with your actual API key
API_KEY = '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'
logging.debug("API_KEY set")

client = Groq(api_key=API_KEY)

def get_llm_reply(prompt, word_placeholder):
    logging.debug(f"Prompt received: {prompt}")
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "you are a career counseling and guidance bot, whose primary function is to help the user with their career related queries by giving them specific guidance, career plans, and resources that can help them solve any career related issues."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        response = ""
        for chunk in completion:
            delta = chunk.choices[0].delta.content or ""
            response += delta
            word_placeholder.write(response)
            time.sleep(0.1)
        return response
    except Exception as e:
        logging.error(f"Error in get_llm_reply: {e}")
        st.error(f"Error in generating reply: {e}")

def extract_text_from_pdf(file):
    logging.debug("Extracting text from PDF")
    try:
        pdf = PdfReader(file)
        text = ""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        logging.error(f"Error in extract_text_from_pdf: {e}")
        st.error(f"Error in extracting text from PDF: {e}")

def parse_pdf_to_dataframe(pdf_text):
    logging.debug("Parsing PDF to DataFrame")
    try:
        data = {"text": [pdf_text]}
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        logging.error(f"Error in parse_pdf_to_dataframe: {e}")
        st.error(f"Error in parsing PDF to DataFrame: {e}")

# Streamlit configuration for theme
st.set_page_config(
    page_title="Copilot for your Career",
    page_icon="*",
    layout="wide",
    initial_sidebar_state="expanded",
)

css = """
<style>
    .gradient-text {
        background: -webkit-linear-gradient(left, #87CEEB, #FF00FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
"""

st.markdown(css, unsafe_allow_html=True)
st.markdown('<h1 class="gradient-text">Copilot for your Career</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    df = parse_pdf_to_dataframe(pdf_text)
    st.write("Parsed Resume Data:")
    st.dataframe(df)

    if st.button("Get Review"):
        with st.spinner("Analyzing resume..."):
            prompt = f"Review the following resume, give a rating out of 10 as well:\n\n{pdf_text}"
            word_placeholder = st.empty()
            get_llm_reply(prompt, word_placeholder)
else:
    prompt = st.text_input("Enter your message:", "")
    if st.button("Ask"):
        if prompt:
            with st.spinner("Generating response..."):
                word_placeholder = st.empty()
                get_llm_reply(prompt, word_placeholder)
        else:
            st.error("Please enter a message.")
