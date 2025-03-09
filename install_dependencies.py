#!/usr/bin/env python3
"""
Simple dependency installer for Content Creation Assistant
"""
import sys
import subprocess
import platform
import os

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️ {text}")

def install_package(package_name):
    print(f"Installing {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print_success(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Failed to install {package_name}")
        return False

def main():
    print_header("Content Creation Assistant - Dependency Installer")
    
    # Verify Python version
    python_version = sys.version.split()[0]
    print_info(f"Python version: {python_version}")
    print_info(f"Python path: {sys.executable}")
    
    # Upgrade pip
    print_info("Upgrading pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print_success("Pip upgraded successfully")
    except:
        print_error("Failed to upgrade pip")
    
    # Essential packages
    essential_packages = [
        "langchain_ollama",
        "langchain_chroma",
        "langchain-text-splitters",
        "flask",
        "flask-cors",
        "requests",
        "chromadb"
    ]
    
    print_header("Installing Essential Packages")
    failed_packages = []
    
    for package in essential_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print_error("Failed to install some packages:")
        for package in failed_packages:
            print(f"  - {package}")
    else:
        print_success("All essential packages installed successfully")
    
    # Create necessary directories
    directories = ["data", "chroma", "static"]
    print_header("Creating Directories")
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print_success(f"Created {directory} directory")
            except:
                print_error(f"Failed to create {directory} directory")
        else:
            print_info(f"{directory} directory already exists")
    
    # Final instructions
    print_header("Next Steps")
    print_info("1. Make sure Ollama is installed and running")
    print_info("2. Pull the required models with:")
    print("   ollama pull llama3.2:3b")
    print("   ollama pull nomic-embed-text")
    print_info("3. Run the application with:")
    print("   python main.py --reset")
    
    print("\nThank you for installing Content Creation Assistant!")

if __name__ == "__main__":
    main()