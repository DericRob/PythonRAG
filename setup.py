#!/usr/bin/env python3
"""
Setup script for Content Creation Assistant
Checks for Ollama installation and downloads required models
"""
import os
import sys
import platform
import subprocess
import webbrowser
import time

def check_ollama_installed():
    """Check if Ollama is installed and running."""
    try:
        import requests
        try:
            response = requests.get("http://localhost:11434/api/version")
            if response.status_code == 200:
                print("✅ Ollama is installed and running")
                return True
        except:
            pass
            
        # Check if Ollama is installed but not running
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
            if "ollama" in result.stdout:
                print("⚠️ Ollama is installed but not running. Please start Ollama and try again.")
                return False
        else:  # macOS or Linux
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            if result.returncode == 0:
                print("⚠️ Ollama is installed but not running. Please start Ollama and try again.")
                return False
                
        print("❌ Ollama is not installed")
        return False
    except ImportError:
        print("❌ Please install the requests package: pip install requests")
        return False


def install_ollama():
    """Provide instructions for installing Ollama."""
    print("\n=== Installing Ollama ===")
    system = platform.system()
    
    print("Ollama needs to be installed manually. Opening the Ollama website...")
    time.sleep(2)
    webbrowser.open("https://ollama.ai/download")
    
    print("\nPlease:")
    print("1. Download and install Ollama from the website")
    print("2. Start Ollama")
    print("3. Run this setup script again once Ollama is running")
    
    input("\nPress Enter once you've completed these steps or Ctrl+C to exit...")
    return check_ollama_installed()


def download_models():
    """Download the required models using Ollama."""
    models_to_download = ["llama3:3b", "nomic-embed-text"]
    
    print("\n=== Downloading Models ===")
    for model in models_to_download:
        print(f"Downloading {model}... (this may take a while)")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            print(f"✅ {model} downloaded successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to download {model}")
            return False
    
    return True


def setup_env():
    """Create necessary directories and install Python dependencies."""
    # Create directories
    for directory in ["data", "chroma", "static"]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created {directory} directory")
    
    # Install Python dependencies
    print("\n=== Installing Python Dependencies ===")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Python dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        return False
    
    return True


def main():
    print("=" * 60)
    print("🤖 Content Creation Assistant Setup")
    print("=" * 60)
    
    # Check if Ollama is installed and running
    if not check_ollama_installed():
        if not install_ollama():
            print("\n❌ Setup failed. Please install and start Ollama manually.")
            return
    
    # Download required models
    if not download_models():
        print("\n❌ Failed to download required models.")
        print("Please run the following commands manually:")
        print("ollama pull llama3:3b")
        print("ollama pull nomic-embed-text")
        return
    
    # Setup environment
    if not setup_env():
        print("\n❌ Failed to set up environment.")
        return
    
    print("\n✅ Setup completed successfully!")
    print("\nYou can now:")
    print("1. Add your documents to the 'data' folder")
    print("2. Run the application with: python main.py --reset")
    print("\nEnjoy using Content Creation Assistant!")


if __name__ == "__main__":
    main()