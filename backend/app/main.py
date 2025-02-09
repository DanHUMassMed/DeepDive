from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.llms import Ollama
from pydantic import BaseModel

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows React app to make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Define the Pydantic model for the request body
class PromptRequest(BaseModel):
    prompt: str

# Initialize the Ollama LLM
llm = Ollama(model="deepseek-r1:32b")  # Replace with the actual model name if needed

# Function to send a prompt to the model
def sendPrompt(prompt: str) -> str:
    return llm(prompt)

# API endpoint to get the response from the model
@app.post("/chat/")
async def chat(request: PromptRequest):
    response = sendPrompt(request.prompt)
    print("Response:", response)
    print("Type:", type(response))
    return {"response": response}