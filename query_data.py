from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import importlib.util
import logging

from get_embedding_function import get_embedding_function
from cdc_search import documents_from_cdc_search

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CHROMA_PATH = "chroma"
LLAMA_MODEL = "llama3.2:3b"  

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
    """Try multiple import paths to find the Ollama LLM class."""
    import_paths = [
        "langchain_ollama.Ollama",
        "langchain_community.llms.ollama.Ollama",
        "langchain.llms.ollama.Ollama"
    ]
    
    for path in import_paths:
        module_path, class_name = path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            OllamaClass = getattr(module, class_name)
            logger.info(f"Using Ollama from {module_path}")
            return OllamaClass
        except (ImportError, AttributeError):
            continue
    
    # If we get here, none of the imports worked
    raise ImportError("Could not import Ollama from any known path. Please install langchain_ollama.")

def split_documents(documents):
    """Split documents into smaller chunks for better retrieval."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def add_chunks_to_chroma(db, chunks):
    """Add document chunks to the Chroma vector database."""
    # Calculate unique IDs for chunks
    ids = []
    for i, chunk in enumerate(chunks):
        # Use the document ID if available, otherwise generate one
        if "id" in chunk.metadata:
            chunk_id = chunk.metadata["id"]
        else:
            source = chunk.metadata.get("source", "unknown")
            # Generate a unique suffix for this chunk
            chunk_id = f"{source}_chunk{i}"
        
        # Store the ID in the metadata and in our list
        chunk.metadata["id"] = chunk_id
        ids.append(chunk_id)
    
    # Get existing document IDs
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    
    # Only add documents that don't exist in the DB
    new_chunks = []
    new_ids = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = ids[i]
        if chunk_id not in existing_ids:
            new_chunks.append(chunk)
            new_ids.append(chunk_id)
    
    if new_chunks:
        logger.info(f"Adding {len(new_chunks)} new chunks to the vector database")
        db.add_documents(new_chunks, ids=new_ids)
    else:
        logger.info("No new chunks to add to the database")
    
    return db

def extract_core_query(query_text: str) -> str:
    """
    Extract the core query terms from a prompt.
    Removes phrases like "Write an article about" to get just the topic.
    
    Args:
        query_text: The full query text or prompt
        
    Returns:
        The extracted core query
    """
    # List of prefix phrases to remove
    prefixes = [
        "Write an informative article about:",
        "Write an informative article about",
        "Write a short social media post about:",
        "Write a short social media post about", 
        "Write a script for a video about:",
        "Write a script for a video about",
        "Create content about:",
        "Create content about",
        "Write about:",
        "Write about"
    ]
    
    # Try to remove prefixes
    clean_query = query_text
    for prefix in prefixes:
        if clean_query.startswith(prefix):
            clean_query = clean_query[len(prefix):].strip()
            logger.info(f"Removed prefix: '{prefix}' from query")
            break
    
    # Remove "Context:" and everything after it if present
    if " Context:" in clean_query:
        clean_query = clean_query.split(" Context:")[0].strip()
        logger.info(f"Removed context suffix from query")
    
    logger.info(f"Original query: '{query_text}' -> Core query: '{clean_query}'")
    return clean_query

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

        # Extract the core query for CDC search
        core_query = extract_core_query(query_text)
        
        # First, search stacks.cdc.gov for the core query (without prompt phrases)
        logger.info(f"Searching CDC Stacks for core query: {core_query}")
        cdc_documents = documents_from_cdc_search(core_query, max_results=5)
        
        if cdc_documents:
            # Split CDC documents into chunks
            logger.info(f"Splitting {len(cdc_documents)} CDC documents into chunks")
            cdc_chunks = split_documents(cdc_documents)
            
            # Add CDC chunks to the database
            add_chunks_to_chroma(db, cdc_chunks)
            logger.info(f"Added CDC document chunks to the database")

        # Search the DB for relevant documents
        results = db.similarity_search_with_score(query_text, k=5)
        
        if not results:
            return "No relevant information found in the knowledge base.", []

        # Format context from retrieved documents
        context_parts = []
        for i, (doc, score) in enumerate(results):
            source = doc.metadata.get("source", "unknown source")
            title = doc.metadata.get("title", "")
            url = doc.metadata.get("url", "")
            
            # Format source information
            source_info = f"Source: {source}"
            if title:
                source_info += f", Title: {title}"
            if url:
                source_info += f", URL: {url}"
            
            context_parts.append(f"[Document {i+1}] ({source_info}, Relevance: {score:.2f})\n{doc.page_content}")
        
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
        sources = []
        for doc, _score in results:
            source = doc.metadata.get("source", "unknown")
            title = doc.metadata.get("title", "")
            url = doc.metadata.get("url", "")
            
            source_info = source
            if title:
                source_info += f" - {title}"
            if url:
                source_info += f" ({url})"
                
            sources.append(source_info)
        
        return response_text, sources
        
    except Exception as e:
        logger.error(f"Error during RAG query: {str(e)}")
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