import os
from typing import List
from langchain.schema.document import Document
from langchain_community.document_loaders import (
    PyPDFDirectoryLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
)

def load_documents(data_path: str) -> List[Document]:
    """
    Loads documents from various file formats in the specified directory.
    
    Supported formats:
    - PDF (.pdf)
    - Excel (.xlsx, .xls)
    - CSV (.csv)
    - Word (.doc, .docx)
    - Text (.txt)
    
    Args:
        data_path: Path to the directory containing the documents
        
    Returns:
        List of Document objects
    """
    all_documents = []
    
    # Ensure data directory exists
    if not os.path.exists(data_path):
        os.makedirs(data_path)
        print(f"Created data directory at {data_path}")
        return []
    
    # Load PDFs
    if any(f.endswith('.pdf') for f in os.listdir(data_path)):
        pdf_loader = PyPDFDirectoryLoader(data_path)
        all_documents.extend(pdf_loader.load())
        print(f"Loaded PDF documents from {data_path}")
    
    # Load other file types
    for filename in os.listdir(data_path):
        file_path = os.path.join(data_path, filename)
        
        # Skip directories and PDF files (already handled)
        if os.path.isdir(file_path) or filename.endswith('.pdf'):
            continue
            
        try:
            # Text files
            if filename.endswith('.txt'):
                loader = TextLoader(file_path)
                all_documents.extend(loader.load())
                
            # CSV files  
            elif filename.endswith('.csv'):
                loader = CSVLoader(file_path)
                all_documents.extend(loader.load())
                
            # Word documents
            elif filename.endswith('.docx'):
                loader = Docx2txtLoader(file_path)
                all_documents.extend(loader.load())
                
            # Excel files
            elif filename.endswith(('.xlsx', '.xls')):
                loader = UnstructuredExcelLoader(file_path, mode="elements")
                all_documents.extend(loader.load())
                
            # Add support for .doc files if needed
            elif filename.endswith('.doc'):
                # We need to use a different approach for .doc files
                # This may require additional dependencies
                print(f"Warning: .doc file format requires additional configuration: {filename}")
                
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
    
    print(f"Loaded {len(all_documents)} documents in total")
    return all_documents