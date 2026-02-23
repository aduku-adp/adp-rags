import hashlib
import io
import os
import uuid
from typing import Dict, List

import boto3
import pandas as pd
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient, models

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "restaurant_reviews")
OLLAMA_URL = os.getenv("OLLAMA", "http://localhost:11434")
S3_BUCKET = os.getenv("S3_BUCKET", "adp-rags")
S3_PREFIX = os.getenv("S3_PREFIX", "")


def load_csv_rows_from_s3(bucket: str, prefix: str) -> List[Dict]:
    s3_client = boto3.client("s3")

    csv_keys = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.lower().endswith(".csv"):
                csv_keys.append(key)

    if not csv_keys:
        raise ValueError(f"No CSV files found in s3://{bucket}/{prefix}")

    rows = []
    for key in sorted(csv_keys):
        response = s3_client.get_object(Bucket=bucket, Key=key)
        body = response["Body"].read().decode("utf-8")
        df = pd.read_csv(io.StringIO(body))

        required_columns = {"Title", "Review", "Rating", "Date"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValueError(f"{key} is missing required columns: {sorted(missing_columns)}")

        for index, row in df.iterrows():
            rows.append(
                {
                    "source_file": key,
                    "source_row": int(index),
                    "title": str(row["Title"]),
                    "review": str(row["Review"]),
                    "rating": row["Rating"],
                    "date": str(row["Date"]),
                }
            )

    return rows


def point_id(source_file: str, source_row: int) -> str:
    # Qdrant accepts integer or UUID point IDs.
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_file}:{source_row}"))


def content_fingerprint(title: str, review: str, rating, date_value: str) -> str:
    raw = f"{title}|{review}|{rating}|{date_value}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def batched(values: List[str], size: int):
    for i in range(0, len(values), size):
        yield values[i : i + size]


def list_existing_ids_for_source_file(client: QdrantClient, collection_name: str, source_file: str) -> set[str]:
    ids = set()
    offset = None
    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_file",
                        match=models.MatchValue(value=source_file),
                    )
                ]
            ),
            with_payload=False,
            with_vectors=False,
            limit=1000,
            offset=offset,
        )
        if not points:
            break

        for point in points:
            ids.add(str(point.id))

        if offset is None:
            break

    return ids


rows = load_csv_rows_from_s3(S3_BUCKET, S3_PREFIX)

candidates = []
ids_by_source_file: Dict[str, set[str]] = {}
for row in rows:
    text = f"{row['title']} {row['review']}"
    pid = point_id(row["source_file"], row["source_row"])
    fingerprint = content_fingerprint(row["title"], row["review"], row["rating"], row["date"])

    payload = {
        "text": text,
        "title": row["title"],
        "rating": row["rating"],
        "date": row["date"],
        "source_file": row["source_file"],
        "source_row": row["source_row"],
        "source_bucket": S3_BUCKET,
        "source_prefix": S3_PREFIX,
        "fingerprint": fingerprint,
    }

    candidates.append({"id": pid, "text": text, "payload": payload, "source_file": row["source_file"]})
    ids_by_source_file.setdefault(row["source_file"], set()).add(pid)

client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
collection_exists = client.collection_exists(collection_name=QDRANT_COLLECTION)

existing_fingerprints = {}
if collection_exists:
    all_ids = [c["id"] for c in candidates]
    for id_batch in batched(all_ids, 500):
        points = client.retrieve(
            collection_name=QDRANT_COLLECTION,
            ids=id_batch,
            with_payload=True,
            with_vectors=False,
        )
        for point in points:
            existing_fingerprints[str(point.id)] = (point.payload or {}).get("fingerprint")

changed_or_new = [
    c
    for c in candidates
    if existing_fingerprints.get(c["id"]) != c["payload"]["fingerprint"]
]

stale_ids = []
if collection_exists:
    for source_file, current_ids in ids_by_source_file.items():
        existing_ids_for_file = list_existing_ids_for_source_file(client, QDRANT_COLLECTION, source_file)
        stale_ids.extend(sorted(existing_ids_for_file - current_ids))

if stale_ids:
    for id_batch in batched(stale_ids, 500):
        client.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=models.PointIdsList(points=id_batch),
            wait=True,
        )

if changed_or_new:
    embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)
    texts = [c["text"] for c in changed_or_new]
    vectors = embeddings.embed_documents(texts)

    if not collection_exists:
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=len(vectors[0]),
                distance=models.Distance.COSINE,
            ),
        )

    points = [
        models.PointStruct(id=changed_or_new[i]["id"], vector=vectors[i], payload=changed_or_new[i]["payload"])
        for i in range(len(changed_or_new))
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)

print(
    f"Incremental sync complete for '{QDRANT_COLLECTION}': total_rows={len(candidates)}, "
    f"upserted={len(changed_or_new)}, deleted={len(stale_ids)}"
)
