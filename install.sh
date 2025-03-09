#!/bin/bash
echo "================================================="
echo "Content Creation Assistant - Installation Script"
echo "================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9 or higher and try again"
    exit 1
fi

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install core dependencies
echo "Installing core dependencies..."
pip install wheel setuptools numpy

# Install critical packages first
echo "Installing main packages..."
pip install langchain langchain_ollama langchain_chroma chromadb flask flask-cors requests pandas

# Install document handling packages
echo "Installing document handling packages..."
pip install pypdf docx2txt python-docx openpyxl

# Install remaining requirements
echo "Installing additional dependencies..."
pip install langchain_community langchain-text-splitters python-dotenv

# Create directories
echo "Creating directories..."
mkdir -p data chroma static

echo
echo "Installation completed!"
echo
echo "To run the application:"
echo "1. Make sure Ollama is installed and running"
echo "2. Pull required models: ollama pull llama3:3b nomic-embed-text"
echo "3. Add your documents to the 'data' folder"
echo "4. Run: python main.py --reset"
echo
echo "For troubleshooting, run: python troubleshoot.py"
echo

echo "Press Enter to continue..."
read