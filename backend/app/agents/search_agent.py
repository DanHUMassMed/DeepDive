import asyncio
import json
import logging
import os
from datetime import datetime

from fastapi import WebSocket
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from app.utils.workspace_utilities import get_project_workspace
from app.agents.prompts import Prompts
from app.agents.llm_providers.ollama import OLLAMA_Model 
from app.search_methods.internet_search import ddg_search
from app.scrapers.scraper_methods import scrape_urls
from app.embedding_methods.compressor import ContextCompressor

from app.utils.logging_utilities import setup_logging,trace

logger = setup_logging()

class SearchAgent():
    def __init__(self, websocket: WebSocket=None, chat_id: str=None):
        self.websocket = websocket
        self.chat_id = chat_id
        self.prompts = Prompts()
        #TODO Make the model a configuration param
        self.llm_provider = OLLAMA_Model(model="qwen2.5-ctx_32k:32b", temperature=0, max_tokens=1000, websocket=websocket)
        #TODO Make the internet_search a configuration param
        self.internet_search = ddg_search
        
        self.visited_urls = []


    def checkpoint_chat_interactions(self, prompt, ai_response):
        db_path = f"{get_project_workspace()}/checkpoints.db"
        human_message = HumanMessage(content=prompt)
        ai_message = AIMessage(content=ai_response)
        with SqliteSaver.from_conn_string(db_path) as checkpointer:            
            config = {"configurable": {"thread_id": self.chat_id}}
            checkpointer.put(human_message, config=config)

            
        
    async def _send_output(self, content):
        """Send the llm output to the websocket"""
        if self.websocket is not None:
            logger.debug(f"_send_output is not None")
            await self.websocket.send_text(content)
            
    @trace(logger)
    async def internet_search_context(self, query: str):
        """Given a a query
        1. Find a list of related subtopic to search. (LLM)
        2. For each subtopic find a list of URLs. (Search Engine)
        3. For each URL scrape the web site for content.
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self._get_sub_queries(query) + [query]
        #sub_queries = [query]
        await self._send_output("_OK Let's try these queries: "+",".join(sub_queries)+"_<br>")
        
        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(
            *[self._process_internet_query(sub_query) for sub_query in sub_queries]
        )
        return context
    
    @trace(logger)
    async def generate_internet_search_report(self, query: str):
        context = await self.internet_search_context(query)
        internet_search_report = await self.write_internet_search_report(query, context)
        self.checkpoint_chat_interactions(query, internet_search_report)
        return internet_search_report

    @trace(logger)
    async def _get_sub_queries(self, query: str):
        """
        Given an query
        Request a list of sub queries that could appropriately answer the query
        """
        sub_queries =[]
        try:

            search_queries_prompt = self.prompts.get_prompt(
                "search_queries_prompt",
                number_of_queries = 3,
                task = query,
                datetime_now = datetime.now().strftime("%B %d, %Y")
            )

            system_prompt_search_agent = self.prompts.get_prompt("system_prompt_search_agent")
            
            chat_response = await self.llm_provider.get_chat_response(
                system_prompt_search_agent, search_queries_prompt
            )
            logging.debug("PROMPT get_sub_queries response = %s", chat_response)
            
            sub_queries = json.loads(chat_response)
            if not self._is_list_of_strings(sub_queries):
                logger.error(f"chat_response should be a list of strings but instead be we got {chat_response}")

        except Exception as e:
            logging.error("Error in get_sub_queries WILL ATTEMPT to recover %s", e)
            #sub_queries = await self._extract_json_from_string(
            #    chat_response, default_response
            #)

        return sub_queries
    
    @trace(logger)
    def _is_list_of_strings(self, test_object):
        if isinstance(test_object, list) and all(isinstance(item, str) for item in test_object):
            return True
        return False

    @trace(logger)
    async def _process_internet_query(self, sub_query: str):
        """Takes in a sub query and scrapes urls based on it and gathers context.
        """
        scraped_sites = await self._scrape_sites_by_query(sub_query)
        content = await self._get_similar_content_by_query(sub_query, scraped_sites)
        return content
    
    @trace(logger)
    async def _scrape_sites_by_query(self, sub_query):
        """Given a sub_query
        1. Call the configured internet search provider and retrieve a list of URLs
        2. Keep only the Unique URLs
        3. Scrape the proved site for content
        """
        search_results = self.internet_search(sub_query)
        
        new_search_urls = await self._keep_unique_urls(
            [url.get("href") for url in search_results]
        )
        scraped_content_results = scrape_urls(new_search_urls)
        return scraped_content_results
    
    @trace(logger)
    async def _keep_unique_urls(self, url_set_input):
        """Parse the URLS and remove any duplicates
        """
        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                self.visited_urls.append(url)
                new_urls.append(url)

        return new_urls
    
    @trace(logger)
    async def _get_similar_content_by_query(self, query, documents):
        """Instead of immediately returning retrieved documents as-is,
        they are compressed using the context of the given query,
        then only the relevant information is returned."""
        context_compressor = ContextCompressor(documents = documents)
        return context_compressor.get_context(query)
    
    @trace(logger)
    async def write_internet_search_report(self, query, context):
        """
        Generate a report based on the internet searches done
        """
        chat_response = ""
        report_prompt = self.prompts.get_prompt(
            "internet_search_report_prompt",
            context=context,
            question=query,
            total_words=100,
            report_format="APA",
            datetime_now=datetime.now().strftime("%B %d, %Y"),
        )
        
        system_prompt_search_agent = self.prompts.get_prompt("system_prompt_internet_search_report")
        try:
            chat_response = await self.llm_provider.get_chat_response(
                system_prompt_search_agent, report_prompt, stream=True
            )
            logging.debug("PROMPT write_report response = %s", chat_response)

        except Exception as e:
            print(f"Error in generate_report: {e}")

        return chat_response
