import os

import pandas as pd
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient, models

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "restaurant_reviews")
OLLAMA_URL = os.getenv("OLLAMA", "http://localhost:11434")

# Load data
df = pd.read_csv("realistic_restaurant_reviews.csv")

texts = []
payloads = []
for _, row in df.iterrows():
    text = f"{row['Title']} {row['Review']}"
    texts.append(text)
    payloads.append(
        {
            "text": text,
            "rating": row["Rating"],
            "date": row["Date"],
        }
    )

embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)
vectors = embeddings.embed_documents(texts)

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

# Recreate collection for deterministic re-ingestion.
client.recreate_collection(
    collection_name=QDRANT_COLLECTION,
    vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
)

points = [
    models.PointStruct(id=i, vector=vectors[i], payload=payloads[i])
    for i in range(len(vectors))
]

client.upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)

print(f"Ingested {len(points)} points into collection '{QDRANT_COLLECTION}'.")
