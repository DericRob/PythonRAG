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
import requests  # For API calls
from threading import Timer

def check_dependencies():
    """Check if all required dependencies are installed with comprehensive error handling."""
    # List of packages to check and import
    packages_to_check = [
        "langchain_chroma",
        "flask",
        "flask_cors",
        "chromadb",
        "langchain_text_splitters"
    ]
    
    # Check core packages first
    missing_packages = []
    for package in packages_to_check:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("   Run: pip install " + " ".join(missing_packages))
        return False
        
    # Specifically check Ollama with multiple fallback paths
    ollama_imported = False
    ollama_class = None
    import_errors = []
    
    global Ollama
    # Try all possible import paths
    try:
        # First try the recommended import
        from langchain_ollama import Ollama
        ollama_imported = True
        ollama_class = Ollama
        print("✅ Successfully imported Ollama from langchain_ollama")
    except ImportError as e:
        import_errors.append(f"langchain_ollama: {str(e)}")
        
        try:
            # Try alternative import from community package
            from langchain_community.llms.ollama import Ollama
            ollama_imported = True
            ollama_class = Ollama
            print("✅ Successfully imported Ollama from langchain_community.llms.ollama")
        except ImportError as e:
            import_errors.append(f"langchain_community.llms.ollama: {str(e)}")
            
            try:
                # Try another alternative deprecated path
                from langchain.llms.ollama import Ollama
                ollama_imported = True
                ollama_class = Ollama
                print("✅ Successfully imported Ollama from langchain.llms.ollama (deprecated path)")
            except ImportError as e:
                import_errors.append(f"langchain.llms.ollama: {str(e)}")
                
    if not ollama_imported:
        print("❌ Failed to import Ollama from any of the known paths")
        print("   Import errors:")
        for error in import_errors:
            print(f"   - {error}")
        print("\n💡 Solution: Install the langchain_ollama package:")
        print("   pip install langchain_ollama")
        print("\n   If that doesn't work, try installing the full langchain suite:")
        print("   pip install langchain langchain_community")
        
        # Try to auto-fix by installing the package
        try_fix = input("\nWould you like me to attempt to install the missing package? (y/n): ").lower()
        if try_fix == 'y':
            print("\nAttempting to install langchain_ollama...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "langchain_ollama"])
                print("✅ Installation successful! Please restart the application.")
            except subprocess.CalledProcessError:
                print("❌ Installation failed.")
                print("   Try manually with: pip install langchain_ollama")
                
        return False
    
    # Store the Ollama class globally for later use
    Ollama = ollama_class
    
    # Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code != 200:
            print("⚠️ Warning: Ollama server responded with status code", response.status_code)
            print("   Please make sure Ollama is running properly.")
            return False
        print(f"✅ Ollama server is running (version: {response.json().get('version', 'unknown')})")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama server at http://localhost:11434")
        print("   Please make sure Ollama is installed and running.")
        print("   You can download Ollama from: https://ollama.ai/")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama server: {str(e)}")
        return False
            
    # Check for required models
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            # Check for Llama model
            llm_model_name = "llama3.2:3b"
            embed_model_name = "nomic-embed-text:latest"
            
            model_names = [model.get("name") for model in models]
            print(f"Available models: {', '.join(model_names)}")
            
            if llm_model_name not in model_names:
                print(f"❌ Required model '{llm_model_name}' not found in Ollama")
                print(f"   Please run: ollama pull {llm_model_name}")
                return False
            else:
                print(f"✅ Found required LLM model: {llm_model_name}")
                
            if embed_model_name not in model_names:
                print(f"❌ Required embedding model '{embed_model_name}' not found in Ollama")
                print(f"   Please run: ollama pull {embed_model_name}")
                return False
            else:
                print(f"✅ Found required embedding model: {embed_model_name}")
        else:
            print(f"⚠️ Warning: Failed to get list of models from Ollama (status code: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama models: {str(e)}")
        return False
        
    return True


def setup_directories():
    """Ensure required directories exist."""
    directories = {
        "data": "📁 Data directory for source documents",
        "static": "📁 Static directory for web assets",
        "chroma": "📁 Chroma directory for vector database"
    }
    
    for dir_name, description in directories.items():
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created {description}")
        else:
            print(f"✅ Found {description}")


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
    try:
        # Dynamically import app to avoid import errors
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app
        
        # Open browser after 1.5 seconds to ensure server has started
        Timer(1.5, open_browser, args=["http://localhost:5000"]).start()
        
        print("🚀 Starting web server...")
        app.run(debug=False, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error importing app.py: {e}")
        print("   Please check that app.py exists and contains a valid Flask application.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Content Creation Assistant with RAG")
    parser.add_argument("--reset", action="store_true", help="Reset the vector database")
    parser.add_argument("--populate-only", action="store_true", help="Only populate the database, don't start web server")
    parser.add_argument("--force", action="store_true", help="Skip dependency checks and force execution")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🤖 Content Creation Assistant with RAG")
    print("=" * 60)
    
    # Check dependencies unless force flag is used
    if not args.force and not check_dependencies():
        print("\n❌ Please resolve the dependency issues before continuing.")
        print("   You can bypass this check with: python main.py --force")
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
    try:
        main()
    except KeyboardInterrupt:
        print("\n💡 Program interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()