import os

from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "restaurant_reviews")
OLLAMA_URL = os.getenv("OLLAMA", "http://localhost:11434")

query = "Vega Sicilia Unico"

embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)
query_vector = embeddings.embed_query(query)

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
results = client.query_points(
    collection_name=QDRANT_COLLECTION,
    query=query_vector,  # vector query
    limit=5,
    with_payload=True,
)

for p in results.points:
    print(p.score, p.payload)
