"""
Query the RAG system with better error handling and multiple import paths.
"""
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
import sys
import importlib.util

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"
LLAMA_MODEL = "llama3.2:3b"

# Improved prompt template with instructions on how to respond
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Question: {question}

Instructions:
- Answer using only the information provided in the context above
- If the context doesn't contain the answer, say "I don't have enough information to answer that question"
- Be concise and direct
- Cite the relevant sources when possible
"""


def get_llm_class():
    """
    Try multiple import paths to find the Ollama LLM class.
    
    Returns:
        Ollama class or raises ImportError if not found
    """
    import_paths = [
        "langchain_ollama.Ollama",
        "langchain_community.llms.ollama.Ollama",
        "langchain.llms.ollama.Ollama"
    ]
    
    import_errors = []
    
    for path in import_paths:
        module_path, class_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            OllamaClass = getattr(module, class_name)
            print(f"✅ Successfully imported Ollama from {module_path}")
            return OllamaClass
        except (ImportError, AttributeError) as e:
            import_errors.append(f"{path}: {str(e)}")
    
    # If we get here, none of the imports worked
    error_msg = "Failed to import Ollama from any known path:\n"
    error_msg += "\n".join([f"- {err}" for err in import_errors])
    error_msg += "\n\nPlease install one of the following packages:"
    error_msg += "\n- pip install langchain_ollama"
    error_msg += "\n- pip install langchain-community"
    raise ImportError(error_msg)


def query_rag(query_text: str):
    """
    Query the RAG system with the given text.
    
    Args:
        query_text: The question or query to ask
        
    Returns:
        Tuple of (response_text, sources)
    """
    try:
        # Prepare the DB and embedding function
        embedding_function = get_embedding_function()
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

        # Search the DB for relevant documents
        results = db.similarity_search_with_score(query_text, k=5)
        
        if not results:
            return "No relevant information found in the knowledge base.", []

        # Format context from retrieved documents
        context_parts = []
        for i, (doc, score) in enumerate(results):
            source_id = doc.metadata.get("id", "unknown source")
            context_parts.append(f"[Document {i+1}] (Source: {source_id}, Relevance: {score:.2f})\n{doc.page_content}")
        
        context_text = "\n\n---\n\n".join(context_parts)
        
        # Create prompt with context and question
        prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context_text, question=query_text)
        
        # Get the appropriate Ollama class
        OllamaClass = get_llm_class()
        
        # Initialize Llama 3.2 model via Ollama
        model = OllamaClass(model=LLAMA_MODEL)
        
        # Get response from LLM
        response_text = model.invoke(prompt)
        
        # Format sources for reference
        sources = [doc.metadata.get("id", "unknown") for doc, _score in results]
        
        return response_text, sources
        
    except Exception as e:
        print(f"Error during RAG query: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"An error occurred: {str(e)}", []


def main():
    """
    Command-line interface for querying the RAG system.
    """
    import argparse
    
    # Create CLI
    parser = argparse.ArgumentParser(description="Query the RAG system")
    parser.add_argument("query_text", type=str, help="The question to ask")
    args = parser.parse_args()
    
    # Process query
    response_text, sources = query_rag(args.query_text)
    
    # Print response
    print("\n--- RESPONSE ---")
    print(response_text)
    print("\n--- SOURCES ---")
    for source in sources:
        print(f"- {source}")


if __name__ == "__main__":
    main()