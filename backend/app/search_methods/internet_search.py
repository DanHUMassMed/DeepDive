    
import os
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException, RatelimitException, TimeoutException
from tavily import TavilyClient
import requests
from requests.exceptions import RequestException
import time
from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging()
    
@trace(logger)
def ddg_search(query, max_results=5, retries=3, timeout=10):
    """Perform a search using DuckDuckGo's API with retry and timeout handling."""
    search_response = []
    attempt = 0
    while attempt < retries:
        try:
            ddg = DDGS(timeout=timeout)
            search_response = ddg.text(
                query,
                region="wt-wt",
                safesearch="off",
                timelimit="y",
                backend="lite",
                max_results=max_results,
            )
            break  # Exit loop if search is successful
        except RatelimitException as e:
            attempt += 1
            wait_time = min(2 ** attempt, 30)  # Exponential backoff with a max wait time of 30 seconds
            logger.debug(f"Rate limit exceeded: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except TimeoutException as e:
            attempt += 1
            wait_time = min(2 ** attempt, 30)
            logger.debug(f"Timeout error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        except DuckDuckGoSearchException as e:
            attempt += 1
            wait_time = min(2 ** attempt, 30)
            logger.debug(f"DuckDuckGo search error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    else:
        logger.debug("Maximum retries reached. Returning empty search response.")
    return search_response

@trace(logger)
def searxng_search(query, max_results=5, retries=3, timeout=10):
    searxng_url = "https://searxng.danhiggins.org/search"
    
    # Define your search query parameters
    params = {
        "q": query,
        "format": "json"
    }
    
    # Initialize variables for retry logic
    attempt = 0
    last_exception = None
    
    while attempt < retries:
        try:
            # Send the request to the SearxNG instance with timeout
            response = requests.get(searxng_url, params=params, timeout=timeout)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON response
                json_response = response.json()
                
                # Get results with a fallback to an empty list
                json_response_results = json_response.get("results", [])
                
                # Limit results if needed
                json_response_results = json_response_results[:max_results]
                
                # Map the response
                json_response_mapped = [
                    {
                        'href': item.get('url', ''),
                        'title': item.get('title', ''),
                        'body': item.get('content', '')
                    }
                    for item in json_response_results
                    if any(key in item for key in ('url', 'title', 'content'))
                ]
                        
                return json_response_mapped
            else:
                last_exception = f"Error: HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            last_exception = f"Timeout after {timeout} seconds"
        except RequestException as e:
            last_exception = f"Request failed: {str(e)}"
        
        # Increment attempt count and wait before retrying (with exponential backoff)
        attempt += 1
        if attempt < retries:
            wait_time = min(2 ** attempt, 30)  # Max wait time of 30 seconds
            print(f"Attempt {attempt} failed: {last_exception}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    # If all retries failed, raise an exception with the last error
    raise Exception(f"All {retries} attempts failed. Last error: {last_exception}")

def tavily_search(query, max_results=7):
    """Tavily is a search engine built specifically for AI agents (LLMs).
    As of May 2024 Tavily has Free tier allows 1,000 Free searches per month
    https://tavily.com/
    """
    try:
        api_key = os.environ["TAVILY_API_KEY"]
        client = TavilyClient(api_key)
    except:
        raise Exception(
            "Tavily API key not found. Please set the TAVILY_API_KEY environment variable. "
            "You can get a key at https://app.tavily.com"
        )

    try:
        # Search the query
        results = client.search(query, search_depth="advanced", max_results=max_results)
        # Return the results
        print(results)
        print("="*40)
        search_response = [
            {"title": result["title"], "href": result["url"], "body": result["content"]}
            for result in results.get("results", [])
        ]
    except Exception as e:  # Fallback in case overload on Tavily Search API
        logger.debug(f"tavily_search Error: {e}")
        search_response = ddg_search(query, max_results)

    search_response = [
        obj for obj in search_response if "youtube.com" not in obj["href"]
    ]
    return search_response

    