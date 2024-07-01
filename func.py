import streamlit as st
import Groq
import time

# Replace 'your_api_key_here' with your actual API key
API_KEY = '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'

client = Groq(api_key=API_KEY)

def get_llm_reply(prompt):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
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

st.title("Copilot for your Career")

prompt = st.text_input("Enter your message:", "")

if st.button("Send"):
    if prompt:
        with st.spinner("Generating response..."):
            word_placeholder = st.empty()
            get_llm_reply(prompt)
    else:
        st.error("Please enter a message.")
