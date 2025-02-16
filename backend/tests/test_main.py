import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app, sendPrompt   # Assuming your file is named 'main.py'

client = TestClient(app)

# Test case for POST /chat/ endpoint
@patch("app.main.sendPrompt")
def test_chat(mock_sendPrompt):
    # Mock the response of sendPrompt
    mock_sendPrompt.return_value = "This is a test response."

    # Send a test request
    response = client.post("/chat/", json={"prompt": "Test prompt"})

    # Assert that the status code is 200 (OK)
    assert response.status_code == 200

    # Assert the structure of the returned response
    assert response.json() == {"response": "This is a test response."}

    # Ensure that sendPrompt was called with the correct argument
    mock_sendPrompt.assert_called_once_with("Test prompt")


# Test case for GET /available-models/ endpoint
def test_available_models():
    # Send a test request to the /available-models/ endpoint
    response = client.get("/available-models/")

    # Assert that the status code is 200 (OK)
    assert response.status_code == 200

    # Assert the structure of the returned response
    assert response.json() == ["deepseek-r1:32b"]


