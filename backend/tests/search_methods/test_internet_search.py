import pytest
import os
from unittest.mock import patch, MagicMock

from app.search_methods.internet_search import ddg_search, tavily_search
from app.utils.logging_utilities import setup_logging, trace

logger = setup_logging("test")


# Mocking DDGS and TavilyClient for testing
@pytest.fixture
def mock_ddgs():
    with patch("duckduckgo_search.DDGS") as mock:
        yield mock


@pytest.fixture
def mock_tavily_client():
    with patch("tavily.TavilyClient") as mock:
        yield mock


@pytest.fixture
def set_tavily_api_key():
    os.environ["TAVILY_API_KEY"] = "dummy_api_key"
    yield
    del os.environ["TAVILY_API_KEY"]


# Test ddg_search function
def test_ddg_search(mock_ddgs):
    query = "who is the president of the united states of america in 2025"
    max_results = 2

    response = ddg_search(query, max_results)

    assert len(response) == 2
    logger.debug(response)





# # Test tavily_search function with valid API key and mock response
# def test_tavily_search_success(mock_tavily_client, set_tavily_api_key):
#     mock_tavily_instance = MagicMock()
#     mock_tavily_client.return_value = mock_tavily_instance
#     mock_tavily_instance.search.return_value = {
#         "results": [
#             {"title": "Result 1", "url": "https://example.com", "content": "Description of result 1"},
#             {"title": "Result 2", "url": "https://example2.com", "content": "Description of result 2"}
#         ]
#     }

#     query = "python"
#     max_results = 2

#     response = tavily_search(query, max_results)

#     assert len(response) == 2
#     assert response[0]["title"] == "Result 1"
#     assert response[1]["href"] == "https://example2.com"


# # Test tavily_search function with invalid API key (missing key)
# def test_tavily_search_api_key_missing():
#     del os.environ["TAVILY_API_KEY"]  # Simulate missing API key

#     query = "python"

#     with pytest.raises(Exception):
#         tavily_search(query)


# # Test tavily_search function when ddg_search is used as fallback
# def test_tavily_search_fallback_to_ddg(mock_ddgs, mock_tavily_client, set_tavily_api_key):
#     # Mock TavilyClient to raise an exception
#     mock_tavily_instance = MagicMock()
#     mock_tavily_client.return_value = mock_tavily_instance
#     mock_tavily_instance.search.side_effect = Exception("Tavily API error")

#     # Mock ddg_search to return mock data
#     mock_ddgs_instance = MagicMock()
#     mock_ddgs.return_value = mock_ddgs_instance
#     mock_ddgs_instance.text.return_value = [
#         {"title": "Fallback Result 1", "href": "https://example3.com", "body": "Description of result 3"},
#         {"title": "Fallback Result 2", "href": "https://example4.com", "body": "Description of result 4"}
#     ]

#     query = "python"
#     max_results = 2

#     response = tavily_search(query, max_results)

#     assert len(response) == 2
#     assert response[0]["title"] == "Fallback Result 1"
#     assert response[1]["href"] == "https://example4.com"


# # Test tavily_search function with youtube results filtered out
# def test_tavily_search_filter_youtube(mock_tavily_client, set_tavily_api_key):
#     mock_tavily_instance = MagicMock()
#     mock_tavily_client.return_value = mock_tavily_instance
#     mock_tavily_instance.search.return_value = {
#         "results": [
#             {"title": "Result 1", "url": "https://example.com", "content": "Description of result 1"},
#             {"title": "Youtube Video", "url": "https://youtube.com/video", "content": "Description of youtube video"}
#         ]
#     }

#     query = "python"
#     max_results = 3

#     response = tavily_search(query, max_results)

#     assert len(response) == 1
#     assert response[0]["title"] == "Result 1"
#     assert "youtube.com" not in response[0]["href"]