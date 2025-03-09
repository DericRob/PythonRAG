from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import os
import json
from query_data import query_rag

app = Flask(__name__, static_folder="static")
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/')
def index():
    """Serve the main index.html page."""
    return app.send_static_file('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """
    Process a query from the frontend.
    
    Expected JSON body:
    {
        "topic": "What's the question?",
        "additionalInfo": "Any additional context"
    }
    
    Returns:
    {
        "articleContent": "Generated article",
        "facebookContent": "Generated social post",
        "youtubeContent": "Generated video script",
        "sources": ["List of sources used"]
    }
    """
    try:
        # Get the request data
        data = request.json
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Missing required field 'topic'"}), 400
            
        topic = data['topic']
        additional_info = data.get('additionalInfo', '')
        
        # Create full query with additional info if provided
        full_query = topic
        if additional_info:
            full_query += f" Context: {additional_info}"
            
        # Query the RAG system
        article_response, sources = query_rag(f"Write an informative article about: {full_query}")
        facebook_response, _ = query_rag(f"Write a short social media post about: {full_query}")
        youtube_response, _ = query_rag(f"Write a script for a video about: {full_query}")
        
        # Return the responses
        return jsonify({
            "articleContent": article_response,
            "facebookContent": facebook_response,
            "youtubeContent": youtube_response,
            "sources": sources
        })
        
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def check_status():
    """Check if the API is running and the RAG system is available."""
    return jsonify({
        "status": "online",
        "model": "Llama 3.2 3B",
        "database": "Chroma",
    })

def setup_static_folder():
    """Ensure the static folder exists and contains the frontend files."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    # Create static directory if it doesn't exist
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        
    # Check if openai004.html exists
    html_path = 'openai004.html'
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found!")
        return False
        
    # Copy the HTML file to the static directory
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Update the HTML to work with our backend
    # Replace OpenAI API calls with our own backend API
    html_content = html_content.replace(
        'https://api.openai.com/v1/chat/completions', 
        '/api/query'
    )
    
    # Fix the JavaScript to work with our API
    # Replace the entire callOpenAI function with our version
    js_pattern = "async function callOpenAI(contentType, topic, additionalInfo, apiKey) {"
    js_replacement = """async function callOpenAI(contentType, topic, additionalInfo, apiKey) {
    // For backend API, we'll use a different approach
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic: topic,
                additionalInfo: additionalInfo
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `API call failed with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Return the appropriate content based on contentType
        if (contentType === 'article') {
            return data.articleContent;
        } else if (contentType === 'facebook') {
            return data.facebookContent;
        } else if (contentType === 'youtube') {
            return data.youtubeContent;
        }
    } catch (error) {
        throw error;
    }"""
    
    # Replace the function
    if js_pattern in html_content:
        html_content = html_content.replace(js_pattern, js_replacement)
    
    # Save the modified HTML
    with open(os.path.join(static_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Frontend files prepared in {static_dir}")
    return True

if __name__ == '__main__':
    if setup_static_folder():
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to set up the static folder. Please check that openai004.html exists.")