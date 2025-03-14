"""
Search stacks.cdc.gov for relevant documents and add them to the knowledge base.
"""
import os
import requests
from bs4 import BeautifulSoup
import time
from langchain.schema.document import Document
from urllib.parse import urljoin, urlparse, quote
import tempfile
import hashlib
from typing import List, Dict, Tuple, Optional
import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Updated search URL based on the provided endpoint
CDC_SEARCH_URL = "https://stacks.cdc.gov/gsearch"

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_FACTOR = 0.5  # Exponential backoff factor
RETRY_STATUS_CODES = [429, 500, 502, 503, 504, 403, 404]  # Status codes to retry on

def make_request_with_retry(url: str, headers: Dict, params: Dict = None, timeout: int = 30) -> requests.Response:
    """
    Make an HTTP request with retry capability for error handling.
    
    Args:
        url: URL to request
        headers: HTTP headers
        params: Query parameters
        timeout: Request timeout in seconds
        
    Returns:
        Response object
    
    Raises:
        requests.RequestException: If all retries fail
    """
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                # Add jitter to prevent thundering herd
                sleep_time = RETRY_BACKOFF_FACTOR * (2 ** attempt) + random.uniform(0, 0.5)
                logger.info(f"Retry attempt {attempt+1}/{MAX_RETRIES} for {url} (waiting {sleep_time:.2f}s)")
                time.sleep(sleep_time)
            
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            
            # Log response details
            logger.info(f"Request to {url} returned status code {response.status_code}")
            
            # If successful or not a retryable status code, return immediately
            if response.status_code < 400 or response.status_code not in RETRY_STATUS_CODES:
                response.raise_for_status()  # Raise for other error codes
                return response
                
            logger.warning(f"Received status code {response.status_code} from {url}")
            
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Request error: {str(e)}. Retrying ({attempt+1}/{MAX_RETRIES})...")
            else:
                logger.error(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
                raise
                
    # If we get here, we've exhausted our retries on status codes
    logger.error(f"Request to {url} failed after {MAX_RETRIES} attempts with status {response.status_code}")
    response.raise_for_status()  # Raise the last error
    return response  # This line should never be reached

def search_cdc_stacks(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search stacks.cdc.gov for relevant documents using gsearch endpoint.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with document information
    """
    logger.info(f"Searching CDC Stacks for: {query}")
    
    # URL encode the search terms
    encoded_query = quote(query)
    
    try:
        # Set up headers to make our request look like it's coming from a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.cdc.gov/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        
        # Make the search request to the gsearch endpoint
        search_url = f"{CDC_SEARCH_URL}?collection=&terms={encoded_query}"
        logger.info(f"Making request to: {search_url}")
        
        # Use the retry function for the request
        response = make_request_with_retry(search_url, headers=headers)
        
        # Parse the search results page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find search result items - using the appropriate selector for gsearch results
        search_results = []
        result_items = soup.select('div.gs-result')
        
        logger.info(f"Found {len(result_items)} raw result items")
        
        for idx, item in enumerate(result_items):
            if idx >= max_results:
                break
                
            # Extract title and link
            title_elem = item.select_one('.gs-title a')
            if not title_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            url = title_elem['href']
            
            # Extract snippet/description if available
            snippet_elem = item.select_one('.gs-snippet')
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
            
            # Extract metadata if available
            metadata_elem = item.select_one('.gs-metadata')
            metadata = metadata_elem.get_text(strip=True) if metadata_elem else ""
            
            search_results.append({
                'title': title,
                'url': url,
                'abstract': snippet,
                'metadata': metadata
            })
        
        logger.info(f"Processed {len(search_results)} results from CDC Stacks")
        return search_results
        
    except Exception as e:
        logger.error(f"Error searching CDC Stacks: {str(e)}")
        return []

def fetch_document_content(doc_info: Dict) -> Optional[str]:
    """
    Fetch the content of a document from its URL.
    
    Args:
        doc_info: Dictionary with document information
        
    Returns:
        Document content as text
    """
    url = doc_info['url']
    logger.info(f"Fetching document content from: {url}")
    
    try:
        # Set up headers to make our request look like it's coming from a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Referer": "https://www.cdc.gov/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }
        
        # Use the retry function for the request
        response = make_request_with_retry(url, headers=headers)
        
        # Parse the document page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the main content
        content_selectors = [
            'div.main-content',  # Main content container
            'div.item-page',     # Item page container
            'div.ds-static-div',  # DSpace content
            'main',              # HTML5 main content
            'article',           # HTML5 article element
            '#content',          # Generic content ID
            'div.content'        # Generic content class
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, nav, header, footer'):
                    elem.decompose()
                
                text = content_elem.get_text(separator=' ', strip=True)
                if text and len(text) > 100:  # Only return if we have meaningful content
                    return text
        
        # If we can't find a content container, look for PDF link
        pdf_link = soup.select_one('a[href$=".pdf"]')
        if pdf_link and pdf_link.get('href'):
            pdf_url = urljoin(url, pdf_link.get('href'))
            logger.info(f"Found PDF link: {pdf_url}")
            
            # Just extract metadata since we can't parse PDF
            metadata = []
            
            # Try to get the title
            title_elem = soup.select_one('h1') or soup.select_one('h2')
            if title_elem:
                metadata.append(f"Title: {title_elem.get_text(strip=True)}")
                
            # Try to get the abstract
            abstract_elem = soup.select_one('div.abstract') or soup.select_one('div.description')
            if abstract_elem:
                metadata.append(f"Abstract: {abstract_elem.get_text(strip=True)}")
                
            # Include the snippet from search results as fallback
            if doc_info.get('abstract'):
                metadata.append(doc_info['abstract'])
                
            # Add PDF link note
            metadata.append(f"Note: Full text available as PDF at {pdf_url}")
            
            return " ".join(metadata)
        
        # Last resort: just get the body text
        body = soup.select_one('body')
        if body:
            for elem in body.select('script, style, nav, header, footer'):
                elem.decompose()
            return body.get_text(separator=' ', strip=True)
            
        return None
    
    except Exception as e:
        logger.error(f"Error fetching document content from {url}: {str(e)}")
        return None
        
        # Parse the document page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find the main content
        content_selectors = [
            'div.main-content',  # Main content container
            'div.item-page',     # Item page container
            'div.ds-static-div',  # DSpace content
            'main',              # HTML5 main content
            'article',           # HTML5 article element
            '#content',          # Generic content ID
            'div.content'        # Generic content class
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove unwanted elements
                for elem in content_elem.select('script, style, nav, header, footer'):
                    elem.decompose()
                
                text = content_elem.get_text(separator=' ', strip=True)
                if text and len(text) > 100:  # Only return if we have meaningful content
                    return text
        
        # If we can't find a content container, look for PDF link
        pdf_link = soup.select_one('a[href$=".pdf"]')
        if pdf_link and pdf_link.get('href'):
            pdf_url = urljoin(url, pdf_link.get('href'))
            logger.info(f"Found PDF link: {pdf_url}")
            
            # Just extract metadata since we can't parse PDF
            metadata = []
            
            # Try to get the title
            title_elem = soup.select_one('h1') or soup.select_one('h2')
            if title_elem:
                metadata.append(f"Title: {title_elem.get_text(strip=True)}")
                
            # Try to get the abstract
            abstract_elem = soup.select_one('div.abstract') or soup.select_one('div.description')
            if abstract_elem:
                metadata.append(f"Abstract: {abstract_elem.get_text(strip=True)}")
                
            # Include the snippet from search results as fallback
            if doc_info.get('abstract'):
                metadata.append(doc_info['abstract'])
                
            # Add PDF link note
            metadata.append(f"Note: Full text available as PDF at {pdf_url}")
            
            return " ".join(metadata)
        
        # Last resort: just get the body text
        body = soup.select_one('body')
        if body:
            for elem in body.select('script, style, nav, header, footer'):
                elem.decompose()
            return body.get_text(separator=' ', strip=True)
            
        return None
    
    except Exception as e:
        logger.error(f"Error fetching document content from {url}: {str(e)}")
        return None

def documents_from_cdc_search(query: str, max_results: int = 5) -> List[Document]:
    """
    Search stacks.cdc.gov and convert results to Document objects.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of Document objects
    """
    search_results = search_cdc_stacks(query, max_results)
    documents = []
    
    for result in search_results:
        # Try to fetch the full content
        content = fetch_document_content(result)
        
        # If content retrieval failed, use the abstract
        if not content:
            content = result.get('abstract', '')
            logger.info(f"Using abstract as fallback for {result['url']}")
            
        # Skip if we have no content
        if not content:
            logger.warning(f"No content retrieved for {result['url']}")
            continue
            
        # Create a source ID based on the URL
        url = result['url']
        source_id = f"cdc:{hashlib.md5(url.encode()).hexdigest()[:8]}"
        
        # Create document metadata
        metadata = {
            'source': source_id,
            'title': result.get('title', ''),
            'url': url,
            'metadata': result.get('metadata', ''),
            'query': query,
            'id': source_id  # Ensure ID is set for Chroma storage
        }
        
        # Create the document
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        
        documents.append(doc)
        logger.info(f"Created document for {source_id}: {result['title']}")
        
    logger.info(f"Created {len(documents)} documents from CDC search results")
    return documents

# For testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cdc_search.py <search query>")
        sys.exit(1)
        
    query = sys.argv[1]
    documents = documents_from_cdc_search(query)
    
    print(f"Found {len(documents)} documents for query: {query}")
    for i, doc in enumerate(documents):
        print(f"\nDocument {i+1}:")
        print(f"Title: {doc.metadata.get('title', 'N/A')}")
        print(f"Source: {doc.metadata.get('source', 'N/A')}")
        print(f"URL: {doc.metadata.get('url', 'N/A')}")
        print(f"Content length: {len(doc.page_content)} characters")
        print("First 200 chars: " + doc.page_content[:200] + "...")