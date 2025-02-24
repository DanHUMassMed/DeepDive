import pytest
import json
import os
from datetime import datetime
from unittest.mock import patch, mock_open
from app.chat_history_manager import ChatHistoryManager, ChatHistoryItem
import logging

# Configure the logger
logging.basicConfig(
    filename='debug.log',        # Log file name
    filemode='a',              # Append mode; use 'w' to overwrite
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG       # Set the logging level
)


def mock_data():
    return [
        {
            "project_id": "my-second-project",
            "project_name": "my-second-project",
            "project_start_date": "2025-02-24 07:32:35 AM",
            "chat_history_timestamp": "2025-02-24 07:32:35.262",
            "chat_history_items": []
        },
        {
            "project_id": "my-first-project",
            "project_name": "my-first-project",
            "project_start_date": "2025-02-24 07:32:35 AM",
            "chat_history_timestamp": "2025-02-24 07:32:35.261",
            "chat_history_items": []
        },
        {
            "project_id": "deep-dive",
            "project_name": "deep-dive",
            "project_start_date": "2025-02-24 07:32:35 AM",
            "chat_history_timestamp": "2025-02-24 08:02:40.954",
            "chat_history_items": [
                {
                    "project_id": "deep-dive",
                    "chat_id": "893c5dc2-9ca8-4a5d-9562-f2ae4abc41b6",
                    "chat_start_date": "2025-02-24 07:59:38 AM",
                    "chat_title": "Chat on 2025-02-24 07:59:38 AM",
                    "chat_llm_name": "deep.seekr1:32b",
                    "active_chat": False
                },
                {
                    "project_id": "deep-dive",
                    "chat_id": "4edea6c2-a59a-43e2-98cb-8a33beba89b6",
                    "chat_start_date": "2025-02-24 07:45:40 AM",
                    "chat_title": "Not Active",
                    "chat_llm_name": "deep.seekr1:32b",
                    "active_chat": True
                }
            ]
        }
    ]

@pytest.fixture
def chat_history_manager():
    # Use a temporary file or mock file loading
    with patch('app.chat_history_manager.ChatHistoryManager._file_name', "resources/test_chat_history.json"):
        with patch('app.chat_history_manager.ChatHistoryManager._load_project_state', return_value=mock_data()):
            manager = ChatHistoryManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests
    ChatHistoryManager._instance = None

def test_get_chat_history(chat_history_manager):
    result = chat_history_manager.get_chat_history('deep-dive')
    assert len(result) == 2
    assert result[0]['chat_id'] == '893c5dc2-9ca8-4a5d-9562-f2ae4abc41b6'
    assert result[1]['chat_id'] == '4edea6c2-a59a-43e2-98cb-8a33beba89b6'

def test_delete_chat_history(chat_history_manager):
    chat_history_manager.delete_chat_history('deep-dive')
    result = chat_history_manager.get_chat_history('deep-dive')
    assert len(result) == 0
    

def test_create_chat_history_item(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive')
    result = chat_history_manager.create_chat_history_item(new_chat_item)
    assert result['project_id'] == 'deep-dive'
    assert result['active_chat'] is True
    assert 'chat_id' in result
    assert 'chat_start_date' in result
    logging.debug(f"results {result}")
        
def test_update_chat_history_item_title(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='893c5dc2-9ca8-4a5d-9562-f2ae4abc41b6', chat_title='Updated Chat Title')
    chat_history_manager.update_chat_history_item_title(new_chat_item)
    result = chat_history_manager.get_chat_history('deep-dive')
    assert result[0]['chat_title'] == 'Updated Chat Title'

def test_delete_chat_history_item(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='893c5dc2-9ca8-4a5d-9562-f2ae4abc41b6')
    result = chat_history_manager.delete_chat_history_item(new_chat_item)
    remaining_chats = chat_history_manager.get_chat_history('deep-dive')
    assert len(remaining_chats) == 1
    assert remaining_chats[0]['chat_id'] == '4edea6c2-a59a-43e2-98cb-8a33beba89b6'

def test_delete_active_chat_history_item(chat_history_manager):
    chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='4edea6c2-a59a-43e2-98cb-8a33beba89b6')
    result = chat_history_manager.delete_chat_history_item(chat_item)
    remaining_chats = chat_history_manager.get_chat_history('deep-dive')
    assert len(remaining_chats) == 1
    assert remaining_chats[0]['chat_id'] == '893c5dc2-9ca8-4a5d-9562-f2ae4abc41b6'
    assert remaining_chats[0]['active_chat'] is True

def test_get_active_chat(chat_history_manager):
    active_chat = chat_history_manager.get_active_chat('deep-dive')
    assert active_chat['chat_id'] == '4edea6c2-a59a-43e2-98cb-8a33beba89b6'
    assert active_chat['active_chat'] is True

def test_set_active_chat(chat_history_manager):
    chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='893c5dc2-9ca8-4a5d-9562-f2ae4abc41b6')
    chat_history_manager.set_active_chat(chat_item)
    chat_history = chat_history_manager.get_chat_history('deep-dive')
    assert chat_history[0]['active_chat'] is True
    assert chat_history[1]['active_chat'] is False