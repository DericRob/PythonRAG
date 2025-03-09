#!/usr/bin/env python3
"""
Fix script for Ollama import issues in the Content Creation Assistant
"""
import os
import sys
import subprocess
import importlib.util

def check_ollama_import():
    """Check if Ollama can be imported from the correct location"""
    try:
        from langchain_community.llms.ollama import Ollama
        print("✅ Ollama can be imported from langchain_community.llms.ollama")
        return True
    except ImportError:
        print("❌ Cannot import Ollama from langchain_community.llms.ollama")
        return False

def fix_dependencies():
    """Install or reinstall the necessary packages"""
    packages = [
        "langchain-community>=0.0.13",
        "langchain-chroma>=0.0.1",
        "langchain>=0.1.0"
    ]
    
    print("\n🔄 Installing/Reinstalling required packages...")
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", package], check=True)
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def main():
    print("=" * 60)
    print("🔧 Import Fix Tool for Content Creation Assistant")
    print("=" * 60)
    
    print("\nChecking for Ollama import issues...")
    if check_ollama_import():
        print("\n✅ All imports appear to be working correctly!")
        print("If you're still experiencing issues, please run:")
        print("python troubleshoot.py")
        return
    
    print("\nAttempting to fix import issues...")
    if fix_dependencies():
        # Check again to see if it's fixed
        if check_ollama_import():
            print("\n✅ Successfully fixed import issues!")
            print("You can now run the application with:")
            print("python main.py")
        else:
            print("\n⚠️ Import issues persist after reinstalling packages.")
            print("Please try manually installing with:")
            print("pip install --upgrade langchain-community")
    else:
        print("\n❌ Failed to fix import issues.")
        print("Please try manually installing packages with:")
        print("pip install --upgrade langchain-community")

if __name__ == "__main__":
    main()