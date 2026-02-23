import sys
import types
from types import SimpleNamespace


def _install_import_stubs():
    streamlit = types.ModuleType("streamlit")
    streamlit.cache_resource = lambda fn: fn
    streamlit.session_state = {}
    sys.modules["streamlit"] = streamlit

    prompts_mod = types.ModuleType("langchain_core.prompts")

    class _PromptTemplate:
        @staticmethod
        def from_template(_):
            return _PromptTemplate()

        def __or__(self, _llm):
            return _llm

    prompts_mod.ChatPromptTemplate = _PromptTemplate
    sys.modules["langchain_core.prompts"] = prompts_mod

    ollama_mod = types.ModuleType("langchain_ollama")
    ollama_mod.OllamaEmbeddings = object
    sys.modules["langchain_ollama"] = ollama_mod

    ollama_llm_mod = types.ModuleType("langchain_ollama.llms")
    ollama_llm_mod.OllamaLLM = object
    sys.modules["langchain_ollama.llms"] = ollama_llm_mod

    langfuse_mod = types.ModuleType("langfuse.langchain")
    langfuse_mod.CallbackHandler = object
    sys.modules["langfuse.langchain"] = langfuse_mod

    qdrant_mod = types.ModuleType("qdrant_client")
    qdrant_mod.QdrantClient = object
    sys.modules["qdrant_client"] = qdrant_mod


_install_import_stubs()
from resto.app.main import QDRANT_COLLECTION, retrieve_reviews


class FakeEmbeddings:
    def __init__(self):
        self.queries = []

    def embed_query(self, text):
        self.queries.append(text)
        return [0.1, 0.2, 0.3]


class FakeClient:
    def __init__(self):
        self.query_calls = []

    def query_points(self, **kwargs):
        self.query_calls.append(kwargs)
        return SimpleNamespace(
            points=[
                SimpleNamespace(payload={"text": "Great crust and sauce."}),
                SimpleNamespace(payload={"rating": 5}),
                SimpleNamespace(payload=None),
                SimpleNamespace(payload={"text": "Service was quick."}),
            ]
        )


def test_retrieve_reviews_returns_only_text_payloads():
    embeddings = FakeEmbeddings()
    client = FakeClient()

    reviews = retrieve_reviews("best pizza", embeddings, client, top_k=3)

    assert reviews == ["Great crust and sauce.", "Service was quick."]
    assert embeddings.queries == ["best pizza"]

    assert len(client.query_calls) == 1
    call = client.query_calls[0]
    assert call["collection_name"] == QDRANT_COLLECTION
    assert call["limit"] == 3
    assert call["with_payload"] is True
    assert call["query"] == [0.1, 0.2, 0.3]
