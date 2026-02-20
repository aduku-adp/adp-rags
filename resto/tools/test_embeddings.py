from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large", base_url="http://localhost:11435"
)

vector_store = Chroma(
    collection_name="restaurant_reviews",
    embedding_function=embeddings,
    host="localhost",
    port=8000,
)

results = vector_store.similarity_search("Vega Sicilia Unico", k=5)

print(results)
