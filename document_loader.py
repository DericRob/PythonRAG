import os
from typing import List
from langchain.schema.document import Document
from langchain_community.document_loaders import (
    PyPDFDirectoryLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
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
                try:
                    # Custom Excel handling with pandas
                    import pandas as pd
                    
                    # Read all sheets
                    xlsx = pd.ExcelFile(file_path)
                    sheet_names = xlsx.sheet_names
                    
                    for sheet_name in sheet_names:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        # Convert dataframe to text
                        text = f"Sheet: {sheet_name}\n\n{df.to_string(index=False)}"
                        
                        # Create a document
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": file_path,
                                "sheet": sheet_name,
                                "rows": len(df),
                                "columns": len(df.columns)
                            }
                        )
                        all_documents.append(doc)
                    
                    print(f"Loaded Excel file {filename} with {len(sheet_names)} sheets")
                except Exception as e:
                    print(f"Error loading Excel file {filename}: {str(e)}")
                
            # Add support for .doc files if needed
            elif filename.endswith('.doc'):
                # We need to use a different approach for .doc files
                # This may require additional dependencies
                print(f"Warning: .doc file format requires additional configuration: {filename}")
                
        except Exception as e:
            print(f"Error loading {filename}: {str(e)}")
    
    print(f"Loaded {len(all_documents)} documents in total")
    return all_documents