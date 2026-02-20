from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import pandas as pd
import os

# Config from environment
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
OLLAMA_URL = os.getenv("OLLAMA", "http://localhost:11435")

# Load data
df = pd.read_csv("realistic_restaurant_reviews.csv")

embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)

# Connect to Chroma server
vector_store = Chroma(
    collection_name="restaurant_reviews",
    embedding_function=embeddings,
    host=CHROMA_HOST,
    port=CHROMA_PORT,
)

# Insert documents (optional)
documents = []
ids = []

for i, row in df.iterrows():
    document = Document(
        page_content=row["Title"] + " " + row["Review"],
        metadata={"rating": row["Rating"], "date": row["Date"]},
        id=str(i),
    )
    documents.append(document)
    ids.append(str(i))

vector_store.add_documents(documents=documents, ids=ids)

# Retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
