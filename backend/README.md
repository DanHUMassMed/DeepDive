# FastAPI Chat with Ollama LLM using LangChain

This project demonstrates how to build a simple FastAPI application that interacts with a large language model (LLM) via LangChain. The LLM used in this case is the Ollama model. The application allows users to send a prompt to the model and get a response through an API.

## Prerequisites

- Python 3.10y+
- Pip for managing Python packages


## Installation
* `conda create -n deep-dive python=3.12 ipykernel`
* `conda activate deep-dive`
* `pip install -r requirements.txt`
### Runn with

```bash
uvicorn app.main:app --reload
```