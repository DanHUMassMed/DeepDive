    
import os
from duckduckgo_search import DDGS
from tavily import TavilyClient

def ddg_search(query, max_results=5):
    """DuckDuckGo is a free private search engine.
    As of May 2024 DuckDuckGo is Free with no search limits
    https://duckduckgo.com/
    
    NOTE: The results have been very good and I have been 
    using this as the default for much of the work
    """
    search_response = []
    try:
        ddg = DDGS()
        search_response = ddg.text(
            query,
            region="wt-wt",
            safesearch="off",
            timelimit="y",
            max_results=max_results,
        )
    except Exception as e:  # Fallback in case overload on Tavily Search API
        print(f"ddgs_search Error: {e}")

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
        print(f"tavily_search Error: {e}")
        search_response = ddg_search(query, max_results)

    search_response = [
        obj for obj in search_response if "youtube.com" not in obj["href"]
    ]
    return search_response

    