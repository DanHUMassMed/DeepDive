    
import os
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import DuckDuckGoSearchException, RatelimitException, TimeoutException
from tavily import TavilyClient

import time
from app.utils.logging_utilities import setup_logging

logger = setup_logging()
    

def ddg_search(query, max_results=5, retries=3):
    """DuckDuckGo is a free private search engine.
    As of May 2024 DuckDuckGo is Free with no search limits
    https://duckduckgo.com/
    
    NOTE: The results have been very good and I have been 
    using this as the default for much of the work
    """
    search_response = []
    attempt = 0
    while attempt < retries:
        try:
            ddg = DDGS(timeout=10)
            search_response = ddg.text(
                query,
                region="wt-wt",
                safesearch="off",
                timelimit="y",
                max_results=max_results,
            )
            break  # Exit loop if search is successful
        except RatelimitException as e:
            attempt += 1
            logger.debug(f"Rate limit exceeded: {e}. Retrying in 1 second...")
            if attempt < retries:
                time.sleep(1)
            else:
                logger.debug("Maximum retries reached. Exiting.")
                search_response = []  # or handle as needed
                break
        except TimeoutException as e:
            attempt += 1
            logger.debug(f"Timeout error: {e}. Retrying immediately...")
            if attempt >= retries:
                logger.debug("Maximum retries reached. Exiting.")
                search_response = []  # or handle as needed
                break
        except DuckDuckGoSearchException as e:
            attempt += 1
            logger.debug(f"DuckDuckGo search error: {e}. Retrying in 1 second...")
            if attempt < retries:
                time.sleep(1)
            else:
                logger.debug("Maximum retries reached. Exiting.")
                search_response = []  # or handle as needed
                break
    return search_response


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

    