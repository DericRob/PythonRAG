from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import os
import json
from query_data import query_rag

app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    """Serve the main index.html page."""
    return app.send_static_file('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a query from the frontend."""
    try:
        # Get the request data
        data = request.json
        print(f"Received request: {data}")
        
        if not data or 'topic' not in data:
            return jsonify({"error": "Missing required field 'topic'"}), 400
            
        topic = data['topic']
        additional_info = data.get('additionalInfo', '')
        
        # Create full query with additional info if provided
        full_query = topic
        if additional_info:
            full_query += f" Context: {additional_info}"
            
        print(f"Processing query: {full_query}")
            
        # Query the RAG system
        print("Generating article content...")
        article_response, sources = query_rag(f"Write an informative article about: {full_query}")
        
        print("Generating social media content...")
        facebook_response, _ = query_rag(f"Write a short social media post about: {full_query}")
        
        print("Generating video script content...")
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
    """Check if the API is running."""
    return jsonify({
        "status": "online",
        "model": "Llama 3.2 3B",
        "database": "Chroma",
    })

def setup_static_folder():
    """Set up the static folder with the frontend files."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"Created static directory at {static_dir}")
    
    # Create a simple HTML file directly
    index_path = os.path.join(static_dir, 'index.html')
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Creation Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Source Sans Pro', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #212529;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        
        .header {
            background-color: #075290;
            color: white;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
            border-radius: 8px;
        }
        
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-bottom: 30px;
        }
        
        h1 {
            color: #075290;
            margin-bottom: 30px;
            text-align: center;
            font-weight: 600;
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input[type="text"], 
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        button {
            background-color: #075290;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background-color: #005eaa;
        }
        
        .result-box {
            background-color: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 20px;
            display: none;
        }
        
        .result-box h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        
        .spinner {
            border: 4px solid rgba(0, 0, 0, 0.1);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border-left-color: #3498db;
            animation: spin 1s linear infinite;
            display: inline-block;
            vertical-align: middle;
            margin-left: 10px;
            display: none;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .copy-btn {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            float: right;
        }
        
        .error {
            color: #e74c3c;
            margin-top: 10px;
            padding: 10px;
            border-radius: 4px;
            background-color: #fadbd8;
            display: none;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Content Creation Assistant</h1>
    </div>
    
    <div class="container">
        <div class="input-group">
            <label for="topic">What would you like content about?</label>
            <input type="text" id="topic" placeholder="Enter your topic or question...">
        </div>
        
        <div class="input-group">
            <label for="additional-info">Additional Information or Context (optional)</label>
            <textarea id="additional-info" placeholder="Add any specific details, target audience, tone requirements, etc."></textarea>
        </div>
        
        <button id="generate-btn">Generate Content <span id="spinner" class="spinner"></span></button>
        <div id="error-message" class="error"></div>
        
        <div id="article-result" class="result-box">
            <h3>Article Content <button class="copy-btn" data-target="article-content">Copy</button></h3>
            <div id="article-content"></div>
        </div>
        
        <div id="facebook-result" class="result-box">
            <h3>Facebook Post <button class="copy-btn" data-target="facebook-content">Copy</button></h3>
            <div id="facebook-content"></div>
        </div>
        
        <div id="youtube-result" class="result-box">
            <h3>YouTube Script <button class="copy-btn" data-target="youtube-content">Copy</button></h3>
            <div id="youtube-content"></div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Event listeners
            document.getElementById('generate-btn').addEventListener('click', generateContent);
            
            // Copy buttons
            document.querySelectorAll('.copy-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const targetId = this.getAttribute('data-target');
                    const contentElement = document.getElementById(targetId);
                    const textToCopy = contentElement.innerText;
                    
                    navigator.clipboard.writeText(textToCopy).then(() => {
                        const originalText = this.innerText;
                        this.innerText = 'Copied!';
                        setTimeout(() => {
                            this.innerText = originalText;
                        }, 2000);
                    }).catch(err => {
                        console.error('Could not copy text: ', err);
                    });
                });
            });
        });
        
        async function generateContent() {
            const topic = document.getElementById('topic').value.trim();
            const additionalInfo = document.getElementById('additional-info').value.trim();
            const errorElement = document.getElementById('error-message');
            const spinner = document.getElementById('spinner');
            
            // Validate inputs
            if (!topic) {
                showError('Please enter a topic or question.');
                return;
            }
            
            // Clear previous results and errors
            errorElement.style.display = 'none';
            document.getElementById('article-result').style.display = 'none';
            document.getElementById('facebook-result').style.display = 'none';
            document.getElementById('youtube-result').style.display = 'none';
            
            // Show spinner
            spinner.style.display = 'inline-block';
            
            try {
                // Call backend API
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
                
                // Display results
                if (data.articleContent) {
                    document.getElementById('article-content').innerHTML = formatContent(data.articleContent);
                    document.getElementById('article-result').style.display = 'block';
                }
                
                if (data.facebookContent) {
                    document.getElementById('facebook-content').innerHTML = formatContent(data.facebookContent);
                    document.getElementById('facebook-result').style.display = 'block';
                }
                
                if (data.youtubeContent) {
                    document.getElementById('youtube-content').innerHTML = formatContent(data.youtubeContent);
                    document.getElementById('youtube-result').style.display = 'block';
                }
                
            } catch (error) {
                showError(error.message || 'An error occurred while generating content.');
            } finally {
                // Hide spinner
                spinner.style.display = 'none';
            }
        }
        
        function formatContent(content) {
            // Guard against null or undefined content
            if (!content) return '';
            
            // Convert line breaks to <br> tags and maintain paragraphs
            return content
                .replace(/\\n\\n/g, '</p><p>')
                .replace(/\\n/g, '<br>')
                .replace(/^/, '<p>')
                .replace(/$/g, '</p>');
        }
        
        function showError(message) {
            const errorElement = document.getElementById('error-message');
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            document.getElementById('spinner').style.display = 'none';
        }
    </script>
</body>
</html>""")
    
    print(f"Created simple index.html in {static_dir}")
    return True

if __name__ == '__main__':
    if setup_static_folder():
        print("Starting web server on http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    else:
        print("Failed to set up static folder")