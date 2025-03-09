from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    """
    Returns an embedding function using Ollama's embedding model.
    Using a local embedding model for free vector embeddings.
    """
    embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
    return embeddings