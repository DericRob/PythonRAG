#!/usr/bin/env python3
"""
Content Creation Assistant with RAG
- Uses Llama 3.2 3B via Ollama
- Stores document embeddings in Chroma vector database 
- Supports multiple document types (.pdf, .txt, .csv, .docx, etc.)
"""
import os
import argparse
import subprocess
import sys
import time
import webbrowser
from threading import Timer

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        # Check for required packages
        import langchain_chroma
        
        # Make sure we can import Ollama from the correct location
        try:
            from langchain_community.llms.ollama import Ollama
        except ImportError:
            print("⚠️ Warning: Could not import Ollama from langchain_community.llms.ollama")
            print("   Please make sure langchain_community is properly installed.")
            return False
            print("⚠️ Warning: Couldn't connect to Ollama. Please make sure Ollama is installed and running.")
            print("   You can download Ollama from: https://ollama.ai/")
            return False
        
        # Check for Llama 3.2 3B model
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                if not any(model.get("name") == "llama3:3b" for model in models):
                    print("⚠️ Warning: Llama 3.2 3B model not found in Ollama.")
                    print("   Please run: ollama pull llama3:3b")
                    return False
        except:
            print("⚠️ Warning: Couldn't check available models in Ollama.")
            return False
            
        # Check for nomic-embed-text model for embeddings
        try:
            if not any(model.get("name") == "nomic-embed-text" for model in models):
                print("⚠️ Warning: nomic-embed-text embedding model not found in Ollama.")
                print("   Please run: ollama pull nomic-embed-text")
                return False
        except:
            print("⚠️ Warning: Couldn't check for embedding model in Ollama.")
            return False
        
        return True
            
    except ImportError as e:
        print(f"⚠️ Missing dependency: {e.name}")
        print("   Please install the required packages: pip install -r requirements.txt")
        return False


def setup_directories():
    """Ensure required directories exist."""
    # Create data directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
        print("📁 Created 'data' directory")
    
    # Create static directory if it doesn't exist
    if not os.path.exists("static"):
        os.makedirs("static")
        print("📁 Created 'static' directory")
    
    # Create chroma directory if it doesn't exist
    if not os.path.exists("chroma"):
        os.makedirs("chroma")
        print("📁 Created 'chroma' directory")


def populate_database(reset=False):
    """Run the database population script."""
    cmd = [sys.executable, "populate_database.py"]
    if reset:
        cmd.append("--reset")
    
    print("🔄 Populating vector database...")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error populating database: {e}")
        return False
    
    return True


def open_browser(url):
    """Open the browser to the specified URL."""
    webbrowser.open(url)


def run_web_server():
    """Run the Flask web server."""
    from app import app
    
    # Open browser after 1.5 seconds to ensure server has started
    Timer(1.5, open_browser, args=["http://localhost:5000"]).start()
    
    print("🚀 Starting web server...")
    app.run(debug=False, host='0.0.0.0', port=5000)


def main():
    parser = argparse.ArgumentParser(description="Content Creation Assistant with RAG")
    parser.add_argument("--reset", action="store_true", help="Reset the vector database")
    parser.add_argument("--populate-only", action="store_true", help="Only populate the database, don't start web server")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 Content Creation Assistant with RAG")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please resolve the dependency issues before continuing.")
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Populate database
    if not populate_database(reset=args.reset):
        print("\n❌ Database population failed.")
        sys.exit(1)
    
    # If --populate-only flag is provided, exit now
    if args.populate_only:
        print("\n✅ Database populated successfully.")
        sys.exit(0)
    
    # Run web server
    print("\n✅ System ready! Starting web interface...")
    run_web_server()


if __name__ == "__main__":
    main()