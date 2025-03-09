#!/usr/bin/env python3
"""
Script to initialize required Ollama models for Content Creation Assistant
"""
import os
import sys
import platform
import subprocess
import time
import requests

def is_ollama_running():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Attempt to start Ollama"""
    system = platform.system()
    
    print("Attempting to start Ollama...")
    
    if system == "Windows":
        try:
            # On Windows, we'll try to start Ollama via PowerShell
            # This assumes Ollama is installed in the default location
            subprocess.Popen(["powershell", "-Command", "Start-Process ollama serve"], 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
            
            print("Waiting for Ollama to start...")
            for _ in range(10):  # Wait up to 10 seconds
                if is_ollama_running():
                    print("✅ Ollama started successfully")
                    return True
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Failed to start Ollama: {str(e)}")
    
    elif system == "Darwin":  # macOS
        try:
            # On macOS, try to start Ollama via the command line
            subprocess.Popen(["open", "-a", "Ollama"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            
            print("Waiting for Ollama to start...")
            for _ in range(10):  # Wait up to 10 seconds
                if is_ollama_running():
                    print("✅ Ollama started successfully")
                    return True
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Failed to start Ollama: {str(e)}")
    
    elif system == "Linux":
        try:
            # On Linux, try to start Ollama via systemd or direct command
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            
            print("Waiting for Ollama to start...")
            for _ in range(10):  # Wait up to 10 seconds
                if is_ollama_running():
                    print("✅ Ollama started successfully")
                    return True
                time.sleep(1)
                
        except Exception as e:
            print(f"❌ Failed to start Ollama: {str(e)}")
    
    print("❌ Could not automatically start Ollama")
    print("Please start Ollama manually and run this script again")
    return False

def get_available_models():
    """Get list of available models in Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [model.get("name", "") for model in data.get("models", [])]
        return []
    except:
        return []

def pull_model(model_name):
    """Pull a model from Ollama"""
    print(f"\nPulling {model_name}...")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"✅ Successfully pulled {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pulling {model_name}: {e}")
        return False
    except FileNotFoundError:
        print("❌ Ollama command not found. Make sure it's installed and in your PATH")
        return False

def main():
    print("=" * 60)
    print("🤖 Model Initialization for Content Creation Assistant")
    print("=" * 60)
    
    required_models = ["llama3.2:3b", "nomic-embed-text:latest"]
    
    # Check if Ollama is running
    if not is_ollama_running():
        print("❌ Ollama is not running")
        
        # Try to start Ollama
        if not start_ollama():
            print("\nPlease:")
            print("1. Make sure Ollama is installed (https://ollama.ai/download)")
            print("2. Start Ollama manually")
            print("3. Run this script again")
            return False
    
    # Get available models
    available_models = get_available_models()
    
    # Pull missing models
    all_models_available = True
    for model in required_models:
        if model in available_models:
            print(f"✅ {model} is already available")
        else:
            print(f"⚠️ {model} is not available, pulling now...")
            success = pull_model(model)
            if not success:
                all_models_available = False
    
    if all_models_available:
        print("\n✅ All required models are available!")
        print("\nYou can now run the application with:")
        print("python main.py --reset")
    else:
        print("\n❌ Some models could not be pulled automatically.")
        print("Please try pulling them manually:")
        for model in required_models:
            if model not in get_available_models():
                print(f"ollama pull {model}")
        print("\nThen run the application with:")
        print("python main.py --reset")
    
    return all_models_available

if __name__ == "__main__":
    main()