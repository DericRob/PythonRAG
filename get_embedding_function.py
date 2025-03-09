"""Get embedding function from Ollama with multiple import path support."""

def get_embedding_function():
    """
    Returns an embedding function using Ollama's embedding model.
    This function handles multiple import paths for flexibility.
    """
    # Try multiple import paths for better compatibility
    embedding_class = None
    
    # Attempt to import from langchain_ollama (preferred)
    try:
        from langchain_ollama import OllamaEmbeddings
        embedding_class = OllamaEmbeddings
        print("Using OllamaEmbeddings from langchain_ollama")
    except ImportError:
        # Fall back to langchain_community
        try:
            from langchain_community.embeddings import OllamaEmbeddings
            embedding_class = OllamaEmbeddings
            print("Using OllamaEmbeddings from langchain_community.embeddings")
        except ImportError:
            # Try legacy path
            try:
                from langchain.embeddings import OllamaEmbeddings
                embedding_class = OllamaEmbeddings
                print("Using OllamaEmbeddings from langchain.embeddings (legacy path)")
            except ImportError:
                raise ImportError("Could not import OllamaEmbeddings from any known path. Please install langchain_ollama.")
    
    # Create the embedding function
    try:
        embeddings = embedding_class(model="nomic-embed-text")
        return embeddings
    except Exception as e:
        error_msg = f"Error initializing embeddings: {str(e)}"
        error_msg += "\nPlease ensure Ollama is running and the nomic-embed-text model is installed."
        error_msg += "\nRun: ollama pull nomic-embed-text"
        raise RuntimeError(error_msg)

# Test function if run directly
if __name__ == "__main__":
    try:
        embedding_function = get_embedding_function()
        test_text = "This is a test sentence to verify embeddings are working."
        embeddings = embedding_function.embed_query(test_text)
        
        print(f"Successfully generated embeddings with shape: {len(embeddings)}")
        print(f"First 5 values: {embeddings[:5]}")
        print("\nEmbedding function is working correctly!")
    except Exception as e:
        print(f"Error: {str(e)}")