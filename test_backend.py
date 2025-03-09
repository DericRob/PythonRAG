#!/usr/bin/env python3
"""
Simple script to test if the backend API is working
"""
import requests
import sys
import json
import time

API_URL = "http://localhost:5000"

def test_status_endpoint():
    """Test if the status endpoint is responding"""
    try:
        print(f"Testing API status at {API_URL}/api/status")
        response = requests.get(f"{API_URL}/api/status", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Status endpoint responded with: {response.json()}")
            return True
        else:
            print(f"❌ Status endpoint returned error code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {API_URL}")
        print("   Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error testing status endpoint: {str(e)}")
        return False

def test_query_endpoint():
    """Test if the query endpoint is working"""
    test_data = {
        "topic": "Test query",
        "additionalInfo": "This is a test query to check if the API is working"
    }
    
    try:
        print(f"\nTesting API query at {API_URL}/api/query")
        print(f"Sending test data: {json.dumps(test_data)}")
        
        start_time = time.time()
        response = requests.post(
            f"{API_URL}/api/query", 
            json=test_data,
            timeout=30  # Longer timeout for query processing
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Query endpoint responded in {elapsed_time:.2f} seconds")
            print("Response contains:")
            
            for key in data:
                content = data[key]
                if isinstance(content, str):
                    # Truncate long content
                    if len(content) > 100:
                        content = content[:100] + "..."
                print(f"  - {key}: {content}")
            
            return True
        else:
            print(f"❌ Query endpoint returned error code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text[:200]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {API_URL}")
        print("   Is the server running?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout error: The query is taking too long to process")
        print("   The server might be overloaded or still processing the request")
        return False
    except Exception as e:
        print(f"❌ Error testing query endpoint: {str(e)}")
        return False

def test_frontend():
    """Test if the frontend HTML is accessible"""
    try:
        print(f"\nTesting frontend at {API_URL}")
        response = requests.get(API_URL, timeout=5)
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' in content_type:
                html_size = len(response.text)
                print(f"✅ Frontend HTML is accessible (size: {html_size} bytes)")
                
                # Check for basic HTML elements
                if '<html' in response.text and '<body' in response.text:
                    print("   HTML contains basic elements")
                else:
                    print("⚠️ HTML may be incomplete or invalid")
                
                return True
            else:
                print(f"❌ Response is not HTML (Content-Type: {content_type})")
                return False
        else:
            print(f"❌ Frontend returned error code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {API_URL}")
        print("   Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error testing frontend: {str(e)}")
        return False

def change_port():
    """Change the port to test a different port"""
    global API_URL
    port = input("\nEnter a different port to test (e.g., 5001): ")
    try:
        port = int(port)
        API_URL = f"http://localhost:{port}"
        print(f"Now testing {API_URL}")
        return True
    except ValueError:
        print("Invalid port number")
        return False

def main():
    print("=" * 60)
    print("Backend API Connection Test")
    print("=" * 60)
    
    # Parse command line arguments for custom port
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        global API_URL
        port = int(sys.argv[1])
        API_URL = f"http://localhost:{port}"
        print(f"Using custom port: {port}")
    
    # Test status endpoint
    status_ok = test_status_endpoint()
    
    # Test query endpoint if status was successful
    query_ok = False
    if status_ok:
        query_ok = test_query_endpoint()
    
    # Test frontend
    frontend_ok = test_frontend()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"API Status Endpoint: {'✅ PASSED' if status_ok else '❌ FAILED'}")
    print(f"API Query Endpoint:  {'✅ PASSED' if query_ok else '❌ FAILED'}")
    print(f"Frontend Access:     {'✅ PASSED' if frontend_ok else '❌ FAILED'}")
    
    # Recommendations
    if not (status_ok and query_ok and frontend_ok):
        print("\nRecommendations:")
        if not status_ok:
            print("• Make sure the Flask server is running")
            print("• Check if the port is correct and not blocked")
            print("• Try running 'python main.py --debug' to see detailed logs")
        
        if status_ok and not query_ok:
            print("• The server is running but query processing is failing")
            print("• Check server logs for errors")
            print("• Verify that Ollama is running and the models are available")
        
        if not frontend_ok:
            print("• The static files may not be set up correctly")
            print("• Run 'python create_static_files.py' to fix the frontend")
        
        # Offer to test a different port
        change_port_option = input("\nWould you like to test a different port? (y/n): ").lower()
        if change_port_option == 'y' and change_port():
            main()  # Rerun the tests with the new port
    else:
        print("\n✅ All tests passed! The backend is working correctly.")

if __name__ == "__main__":
    main()