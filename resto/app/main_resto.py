import os
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
OLLAMA_URL = os.getenv("OLLAMA", "http://ollama-resto:11434")

model = OllamaLLM(model="llama3.2", base_url=OLLAMA_URL)

embeddings = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_URL)

# Connect to Chroma server
vector_store = Chroma(
    collection_name="restaurant_reviews",
    embedding_function=embeddings,
    host=CHROMA_HOST,
    port=CHROMA_PORT,
)
# Prompt Template

template = """
You are an expert in answering questions about a pizza restaurant.

Here are some relevant reviews:
{reviews}

Here is the question to answer:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# CLI Loop
while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")

    if question.lower() == "q":
        break

    # Retrieve relevant documents
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(question)

    # Convert documents to clean text
    reviews_text = "\n\n".join([doc.page_content for doc in docs])

    result = chain.invoke({"reviews": reviews_text, "question": question})

    print(result)
