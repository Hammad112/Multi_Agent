import os
import validators
import streamlit as st
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Streamlit UI
st.set_page_config(page_title='Langchain: Summarize Text From YT or Website', page_icon='🧠')

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

    <div class="animated-title">Langchain: Summarize Text From YT or Website</div>
    <div class="animated-subtitle">Summarize any YouTube video or webpage</div>
""", unsafe_allow_html=True)


# Sidebar for API key
groq_api_key = st.session_state.get("groq_api_key")

# URL input
generic_url = st.text_input('Enter URL (YouTube or Website)', label_visibility='visible')

# Prompt template
map_reduce_prompt = '''
Provide a summary of the following content in 300 words.
Be precise and concise. Your response should be grammatically complete and error-free.

<content>
{text}
<content>
'''

prompt = PromptTemplate(template=map_reduce_prompt, input_variables=['text'])

# Main logic
if st.button('Summarize'):
    if not (groq_api_key and groq_api_key.strip()) or not (generic_url and generic_url.strip()):
        st.error('❌ Please provide both a valid URL and your API key.')
    elif not validators.url(generic_url):
        st.error('❌ Invalid URL format.')
    else:
        try:
            with st.spinner('🔍 Processing...'):
                # Load content
                if 'youtube.com' in generic_url or 'youtu.be' in generic_url:
                    try:
                        loader = YoutubeLoader.from_youtube_url(
                            generic_url,
                            language='en',
                            # add_video_info=True,     # 👈 Prevents metadata issues
                            
                        )
                        data = loader.load()
                        if not data or not data[0].page_content.strip():
                            raise ValueError("⚠️ No transcript available for this video.")
                    except Exception as e:
                        raise ValueError(f"❌ YouTube load error: {str(e)}")
                else:
                    loader = UnstructuredURLLoader(
                        urls=[generic_url],
                        ssl_verify=False,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    data = loader.load()

                # Split large content
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                split_docs = text_splitter.split_documents(data)

                # LLM init
                llm = ChatGroq(groq_api_key=groq_api_key, model="gemma2-9b-it")

                # Summarization chain
                chain = load_summarize_chain(
                    llm,
                    chain_type='map_reduce',
                    map_prompt=prompt,
                    combine_prompt=prompt,
                    verbose=True
                )

                # Final result
                summary = chain.run(split_docs)
                st.success(f"Summary:  {summary}")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
