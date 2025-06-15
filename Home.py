import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

st.set_page_config(page_title="🏠 Home", layout="centered")

st.title("📚 LangChain Multi-Tool App")
st.markdown("Welcome! Please enter your Groq API key to proceed.")

LANGSMITH_TRACING='true'
LANGSMITH_API_KEY=''
LANGSMITH_PROJECT='Multi Agent'




st.markdown("-------------------------------")
# Groq API key input
groq_api_key = ''

# Store API key in session state
if groq_api_key:
    st.session_state["groq_api_key"] = groq_api_key
    st.success("API key stored successfully!")
else:
    st.warning("Please enter your API key.")

# Navigation buttons
st.markdown("---")
st.subheader("🧠 Available Tools")

col1, col2, col3 , col4 = st.columns(4)

with col1:
    if st.button("📄 PDF Summarizer") and "groq_api_key" in st.session_state:
        st.switch_page("pages/pdf_summarizer.py")

with col2:
    if st.button("🤖 Research Paper Search") and "groq_api_key" in st.session_state:
        st.switch_page("pages/research_paper.py")

with col3:
    if st.button("📺 Youtube Summarizer") and "groq_api_key" in st.session_state:
        st.switch_page("pages/yt_summarizer.py")

with col4:
    if st.button("📺 Text to Image") and "groq_api_key" in st.session_state:
        st.switch_page("pages/image_gen.py")
