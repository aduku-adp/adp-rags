import streamlit as st
import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

# Streamlit Config
st.set_page_config(page_title="Pizza RAG", page_icon="🍕", layout="centered")

# Environment
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
OLLAMA_URL = os.getenv("OLLAMA", "http://ollama-resto:11434")

# LLM + Embeddings


@st.cache_resource
def load_models():
    llm = OllamaLLM(model="llama3.2", base_url=OLLAMA_URL)

    embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)

    vector_store = Chroma(
        collection_name="restaurant_reviews",
        embedding_function=embeddings,
        host=CHROMA_HOST,
        port=CHROMA_PORT,
    )

    return llm, vector_store


llm, vector_store = load_models()

retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# Prompt

template = """
You are an expert in answering questions about a pizza restaurant.

Here are some relevant reviews:
{reviews}

Here is the question to answer:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

# UI

st.title("🍕 Pizza Restaurant RAG")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me anything about the restaurant reviews!",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat Input
if question := st.chat_input("Ask your question"):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    # Retrieve docs
    docs = retriever.invoke(question)
    reviews_text = "\n\n".join([doc.page_content for doc in docs])

    # Generate response
    response = chain.invoke({"reviews": reviews_text, "question": question})

    # Save and display
    st.session_state.messages.append({"role": "assistant", "content": response})

    st.chat_message("assistant").write(response)
