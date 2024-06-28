from langchain_community.llms import Ollama
import streamlit as st
import requests
llm = Ollama(model = "llama3")


try:
    response = requests.get("http://localhost:11434/api/generate")
    print(response.status_code)
    print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")



st.title("Copilot for your career")
prompt = st.text_area("enter your prompt:")
if st.button("Ask"):
    if prompt:
        with st.spinner("please wait....."):
            st.write(llm.stream(prompt, stop=['<|eot_id|>'])) 
