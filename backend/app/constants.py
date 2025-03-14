# constants.py

PROMPTS_FILENAME = "prompts.json"
BLACKLIST_FILENAME = "blacklist.json"
DEFAULT_LLM = "llama3.2:1b"
DEFAULT_SYSTEM_PROMPT = (
    "Answer all questions to the best of your ability. " 
    "Answer concisely but correctly. If you do not know the answer, just say 'I don’t know.'"
    )
REACT_APP_LOCALHOST="http://localhost:3000"
REACT_APP_127_0_0_1="http://127.0.0.1:3000"
OLLAMA_URL="http://localhost:11434/api/tags"