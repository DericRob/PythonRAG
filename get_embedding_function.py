"""
Get embedding function from Ollama with multiple import path support.
"""

def get_embedding_function():
    """
    Returns an embedding function using Ollama's embedding model.
    This function handles multiple import paths for flexibility.
    
    Returns:
        An embedding function compatible with Chroma
    
    Raises:
        ImportError: If no embedding function could be loaded
    """
    # Try multiple import paths for better compatibility
    embedding_class = None
    import_errors = []
    
    # Attempt to import from langchain_ollama (preferred)
    try:
        from langchain_ollama import OllamaEmbeddings
        embedding_class = OllamaEmbeddings
        print("✅ Using OllamaEmbeddings from langchain_ollama")
    except ImportError as e:
        import_errors.append(f"langchain_ollama.OllamaEmbeddings: {str(e)}")
        
        # Fall back to langchain_community
        try:
            from langchain_community.embeddings import OllamaEmbeddings
            embedding_class = OllamaEmbeddings
            print("✅ Using OllamaEmbeddings from langchain_community.embeddings")
        except ImportError as e:
            import_errors.append(f"langchain_community.embeddings.OllamaEmbeddings: {str(e)}")
            
            # Try legacy path
            try:
                from langchain.embeddings import OllamaEmbeddings
                embedding_class = OllamaEmbeddings
                print("✅ Using OllamaEmbeddings from langchain.embeddings (legacy path)")
            except ImportError as e:
                import_errors.append(f"langchain.embeddings.OllamaEmbeddings: {str(e)}")
    
    # If no embedding class was found, raise a helpful error
    if embedding_class is None:
        error_msg = "Failed to import OllamaEmbeddings from any known path:\n"
        error_msg += "\n".join([f"- {err}" for err in import_errors])
        error_msg += "\n\nPlease install one of the following packages:"
        error_msg += "\n- pip install langchain_ollama"
        error_msg += "\n- pip install langchain-community"
        raise ImportError(error_msg)
    
    # Create the embedding function
    try:
        embeddings = embedding_class(model="nomic-embed-text")
        # Test if the embeddings are working by embedding a simple text
        test = embeddings.embed_query("test")
        if isinstance(test, list) and len(test) > 0:
            return embeddings
        else:
            raise ValueError("Embedding test failed - returned empty or invalid embedding")
    except Exception as e:
        error_msg = f"Error initializing embeddings: {str(e)}\n"
        error_msg += "Please ensure Ollama is running and the nomic-embed-text model is installed.\n"
        error_msg += "Run: ollama pull nomic-embed-text"
        raise RuntimeError(error_msg)


# Test function if run directly
if __name__ == "__main__":
    try:
        embedding_function = get_embedding_function()
        test_text = "This is a test sentence to verify embeddings are working."
        embeddings = embedding_function.embed_query(test_text)
        
        print(f"✅ Successfully generated embeddings with shape: {len(embeddings)}")
        print(f"First 5 values: {embeddings[:5]}")
        print("\nEmbedding function is working correctly!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")