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
            'project_id': 'project1',
            'chat_id': 'chat1',
            'chat_start_date': '2023-01-01 12:00 PM',
            'chat_title': 'First Chat',
            'chat_llm_name': 'model1',
            'active_chat': True
        },
        {
            'project_id': 'project1',
            'chat_id': 'chat2',
            'chat_start_date': '2023-01-02 01:00 PM',
            'chat_title': 'Second Chat',
            'chat_llm_name': 'model2',
            'active_chat': False
        },
        {
            'project_id': 'project2',
            'chat_id': 'chat12',
            'chat_start_date': '2023-01-02 01:00 PM',
            'chat_title': 'Second Chat p2',
            'chat_llm_name': 'model2',
            'active_chat': True
        }
    ]

@pytest.fixture
def chat_history_manager():
    # Use a temporary file or mock file loading
    with patch('app.chat_history_manager.ChatHistoryManager._file_name', "resources/test_chat_history.json"):
        with patch('app.chat_history_manager.ChatHistoryManager._load_chat_history', return_value=mock_data()):
            manager = ChatHistoryManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests
    ChatHistoryManager._instance = None

def test_get_chat_history(chat_history_manager):
    result = chat_history_manager.get_chat_history('project1')
    assert len(result) == 2
    assert result[0]['chat_id'] == 'chat1'
    assert result[1]['chat_id'] == 'chat2'

def test_delete_chat_history(chat_history_manager):
    chat_history_manager.delete_chat_history('project1')
    assert chat_history_manager.get_chat_history('project1') == []

def test_create_chat_history_item(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='project2')
    result = chat_history_manager.create_chat_history_item(new_chat_item)
    assert result['project_id'] == 'project2'
    assert result['active_chat'] is True
    assert 'chat_id' in result
    assert 'chat_start_date' in result
    assert result['chat_llm_name'] == 'deep.seekr1:32b'
    logging.debug(f"results {result}")
        
def test_update_chat_history_item_title(chat_history_manager):
    chat_history_manager.update_chat_history_item_title('chat1', 'Updated Chat Title')
    assert chat_history_manager.chat_history_data[0]['chat_title'] == 'Updated Chat Title'

def test_update_chat_history_item_model_name(chat_history_manager):
    chat_history_manager.update_chat_history_item_model_name('chat1', 'Updated Chat Model')
    assert chat_history_manager.chat_history_data[0]['chat_llm_name'] == 'Updated Chat Model'

def test_delete_chat_history_item(chat_history_manager):
    chat_history_manager.delete_chat_history_item('chat1')
    remaining_chats = chat_history_manager.get_chat_history('project1')
    assert len(remaining_chats) == 1
    assert remaining_chats[0]['chat_id'] == 'chat2'

def test_get_active_chat(chat_history_manager):
    active_chat = chat_history_manager.get_active_chat('project1')
    assert active_chat['chat_id'] == 'chat1'
    assert active_chat['active_chat'] is True

def test_set_active_chat(chat_history_manager):
    chat_history_manager.set_active_chat('chat2')
    assert chat_history_manager.chat_history_data[1]['active_chat'] is True
    assert chat_history_manager.chat_history_data[0]['active_chat'] is False