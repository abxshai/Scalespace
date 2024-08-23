import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader 
from groq import Groq

# Set your actual API key here
API_KEY = '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'

# Initialize the Groq client with the API key
client = Groq(api_key=API_KEY)

def get_llm_reply(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
               {
                "role": "system",
                "content": "You are a career counseling and guidance bot, whose primary function is to help the user with their career-related queries by giving them specific guidance, career plans, and resources that can help them solve any career-related issues."
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
            # Update the response in real-time using Streamlit's placeholder
            word_placeholder.write(response)
        
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def extract_text_from_pdf(file):
    try:
        pdf = PdfReader(file)
        text = ""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Failed to extract text from PDF: {e}")
        return ""

def parse_pdf_to_dataframe(pdf_text):
    data = {"text": [pdf_text]}
    df = pd.DataFrame(data)
    return df

st.title("Copilot for your Career")

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    if pdf_text:
        df = parse_pdf_to_dataframe(pdf_text)
        st.write("Parsed Resume Data:")
        st.dataframe(df)

        if st.button("Get Review"):
            with st.spinner("Analyzing resume..."):
                prompt = f"Review the following resume, give it a rating out of 10, provide actionable advice on the words and points included:\n\n{pdf_text}"
                word_placeholder = st.empty()  # Placeholder for streaming response
                get_llm_reply(prompt)
else:
    prompt = st.text_input("Enter your message:", "")
    if st.button("Send"):
        if prompt:
            with st.spinner("Generating response..."):
                word_placeholder = st.empty()  # Placeholder for streaming response
                get_llm_reply(prompt)
        else:
            st.error("Please enter a message.")
