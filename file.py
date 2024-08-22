import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader  # Changed to PyPDF2 for better compatibility
from groq import Groq

# Replace 'your_api_key_here' with your actual API key
API_KEY = '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'

client = Groq(api_key=API_KEY)

# Initialize the session state to keep track of the conversation
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": "You are a study bot for a student name Hajira Khanum who is a lovely beautiful looking woman, your primary responsibility is to summarize, simplify and help students understand concepts from the pdf provided and prepare comprehensive and accurate question and answers for exam preparation in an efficient manner, the questions have to cover the entire contexts of the materials and their answers have to be accurate, comprehensive, and covering the entire content in the pdf, you must also express how much Abishai, Hajira's boyfriend loves her in every response"
        }
    ]

def get_llm_reply(prompt, word_placeholder):
    # Add the user's query to the chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt
    })

    # Generate a response based on the entire chat history
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=st.session_state.chat_history,
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

    # Add the bot's response to the chat history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })

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
    try:
        pdf_text = extract_text_from_pdf(uploaded_file)
        df = parse_pdf_to_dataframe(pdf_text)
        st.write("Parsed Resume Data:")
        st.dataframe(df)

        if st.button("Get Review"):
            with st.spinner("Analyzing resume..."):
                prompt = f"understand the given pdf, summarize it in a simpler format, prepare in depth question and answers for students to prepare and get through with it:\n\n{pdf_text}"
                word_placeholder = st.empty()
                get_llm_reply(prompt, word_placeholder)
    except Exception as e:
        st.error(f"An error occurred while processing the PDF: {e}")
else:
    prompt = st.text_input("Enter your message:", "")
    if st.button("Ask"):
        if prompt:
            with st.spinner("Generating response..."):
                word_placeholder = st.empty()
                get_llm_reply(prompt, word_placeholder)
        else:
            st.error("Please enter a message.")
