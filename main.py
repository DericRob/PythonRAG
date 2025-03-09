#!/usr/bin/env python3
"""
Content Creation Assistant with RAG
- Uses Llama 3.2 via Ollama
- Stores document embeddings in Chroma vector database 
- Supports multiple document types (.pdf, .txt, .csv, .docx, etc.)
"""
import os
import argparse
import subprocess
import sys
import time
import webbrowser
import requests
import socket
from threading import Timer

def check_port_in_use(port):
    """Check if the specified port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        # Check for required packages
        import langchain_chroma
        
        # Try to import Ollama from any known path
        ollama_imported = False
        try:
            from langchain_ollama import Ollama
            ollama_imported = True
            print("✅ Successfully imported Ollama from langchain_ollama")
        except ImportError:
            try:
                from langchain_community.llms.ollama import Ollama
                ollama_imported = True
                print("✅ Successfully imported Ollama from langchain_community.llms.ollama")
            except ImportError:
                try:
                    from langchain.llms.ollama import Ollama
                    ollama_imported = True
                    print("✅ Successfully imported Ollama from langchain.llms.ollama")
                except ImportError:
                    print("❌ Could not import Ollama from any known path")
                    print("   Please install langchain_ollama: pip install langchain_ollama")
                    return False
        
        # Check if Ollama is running
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code != 200:
                print("❌ Ollama is not responding correctly")
                print("   Please make sure Ollama is running properly")
                return False
            print(f"✅ Ollama is running (version: {response.json().get('version', 'unknown')})")
        except:
            print("❌ Could not connect to Ollama at http://localhost:11434")
            print("   Please make sure Ollama is installed and running")
            return False
            
        # Check for required models
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                
                # Check for LLM model
                if "llama3.2:3b" not in model_names:
                    print("❌ Required model 'llama3.2:3b' not found")
                    print("   Please run: ollama pull llama3.2:3b")
                    return False
                print("✅ Found required LLM model: llama3.2:3b")
                
                # Check for embedding model
                if "nomic-embed-text:latest" not in model_names:
                    print("❌ Required embedding model 'nomic-embed-text' not found")
                    print("   Please run: ollama pull nomic-embed-text")
                    return False
                print("✅ Found required embedding model: nomic-embed-text")
            else:
                print("❌ Could not get list of models from Ollama")
                return False
        except:
            print("❌ Could not check available models in Ollama")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Please install required packages: pip install -r requirements.txt")
        return False

def setup_directories():
    """Ensure required directories exist."""
    for directory in ["data", "static", "chroma"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created '{directory}' directory")

def populate_database(reset=False):
    """Run the database population script."""
    cmd = [sys.executable, "populate_database.py"]
    if reset:
        cmd.append("--reset")
    
    print("Populating vector database...")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error populating database: {e}")
        return False

def open_browser(url):
    """Open the browser to the specified URL."""
    try:
        webbrowser.open(url)
    except:
        print(f"Could not open browser automatically. Please navigate to {url}")

def run_web_server(port=5000, debug=False):
    """Run the Flask web server."""
    try:
        # Check if port is in use
        if check_port_in_use(port):
            print(f"Warning: Port {port} is already in use. Trying to use it anyway.")
        
        # Import app
        from app import app
        
        # Open browser after delay
        app_url = f"http://localhost:{port}"
        Timer(2, open_browser, args=[app_url]).start()
        
        print(f"Starting web server on {app_url}")
        app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
    except ImportError as e:
        print(f"Error importing app.py: {e}")
        return False
    except Exception as e:
        print(f"Error starting web server: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Content Creation Assistant with RAG")
    parser.add_argument("--reset", action="store_true", help="Reset the vector database")
    parser.add_argument("--populate-only", action="store_true", help="Only populate the database, don't start web server")
    parser.add_argument("--force", action="store_true", help="Skip dependency checks and force execution")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the web server on")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Content Creation Assistant with RAG")
    print("=" * 60)
    
    # Check dependencies unless force flag is used
    if not args.force and not check_dependencies():
        print("Please resolve dependency issues before continuing.")
        print("You can bypass with: python main.py --force")
        return False
    
    # Setup directories
    setup_directories()
    
    # Populate database
    if not populate_database(reset=args.reset):
        print("Database population failed.")
        return False
    
    # If --populate-only flag is provided, exit now
    if args.populate_only:
        print("Database populated successfully.")
        return True
    
    # Run web server
    print("System ready! Starting web interface...")
    run_web_server(port=args.port, debug=args.debug)
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()