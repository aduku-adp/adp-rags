import sys
import types
from io import BytesIO
from types import SimpleNamespace
from uuid import UUID

import pytest


def _install_import_stubs():
    qdrant_mod = types.ModuleType("qdrant_client")

    class _Noop:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class _Distance:
        COSINE = "cosine"

    models = types.SimpleNamespace(
        Filter=_Noop,
        FieldCondition=_Noop,
        MatchValue=_Noop,
        PointIdsList=_Noop,
        VectorParams=_Noop,
        Distance=_Distance,
        PointStruct=_Noop,
    )
    qdrant_mod.QdrantClient = object
    qdrant_mod.models = models
    sys.modules["qdrant_client"] = qdrant_mod


_install_import_stubs()
from tools import load_embeddings as mod


def test_point_id_is_deterministic_uuid():
    first = mod.point_id("reviews/file.csv", 7)
    second = mod.point_id("reviews/file.csv", 7)
    third = mod.point_id("reviews/file.csv", 8)

    assert first == second
    assert first != third
    UUID(first)


def test_content_fingerprint_changes_when_content_changes():
    a = mod.content_fingerprint("Title", "Review", 5, "2025-01-01")
    b = mod.content_fingerprint("Title", "Review", 4, "2025-01-01")
    c = mod.content_fingerprint("Title", "Review", 5, "2025-01-01")

    assert a != b
    assert a == c


def test_batched_splits_values_by_batch_size():
    values = ["a", "b", "c", "d", "e"]
    chunks = list(mod.batched(values, 2))
    assert chunks == [["a", "b"], ["c", "d"], ["e"]]


def test_load_csv_rows_from_s3_reads_all_csv_objects(monkeypatch):
    csv_one = b"Title,Review,Rating,Date\nA,Good,5,2025-01-01\n"
    csv_two = b"Title,Review,Rating,Date\nB,Okay,3,2025-02-02\n"

    class FakePaginator:
        def paginate(self, **kwargs):
            assert kwargs["Bucket"] == "adp-rags"
            assert kwargs["Prefix"] == "reviews/"
            yield {"Contents": [{"Key": "reviews/part-2.csv"}, {"Key": "reviews/ignore.txt"}]}
            yield {"Contents": [{"Key": "reviews/part-1.csv"}]}

    class FakeS3:
        def get_paginator(self, name):
            assert name == "list_objects_v2"
            return FakePaginator()

        def get_object(self, Bucket, Key):
            assert Bucket == "adp-rags"
            payload = csv_one if Key.endswith("part-1.csv") else csv_two
            return {"Body": BytesIO(payload)}

    monkeypatch.setattr(mod.boto3, "client", lambda service: FakeS3())

    rows = mod.load_csv_rows_from_s3("adp-rags", "reviews/")

    assert len(rows) == 2
    assert rows[0]["source_file"] == "reviews/part-1.csv"
    assert rows[1]["source_file"] == "reviews/part-2.csv"
    assert rows[0]["source_row"] == 0


def test_load_csv_rows_from_s3_raises_when_missing_required_columns(monkeypatch):
    bad_csv = b"Title,Review,Date\nA,Good,2025-01-01\n"

    class FakePaginator:
        def paginate(self, **kwargs):
            yield {"Contents": [{"Key": "reviews/bad.csv"}]}

    class FakeS3:
        def get_paginator(self, name):
            return FakePaginator()

        def get_object(self, Bucket, Key):
            return {"Body": BytesIO(bad_csv)}

    monkeypatch.setattr(mod.boto3, "client", lambda service: FakeS3())

    with pytest.raises(ValueError, match="missing required columns"):
        mod.load_csv_rows_from_s3("adp-rags", "reviews/")


def test_list_existing_ids_for_source_file_scrolls_until_done():
    point_page_1 = [SimpleNamespace(id="id-1"), SimpleNamespace(id="id-2")]
    point_page_2 = [SimpleNamespace(id="id-3")]

    class FakeClient:
        def __init__(self):
            self.calls = 0

        def scroll(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                return point_page_1, "next"
            return point_page_2, None

    client = FakeClient()
    ids = mod.list_existing_ids_for_source_file(client, "restaurant_reviews", "reviews/part-1.csv")

    assert ids == {"id-1", "id-2", "id-3"}
