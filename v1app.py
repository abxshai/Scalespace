from langchain_community.llms import Ollama
import streamlit as st
llm = Ollama(model = "llama3")



st.title("Copilot for your career")
prompt = st.text_area("enter your prompt:")
if st.button("Ask"):
    if prompt:
        with st.spinner("please wait....."):
            st.write(llm.stream(prompt, stop=['<|eot_id|>']))
