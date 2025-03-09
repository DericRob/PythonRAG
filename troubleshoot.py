#!/usr/bin/env python3
"""
Troubleshooting script for Content Creation Assistant
Diagnoses common issues and provides solutions
"""
import os
import sys
import platform
import subprocess
import requests
import importlib.util

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python version must be 3.8 or higher")
        print("   Please upgrade Python and try again")
        return False
    
    print("✅ Python version is compatible")
    return True


def check_pip():
    """Check if pip is installed and up to date."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("✅ pip is installed")
        return True
    except:
        print("❌ pip is not installed or not working")
        print("   Please install or repair pip and try again")
        return False


def check_ollama():
    """Check if Ollama is installed and running."""
    print("\nChecking Ollama...")
    
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ollama is running (version: {data.get('version', 'unknown')})")
            return True
    except:
        print("❌ Ollama is not running")
        
        # Check if Ollama is installed
        system = platform.system()
        try:
            if system == "Windows":
                result = subprocess.run(["where", "ollama"], capture_output=True, text=True)
                if "ollama" in result.stdout:
                    print("   Ollama is installed but not running")
                    print("   Please start Ollama and try again")
                    return False
            else:
                result = subprocess.run(["which", "ollama"], capture_output=True, text=True)
                if result.returncode == 0:
                    print("   Ollama is installed but not running")
                    print("   Please start Ollama and try again")
                    return False
        except:
            pass
        
        print("   Ollama is not installed or not in PATH")
        print("   Please install Ollama from https://ollama.ai/download")
        return False


def check_models():
    """Check if required models are available in Ollama."""
    print("\nChecking models...")
    
    required_models = ["llama3.2:3b", "nomic-embed-text:latest"]
    available_models = []
    
    try:
        # First check if Ollama is running
        try:
            response = requests.get("http://localhost:11434/api/version", timeout=5)
            if response.status_code != 200:
                print("❌ Cannot check models because Ollama is not running")
                return False
        except Exception as e:
            print(f"❌ Cannot check models: {str(e)}")
            return False
        
        # Then check available models
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                available_models = [model.get("name", "") for model in models]
            else:
                print(f"❌ Failed to get models list (status code: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ Error retrieving models list: {str(e)}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error checking models: {str(e)}")
        return False
    
    all_models_available = True
    for model in required_models:
        if model in available_models:
            print(f"✅ {model} is available")
        else:
            print(f"❌ {model} is not available")
            print(f"   Please run: ollama pull {model}")
            all_models_available = False
    
    return all_models_available


def check_dependencies():
    """Check if required Python packages are installed."""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        "langchain",
        "langchain_community",
        "langchain_chroma",
        "chromadb",
        "flask",
        "flask_cors"
    ]
    
    all_deps_installed = True
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is not None:
            print(f"✅ {package} is installed")
        else:
            print(f"❌ {package} is not installed")
            all_deps_installed = False
    
    # Specifically check for Ollama import
    try:
        from langchain_community.llms.ollama import Ollama
        print("✅ Ollama can be imported from langchain_community")
    except ImportError:
        print("❌ Cannot import Ollama from langchain_community")
        all_deps_installed = False
    
    if not all_deps_installed:
        print("\nSome required packages are missing.")
        print("Run the following command to install them:")
        print("python setup.py")
    
    return all_deps_installed


def check_directories():
    """Check if required directories exist and have correct permissions."""
    print("\nChecking directories...")
    
    required_dirs = ["data", "chroma", "static"]
    all_dirs_accessible = True
    
    for directory in required_dirs:
        if os.path.exists(directory):
            # Check if directory is readable and writable
            if os.access(directory, os.R_OK | os.W_OK):
                print(f"✅ {directory} exists and is accessible")
            else:
                print(f"❌ {directory} exists but is not accessible")
                print(f"   Please check permissions for {directory}")
                all_dirs_accessible = False
        else:
            print(f"❌ {directory} does not exist")
            try:
                os.makedirs(directory)
                print(f"   Created {directory} directory")
            except:
                print(f"   Failed to create {directory} directory")
                print(f"   Please create it manually")
                all_dirs_accessible = False
    
    # Check data directory contents
    if os.path.exists("data"):
        files = os.listdir("data")
        if not files:
            print("\n⚠️ Warning: data directory is empty")
            print("   Please add documents to the data directory")
    
    return all_dirs_accessible


def fix_common_issues():
    """Try to fix common issues automatically."""
    print("\nAttempting to fix common issues...")
    
    # Upgrade pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        print("✅ Upgraded pip")
    except:
        print("❌ Failed to upgrade pip")
    
    # Install or upgrade core dependencies
    try:
        core_deps = ["wheel", "setuptools", "numpy"]
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade"] + core_deps, check=True)
        print("✅ Installed/upgraded core dependencies")
    except:
        print("❌ Failed to install core dependencies")
    
    # Create required directories
    for directory in ["data", "chroma", "static"]:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created {directory} directory")
            except:
                print(f"❌ Failed to create {directory} directory")
    
    print("\nFixing attempt completed. Please run the troubleshooter again to check status.")


def main():
    print("=" * 60)
    print("🔍 Content Creation Assistant Troubleshooter")
    print("=" * 60)
    
    # Run checks
    python_ok = check_python_version()
    pip_ok = check_pip()
    ollama_ok = check_ollama()
    models_ok = check_models() if ollama_ok else False
    deps_ok = check_dependencies()
    dirs_ok = check_directories()
    
    # Summarize findings
    print("\n" + "=" * 60)
    print("📊 Troubleshooting Summary")
    print("=" * 60)
    
    checks = [
        ("Python Version", python_ok),
        ("pip Installation", pip_ok),
        ("Ollama Running", ollama_ok),
        ("Required Models", models_ok),
        ("Python Dependencies", deps_ok),
        ("Directory Structure", dirs_ok)
    ]
    
    for check, status in checks:
        status_text = "✅ OK" if status else "❌ Issue Found"
        print(f"{check}: {status_text}")
    
    # Overall status
    if all(status for _, status in checks):
        print("\n✅ All checks passed! The system should be working correctly.")
        print("\nTo run the system:")
        print("1. Run database setup: python main.py --reset")
        print("2. Access the web interface at: http://localhost:5000")
    else:
        print("\n❌ Issues were found. Would you like to attempt to fix them? (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            fix_common_issues()
            print("\nSome issues may require manual intervention:")
            if not ollama_ok:
                print("- Install Ollama from https://ollama.ai/download")
            if ollama_ok and not models_ok:
                print("- Pull required models:")
                print("  ollama pull llama3:3b")
                print("  ollama pull nomic-embed-text")
            print("\nAfter addressing these issues, run this troubleshooter again.")
        else:
            print("\nPlease fix the issues manually and run the troubleshooter again.")


if __name__ == "__main__":
    main()