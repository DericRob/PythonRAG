import argparse
import os
import shutil
import hashlib
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_chroma import Chroma

from get_embedding_function import get_embedding_function
from document_loader import load_documents

CHROMA_PATH = "chroma"
DATA_PATH = "data"

def main():
    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    
    if args.reset:
        print("✨ Clearing Database")
        clear_database()
    
    # Create directories if they don't exist
    for dir_path in [CHROMA_PATH, DATA_PATH]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")

    # Create (or update) the data store.
    print("📚 Loading documents from data directory...")
    documents = load_documents(DATA_PATH)
    
    if not documents:
        print("⚠️ No documents found. Please add documents to the data directory.")
        return
        
    print(f"🔪 Splitting {len(documents)} documents into chunks...")
    chunks = split_documents(documents)
    
    print(f"💾 Adding {len(chunks)} chunks to the vector database...")
    add_to_chroma(chunks)
    
    print("✅ Database population complete!")


def split_documents(documents: list[Document]):
    """Split documents into smaller chunks for better retrieval."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    """Add document chunks to the Chroma vector database."""
    # Ensure the chroma directory exists
    if not os.path.exists(CHROMA_PATH):
        os.makedirs(CHROMA_PATH)
    
    # Load the embedding function
    embedding_function = get_embedding_function()
    
    # Load or create the database
    db = Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embedding_function
    )

    # Calculate unique IDs for chunks
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get existing document IDs
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding {len(new_chunks)} new document chunks")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # The persist() method is no longer needed with the new langchain_chroma
        # Chroma automatically persists when using persist_directory
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    """
    Create unique IDs for each chunk based on source, content and position.
    This works for all document types, not just PDFs with page numbers.
    """
    processed_chunks = []
    
    # Group chunks by source
    source_chunks = {}
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        if source not in source_chunks:
            source_chunks[source] = []
        source_chunks[source].append(chunk)
    
    # Process each source
    for source, chunks_for_source in source_chunks.items():
        for i, chunk in enumerate(chunks_for_source):
            # Generate a content hash to help with uniqueness
            content_hash = hashlib.md5(chunk.page_content.encode()).hexdigest()[:8]
            
            # Get page number if it exists (PDF documents)
            page = chunk.metadata.get("page", "")
            
            # Create a unique ID
            if page:
                chunk_id = f"{source}:p{page}:c{i}:{content_hash}"
            else:
                chunk_id = f"{source}:c{i}:{content_hash}"
            
            # Add it to the chunk metadata
            chunk.metadata["id"] = chunk_id
            processed_chunks.append(chunk)
    
    return processed_chunks


def clear_database():
    """Remove the Chroma database directory."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        print(f"Removed directory: {CHROMA_PATH}")


if __name__ == "__main__":
    main()