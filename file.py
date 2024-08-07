import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from groq import Groq


# Replace 'your_api_key_here' with your actual API key
API_KEY = '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'

client = Groq(api_key=API_KEY)

def get_llm_reply(prompt, word_placeholder):
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
        # Use Streamlit's placeholder to update the response word by word
        word_placeholder.write(response)
    return response

def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        text += page.extract_text()
    return text

def parse_pdf_to_dataframe(pdf_text):
    data = {"text": [pdf_text]}
    df = pd.DataFrame(data)
    return df

# Streamlit configuration for theme
st.set_page_config(
    page_title="Copilot for your Career",
    page_icon="*",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS to inject contained in a string
css = """
<style>
    .gradient-text {
        background: -webkit-linear-gradient(left, #87CEEB, #FF00FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
"""

# Inject CSS with markdown
st.markdown(css, unsafe_allow_html=True)

# Title with gradient text
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
