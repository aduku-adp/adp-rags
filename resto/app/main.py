import os

import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langfuse.langchain import CallbackHandler
from qdrant_client import QdrantClient

# Environment
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "restaurant_reviews")
OLLAMA_URL = os.getenv("OLLAMA", "http://ollama-resto:11434")


@st.cache_resource
def load_models():
    llm = OllamaLLM(model="llama3.2", base_url=OLLAMA_URL)
    embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return llm, embeddings, client


def retrieve_reviews(query_text, embeddings, client, top_k=5):
    query_vector = embeddings.embed_query(query_text)
    response = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    )
    reviews = []
    for hit in response.points:
        payload = hit.payload or {}
        text = payload.get("text")
        if text:
            reviews.append(text)
    return reviews


def app():
    st.set_page_config(page_title="Pizza RAG", page_icon="🍕", layout="centered")

    llm, embeddings, client = load_models()

    template = """
You are an expert in answering questions about a pizza restaurant.

Here are some relevant reviews:
{reviews}

Here is the question to answer:
{question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm

    langfuse_handler = CallbackHandler()

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

    if question := st.chat_input("Ask your question"):
        st.session_state.messages.append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        reviews = retrieve_reviews(question, embeddings, client, top_k=5)
        reviews_text = "\n\n".join(reviews)

        invoke_config = None
        if langfuse_handler:
            invoke_config = {
                "callbacks": [langfuse_handler],
                "metadata": {"langfuse_tags": ["resto-rag", "streamlit"]},
            }

        response = chain.invoke(
            {"reviews": reviews_text, "question": question},
            config=invoke_config,
        )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)


if __name__ == "__main__":
    app()
