import streamlit as st


st.set_page_config(page_title="🏠 Home", layout="centered")


st.markdown("""
    <style>
    .animated-title {
        font-size: 32px;
        font-weight: bold;
        background: linear-gradient(270deg, #ff4b1f, #1fddff, #ff4b1f);
        background-size: 600% 600%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s ease infinite;
    }

    @keyframes shine {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .animated-subtitle {
        font-size: 20px;
        color: white;
        opacity: 0;
        transform: translateY(10px);
        animation: fadeSlide 2s ease forwards;
        animation-delay: 0.5s;
    }

    @keyframes fadeSlide {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>

    <div class="animated-title">📚 LangChain Multi-Tool App</div>
    <div class="animated-subtitle">Ask Anything — We'll Search Wikipedia, Arxiv, and the Web for You</div>
""", unsafe_allow_html=True)


langsmith_tracing = st.secrets["LANGSMITH_TRACING"]
langsmith_api_key = st.secrets["LANGSMITH_API_KEY"]
langsmith_project = st.secrets["LANGSMITH_PROJECT"]

st.markdown("-------------------------------")

groq_api_key = st.secrets["GROQ_API_KEY"]

# Store API key in session state
if groq_api_key:
    st.session_state["groq_api_key"] = groq_api_key
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
