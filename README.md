# Content Creation Assistant with RAG

This application uses Retrieval-Augmented Generation (RAG) to create content based on your documents and user queries. The system uses free, open-source tools and models to deliver high-quality results similar to commercial services.

## Features

- **Document Analysis**: Automatically processes multiple document types (.pdf, .txt, .docx, .csv, .xlsx, etc.)
- **Advanced RAG**: Chunks documents intelligently and retrieves relevant information for responses
- **Multiple Content Types**: Generates articles, social media posts, and video scripts
- **Free Models**: Uses Llama 3.2 3B and open-source embedding models
- **Modern UI**: Clean, responsive web interface for content generation
- **Vector Storage**: Stores embeddings in Chroma vector database for fast retrieval

## Requirements

1. Python 3.9+ installed
2. [Ollama](https://ollama.ai) installed and running
3. Llama 3.2 3B and nomic-embed-text models installed via Ollama
4. Python packages listed in `requirements.txt`

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama

Download and install [Ollama](https://ollama.ai).

### 3. Download Required Models

```bash
ollama pull llama3:3b
ollama pull nomic-embed-text
```

### 4. Add Your Documents

Place all documents you want to use as knowledge sources in the `data` folder:
- PDF files (.pdf)
- Word documents (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- CSV files (.csv)
- Text files (.txt)
- And more...

### 5. Run the Application

To reset the database and start fresh:
```bash
python main.py --reset
```

To update the database with new documents without resetting:
```bash
python main.py
```

## Usage

1. The web interface will automatically open in your browser (http://localhost:5000)
2. Enter a question or topic in the input field
3. Add any additional context if needed
4. Click "Generate Content"
5. View and copy the generated article, social media post, and video script

## Structure

- `main.py`: Main script to run the entire application
- `app.py`: Flask web server that handles API requests
- `populate_database.py`: Processes documents and stores them in the vector database
- `query_data.py`: Contains the logic for querying the RAG system
- `document_loader.py`: Handles loading and processing various document types
- `get_embedding_function.py`: Provides embedding functions for vectorization
- `static/`: Contains web interface files
- `data/`: Directory for source documents 
- `chroma/`: Vector database storage

## Customization

You can modify several aspects of the system:
- Adjust the chunk size in `populate_database.py` 
- Change the prompt templates in `query_data.py`
- Update the UI in the `static/index.html` file
- Switch to different models by modifying the model names in the code

## Troubleshooting

If you encounter issues:
1. Make sure Ollama is running by going to http://localhost:11434 in your browser
2. Check you've downloaded the required models with `ollama list`
3. Examine the log output for any specific errors
4. Try restarting the application with the `--reset` flag to rebuild the database

## License

This project uses open-source components and is intended for educational and personal use.