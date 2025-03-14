"""
This module provides an interface for interacting with the Ollama GPT models using 
the `ChatOllama` class from the `langchain_ollama` package.

"""
import os

from fastapi import WebSocket
from langchain_ollama import ChatOllama
from app.utils.logging_utilities import setup_logging,trace

logger = setup_logging()


class OLLAMA_Model:

    def __init__(self, model, temperature, max_tokens, websocket: WebSocket = None):
        self.websocket = websocket
        self.llm = ChatOllama(
            model=model, temperature=temperature, max_tokens=max_tokens
        )

    async def get_chat_response(self, llm_system_prompt, llm_user_prompt, stream=False):
        messages = [
            {"role": "system", "content": llm_system_prompt},
            {"role": "user", "content": f"task: {llm_user_prompt}"},
        ]

        response = ""
        if not stream:
            output = await self.llm.ainvoke(messages)
            response = output.content
        else:
            response = await self._get_stream_response(messages)

        return response

    async def _get_stream_response(self, messages):
        paragraph = ""
        response = ""

        async for chunk in self.llm.astream(messages):
            content = chunk.content
            if content is not None:
                response += content
                paragraph += content
                if "\n" in paragraph:
                    await self._send_output(paragraph)
                    paragraph = ""

        if paragraph:
            await self._send_output(paragraph)

        return response

        

    async def _send_output(self, content):
        logger.debug(f"_send_output {content=}")
        if self.websocket is not None:
            logger.debug(f"_send_output is not None")
            await self.websocket.send_text(content)
