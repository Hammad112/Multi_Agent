import streamlit as st

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


HF_API_KEY = st.secrets["HF_API_KEY"]


# Streamlit UI
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

    <div class="animated-title">Langchain: 🧠 Conversational RAG with PDF</div>
    <div class="animated-subtitle">Ask questions based on the uploaded PDF content.</div>
""", unsafe_allow_html=True)


api_key = st.session_state.get("GROQ_API_KEY")

if api_key:
    session_id = st.text_input("🆔 Session ID", value="Default")

    if 'store' not in st.session_state:
        st.session_state['store'] = {}

    # Sidebar for file upload
    with st.sidebar:
        st.header("📤 Upload")
        uploaded_files = st.file_uploader("📄 Upload PDF files", type="pdf", accept_multiple_files=True)
        if uploaded_files and 'all_docs' not in st.session_state:
            st.session_state['all_docs'] = []

    # Submit button to process documents
    if uploaded_files :
        st.session_state['all_docs'] = []
        for uploaded_file in uploaded_files:
            temp_path = f"./temp_{uuid.uuid4().hex}.pdf"
            print(f"Processing file: {uploaded_file.name}")
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            st.session_state['all_docs'].extend(docs)
        st.session_state['processed'] = True
        os.remove(temp_path) 

    if st.session_state.get('processed', False):
        print("Processing step triggered - Preparing RAG chain...")
        # Text splitting & embeddings
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(st.session_state['all_docs'])
        print(f"Split into {len(splits)} chunks")

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=None  # Ensure it's in-memory
        )

        retriever = vectorstore.as_retriever()
        print("Vector store and retriever created.")

        # Groq LLM
        llm = ChatGroq(api_key=api_key, model_name="gemma2-9b-it")
        print("LLM initialized.")

        # History-aware retriever prompt
        contextual_prompt = (
            "Given the chat history and question, reformulate it to be a standalone question.\n"
            "This helps ensure we use the right context."
        )

        prompt_context = ChatPromptTemplate.from_messages([
            ("system", contextual_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        history_aware_retriever = create_history_aware_retriever(
            retriever=retriever,
            llm=llm,
            prompt=prompt_context,
        )
        print("History-aware retriever created.")

        # Final answering prompt
        system_prompt = (
            "You are a helpful assistant. Use the documents and chat history to answer the user's question.\n"
            "If you don't know the answer, say: 'I don't know the answer.'\n"
            "Answer concisely.\n"
            "{context}"
        )

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        chain = create_stuff_documents_chain(llm, prompt=qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, chain)
        print("RAG chain created.")

        # Session-based message history
        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in st.session_state['store']:
                st.session_state['store'][session_id] = ChatMessageHistory()
            return st.session_state['store'][session_id]

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history=get_session_history,
            history_messages_key='chat_history',
            input_messages_key='input',
            output_messages_key='answer'
        )
        print("Conversational RAG chain initialized.")

        # Question input
        user_input = st.text_input("💬 Ask a question about the PDF")

        if user_input:
            session_history = get_session_history(session_id)
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}},
            )
            print(f"Response generated: {response['answer']}")
            st.success(f"🤖 Assistant: {response['answer']}")

            # Show chat history
            st.markdown("### 🧾 Chat History")
            for msg in session_history.messages:
                st.markdown('-----------------------------------')
                if msg.type == "human":
                    st.markdown(f"**You:** {msg.content}")
                elif msg.type == "ai":
                    st.markdown(f"**Assistant:** {msg.content}")

else:
    st.warning("Please enter your Groq API key to continue.")
