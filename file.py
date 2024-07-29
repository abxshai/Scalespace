import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from groq import Groq
from typing import Generator
import time
import io

# Replace 'your_api_key_here' with your actual API key
API_KEY = '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'

client = Groq(api_key=API_KEY)

def get_llm_reply(prompt):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
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
        # Use Streamlit's placeholder to update the response word by word
        word_placeholder.write(response)
        time.sleep(0.1)  # Add a slight delay for smoother streaming effect
    return response

def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text

def parse_pdf_to_dataframe(pdf_text):
    # Placeholder function to convert PDF text to DataFrame
    # Modify this according to the structure of your PDF and the data you need
    data = {"text": [pdf_text]}
    df = pd.DataFrame(data)
    return df

st.title("Copilot for your Career")
uploaded_file = st.file_uploader("Upload your resume for custom review (PDF format)", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    df = parse_pdf_to_dataframe(pdf_text)
    st.write("Parsed Resume Data:")
    st.dataframe(df)

    if st.button("Send to Groq API"):
        with st.spinner("Analyzing resume..."):
            prompt = f"Review the following resume:\n\n{pdf_text}"
            word_placeholder = st.empty()
            get_llm_reply(prompt)
else:
    prompt = st.text_input("Enter your message:", "")
    if st.button("Send"):
        if prompt:
            with st.spinner("Generating response..."):
                word_placeholder = st.empty()
                get_llm_reply(prompt)
        else:
            st.error("Please enter a message.")
