@echo off
echo =================================================
echo Content Creation Assistant - Installation Script
echo =================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher and try again
    pause
    exit /b 1
)

:: Create a virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install core dependencies
echo Installing core dependencies...
python -m pip install wheel setuptools numpy

:: Install critical packages first
echo Installing main packages...
python -m pip install langchain langchain_ollama langchain_chroma chromadb flask flask-cors requests pandas

:: Install document handling packages
echo Installing document handling packages...
python -m pip install pypdf docx2txt python-docx openpyxl

:: Install remaining requirements
echo Installing additional dependencies...
python -m pip install langchain_community langchain-text-splitters python-dotenv

:: Create directories
echo Creating directories...
if not exist data mkdir data
if not exist chroma mkdir chroma
if not exist static mkdir static

echo.
echo Installation completed!
echo.
echo To run the application:
echo 1. Make sure Ollama is installed and running
echo 2. Pull required models: ollama pull llama3.2:3b nomic-embed-text:latest
echo 3. Add your documents to the 'data' folder
echo 4. Run: python main.py --reset
echo.
echo For troubleshooting, run: python troubleshoot.py
echo.

pause