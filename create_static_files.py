def setup_static_folder():
    """Set up the static folder with the frontend files."""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # Check if openai004.html exists
    html_path = 'openai004.html'
    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found!")
        return False
    
    # Copy the HTML file
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Modify the HTML to remove API key requirement
    # 1. Remove the API key input field
    if '<div class="api-key-container">' in html_content:
        start_index = html_content.find('<div class="api-key-container">')
        end_index = html_content.find('</div>', start_index)
        end_index = html_content.find('</div>', end_index + 1)  # Find the closing div for the container
        html_content = html_content[:start_index] + html_content[end_index + 6:]
        print("Removed API key input field")
    
    # 2. Modify the JavaScript to not require the API key
    js_pattern = "async function callOpenAI(contentType, topic, additionalInfo, apiKey) {"
    js_replacement = """async function callOpenAI(contentType, topic, additionalInfo, apiKey) {
        // API key is not required for local backend
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
        print("Modified JavaScript callOpenAI function")
    
    # 3. Modify the validation to not check for API key
    validation_pattern = "if (!apiKey) {\n                showError('Please enter your OpenAI API key.');\n                return;\n            }"
    validation_replacement = "// API key validation removed for local backend"
    
    if validation_pattern in html_content:
        html_content = html_content.replace(validation_pattern, validation_replacement)
        print("Removed API key validation")
    
    # 4. Remove API key references from localStorage
    localstorage_pattern = "const savedApiKey = localStorage.getItem('openai_api_key');\n            if (savedApiKey) {\n                document.getElementById('api-key').value = savedApiKey;\n            }"
    localstorage_replacement = "// API key storage not needed for local backend"
    
    if localstorage_pattern in html_content:
        html_content = html_content.replace(localstorage_pattern, localstorage_replacement)
        print("Removed localStorage API key references")
    
    # 5. Remove API key saving
    saving_pattern = "document.getElementById('api-key').addEventListener('change', function() {\n                localStorage.setItem('openai_api_key', this.value);\n            });"
    saving_replacement = "// API key saving not needed"
    
    if saving_pattern in html_content:
        html_content = html_content.replace(saving_pattern, saving_replacement)
        print("Removed API key saving code")
    
    # Save as index.html in static folder
    with open(os.path.join(static_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Frontend file created in {static_dir}")
    return True