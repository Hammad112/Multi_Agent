import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler



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

    <div class="animated-title">Langchain: Chat with Search</div>
    <div class="animated-subtitle">Ask Anything — We'll Search Wikipedia, Arxiv, and the Web for You</div>
""", unsafe_allow_html=True)



# Initialize tools
api_wrapper_wiki = WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=500)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

api_wrapper_arxiv = ArxivAPIWrapper(top_k_results=2, doc_content_chars_max=500)
arxiv = ArxivQueryRun(api_wrapper=api_wrapper_arxiv)

search = DuckDuckGoSearchRun(name='Search')

# Access Groq API key from session state
groq_api_key = st.session_state.get("groq_api_key")
if not groq_api_key:
    st.error("Please enter a Groq API key on the home page.")
    st.stop()

# Initialize LLM
llm = ChatGroq(groq_api_key=groq_api_key, model="gemma2-9b-It", streaming=True)

if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {
            'role': 'Assistant',
            'content': 'How can I help you?'
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

if prompt := st.chat_input(placeholder='Ask me anything!'):
    st.session_state.messages.append({'role': 'User', 'content': prompt})
    st.chat_message('User').write(prompt)

    # Initialize agent
    tools = [wiki, arxiv, search]
    agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True, handling_parse_errors=True)

    with st.chat_message('Assistant'):
        st_callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
        response = agent.run(prompt, callbacks=[st_callback])
        st.session_state.messages.append({'role': 'Assistant', 'content': response})
        st.write(response)