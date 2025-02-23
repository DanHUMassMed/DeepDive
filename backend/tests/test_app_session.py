import json
import os
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Optional
import logging

from app.session_manager import UserSession

from pydantic.dataclasses import dataclass
# Configure the logger
logging.basicConfig(
    filename='debug.log',        # Log file name
    filemode='a',              # Append mode; use 'w' to overwrite
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.DEBUG       # Set the logging level
)


def test_get_chat_interactions_count():
    project_id="deep-dive"
    chat_id= "ea9123ff-9a8e-46c0-a53f-22b8f88e3202"
    user_session = UserSession(project_id)
    #user_session._db_path="/Users/dan/Code/LLM/DeepDive/backend/resources/checkpoints.db"
    interactions_count = user_session.get_chat_interactions_count(chat_id)
    logging.debug(f"test_get_chat_interactions_count {interactions_count}")
