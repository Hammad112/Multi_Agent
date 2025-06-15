import streamlit as st


st.set_page_config(page_title="🏠 Home", layout="centered")

st.title("📚 LangChain Multi-Tool App")
st.markdown("Welcome! Please enter your Groq API key to proceed.")

langsmith_tracing = st.secrets["LANGSMITH_TRACING"]
langsmith_api_key = st.secrets["LANGSMITH_API_KEY"]
langsmith_project = st.secrets["LANGSMITH_PROJECT"]

st.markdown("-------------------------------")

groq_api_key = st.secrets["GROQ_API_KEY"]

# Store API key in session state
if groq_api_key:
    st.session_state["groq_api_key"] = groq_api_key
    st.success("API key stored successfully!")
else:
    st.warning("Please enter your API key.")

# Navigation buttons
st.markdown("---")
st.subheader("🧠 Available Tools")

col1, col2, col3  = st.columns(3)


with col1:
    if st.button("🤖 Research Paper Search") and "groq_api_key" in st.session_state:
        st.switch_page("pages/research_paper.py")

with col2:
    if st.button("📺 Youtube Summarizer") and "groq_api_key" in st.session_state:
        st.switch_page("pages/yt_summarizer.py")

with col3:
    if st.button("📺 Text to Image") and "groq_api_key" in st.session_state:
        st.switch_page("pages/image_gen.py")
