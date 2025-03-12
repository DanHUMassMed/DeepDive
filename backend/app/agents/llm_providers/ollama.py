"""
This module provides an interface for interacting with the Ollama GPT models using 
the `ChatOllama` class from the `langchain_ollama` package.

"""
import os

from langchain_ollama import ChatOllama


class OLLAMA_Model:

    def __init__(self, model, temperature, max_tokens):

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

        # Streaming the response using the astream method from langchain
        async for chunk in self.llm.astream(messages):
            content = chunk.content
            if content is not None:
                response += content
                paragraph += content
                # Potentials stream results
                if "\n" in paragraph:
                    print(f"{paragraph}")
                    paragraph = ""

        return response