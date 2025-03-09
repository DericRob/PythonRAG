#!/usr/bin/env python3
"""
Simplified setup script for Content Creation Assistant
Installs only essential dependencies and configures the system
"""
import os
import sys
import subprocess
import platform

def install_core_packages():
    """Install only the essential packages"""
    packages = [
        "langchain==0.1.0",
        "langchain-community==0.0.13",
        "langchain-chroma==0.0.1",
        "chromadb==0.4.22",
        "pypdf==3.17.0",
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "docx2txt==0.8",
        "python-docx==0.8.11",
        "pandas==2.0.3",
        "requests==2.31.0",
        "langchain-text-splitters==0.0.1"
    ]
    
    print("\n=== Installing Core Packages ===")
    try:
        # First update pip
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ Upgraded pip")
        
        # Install packages one by one
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        
        print("✅ Core packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["data", "chroma", "static"]
    
    print("\n=== Creating Directories ===")
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created {directory} directory")
            except Exception as e:
                print(f"❌ Error creating {directory}: {e}")
                return False
        else:
            print(f"✅ {directory} directory already exists")
    
    return True

def check_ollama():
    """Check if Ollama is installed"""
    print("\n=== Checking Ollama ===")
    
    try:
        # Check if we can import requests
        import requests
        
        # Try to connect to Ollama
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
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
                print("⚠️ Ollama is installed but not running")
                print("   Please start Ollama and then run:")
                print("   python initialize_models.py")
                return False
        else:
            result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
            if result.returncode == 0:
                print("⚠️ Ollama is installed but not running")
                print("   Please start Ollama and then run:")
                print("   python initialize_models.py")
                return False
                
        print("⚠️ Ollama is not installed")
        print("   Please install Ollama from: https://ollama.ai/download")
        print("   After installing, run:")
        print("   python initialize_models.py")
        return False
    
    except ImportError:
        print("❌ Could not import requests module")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return False

def setup_frontend():
    """Set up the frontend files"""
    print("\n=== Setting Up Frontend ===")
    
    # Create static directory
    if not os.path.exists("static"):
        os.makedirs("static")
    
    # Copy the main HTML file to static
    try:
        if not os.path.exists("openai004.html"):
            print("⚠️ openai004.html not found, skipping frontend setup")
            return False
            
        with open("openai004.html", "r", encoding="utf-8") as source_file:
            content = source_file.read()
            
        # Make simple modifications for our backend
        content = content.replace(
            'https://api.openai.com/v1/chat/completions',
            '/api/query'
        )
        
        with open("static/index.html", "w", encoding="utf-8") as dest_file:
            dest_file.write(content)
            
        print("✅ Frontend files set up successfully")
        return True
    except Exception as e:
        print(f"❌ Error setting up frontend: {e}")
        return False

def main():
    print("=" * 60)
    print("🤖 Minimal Setup for Content Creation Assistant")
    print("=" * 60)
    
    print("\nThis script will install only the essential dependencies")
    print("and set up the basic system requirements.")
    
    # Install core packages
    if not install_core_packages():
        print("\n❌ Failed to install all core packages")
        print("Please check the error messages and try again")
        return
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create all necessary directories")
        print("Please check the error messages and try again")
        return
    
    # Set up frontend
    setup_frontend()
    
    # Check Ollama
    check_ollama()
    
    print("\n✅ Basic setup completed!")
    print("\nNext steps:")
    print("1. Make sure Ollama is installed and running")
    print("2. Run: python initialize_models.py")
    print("3. Add your documents to the 'data' folder")
    print("4. Run: python main.py --reset")
    print("\nFor troubleshooting, run: python troubleshoot.py")
    print("\nNote: This is a minimal setup with essential dependencies only.")
    print("Some advanced features might require additional packages.")

if __name__ == "__main__":
    main()