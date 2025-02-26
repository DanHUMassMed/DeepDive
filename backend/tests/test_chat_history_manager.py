import pytest
import json
import os
from datetime import datetime
from unittest.mock import patch, mock_open
from app.chat_history_manager import ChatHistoryManager, ChatHistoryItem
from app.utils.utilities import setup_logging
import copy
import inspect
import time

def get_current_method_name():
    return inspect.currentframe().f_code.co_name

logger = setup_logging(logger_nm="test")



def mock_data():
    data = [
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
                    "chat_id": "chat_id_1",
                    "chat_start_date": "2025-02-24 07:59:38 AM",
                    "chat_title": "Chat on 2025-02-24 07:59:38 AM",
                    "chat_llm_name": "deep.seekr1:32b",
                    "active_chat": False
                },
                {
                    "project_id": "deep-dive",
                    "chat_id": "chat_id_2",
                    "chat_start_date": "2025-02-24 07:45:40 AM",
                    "chat_title": "Not Active",
                    "chat_llm_name": "deep.seekr1:32b",
                    "active_chat": True
                }
            ]
        }
    ]
    logger.debug("mock_data loading")
    return copy.deepcopy(data)

@pytest.fixture
def chat_history_manager():
    # Use a temporary file or mock file loading
    with patch('app.chat_history_manager.ChatHistoryManager._file_name', None):
        with patch('app.chat_history_manager.ChatHistoryManager._load_project_state', return_value=mock_data()):
            with patch('app.chat_history_manager.ChatHistoryManager._BaseManager__save_project_state', return_value=None):
                manager = ChatHistoryManager.singleton()
    yield manager
    # Cleanup the singleton instance for other tests
    #logger.debug("Calling ChatHistoryManager._instance = None")
    time.sleep(1) 
    ChatHistoryManager._instance = None

def test_delete_chat_history_item(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='chat_id_1')
    results = chat_history_manager.delete_chat_history_item(new_chat_item)
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results}")
    remaining_chats = chat_history_manager.get_chat_history('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} remaining_chats={remaining_chats}")
    assert len(remaining_chats) == 1
    assert remaining_chats[0]['chat_id'] == 'chat_id_2'

def test_delete_active_chat_history_item(chat_history_manager):
    chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='chat_id_2')
    results = chat_history_manager.delete_chat_history_item(chat_item)
    remaining_chats = chat_history_manager.get_chat_history('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results}")
    assert len(remaining_chats) == 1
    assert remaining_chats[0]['chat_id'] == 'chat_id_1'
    assert remaining_chats[0]['active_chat'] is True


def test_get_active_chat(chat_history_manager):
    active_chat = chat_history_manager.get_active_chat('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={active_chat}")
    assert active_chat['chat_id'] == 'chat_id_2'
    assert active_chat['active_chat'] is True

def test_set_active_chat(chat_history_manager):
    chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='chat_id_1')
    chat_history_manager.set_active_chat(chat_item)
    chat_history = chat_history_manager.get_chat_history('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={chat_history}")
    assert chat_history[0]['active_chat'] is True
    assert chat_history[1]['active_chat'] is False
    
def test_update_chat_history_item_title(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive', chat_id='chat_id_1', chat_title='Updated Chat Title')
    chat_history_manager.update_chat_history_item_title(new_chat_item)
    results = chat_history_manager.get_chat_history('deep-dive')
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results}")
    assert results[0]['chat_title'] == 'Updated Chat Title'


def test_get_chat_history(chat_history_manager):
    result = chat_history_manager.get_chat_history('deep-dive')
    assert len(result) == 2
    assert result[0]['chat_id'] == 'chat_id_1'
    assert result[1]['chat_id'] == 'chat_id_2'

def test_delete_chat_history(chat_history_manager):
    chat_history_manager.delete_chat_history('deep-dive')
    result = chat_history_manager.get_chat_history('deep-dive')
    assert len(result) == 0
    


def test_create_chat_history_item(chat_history_manager):
    new_chat_item = ChatHistoryItem(project_id='deep-dive')
    results = chat_history_manager.create_chat_history_item(new_chat_item)
    assert results['project_id'] == 'deep-dive'
    assert results['active_chat'] is True
    assert 'chat_id' in results
    assert 'chat_start_date' in results
    logger.debug(f"{inspect.currentframe().f_code.co_name} results={results}")
        

