"""
Search API retriever that fetches relevant documents based on a query.

NOTE: Helpful URLS for understanding and expanding the notions expressed in this code
https://blog.langchain.dev/improving-document-retrieval-with-contextual-compression/
https://medium.com/@SrGrace_/contextual-compression-langchain-llamaindex-7675c8d1f9eb
"""

from typing import Dict, List

from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.logging_utilities import setup_logging, trace
logger = setup_logging()

class SearchAPIRetriever(BaseRetriever):
    """Search API retriever."""

    pages: List[Dict] = []

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:

        docs = [
            Document(
                page_content=page.get("raw_content", ""),
                metadata={
                    "title": page.get("title", ""),
                    "source": page.get("url", ""),
                },
            )
            for page in self.pages
        ]

        return docs


class ContextCompressor:
    def __init__(self, documents, max_results=5, embeddings_provider_nm="ollama", similarity_threshold=0.38, **kwargs):
        self.max_results = max_results
        self.documents = documents
        self.kwargs = kwargs
        self.embeddings = self._get_embeddings_provider(embeddings_provider_nm)
        self.similarity_threshold = similarity_threshold
        self.unique_documents_visited = set()

    def _get_embeddings_provider(self, embeddings_provider_nm):
        """Map embeddings_provider_nm to a Langchain Embeddings Class"""
        embeddings = None
        match embeddings_provider_nm:
            case "ollama":
                from langchain_ollama import OllamaEmbeddings
                embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
            case "openai":
                from langchain_openai import OpenAIEmbeddings
                embeddings = OpenAIEmbeddings()
            case "huggingface":
                from langchain_huggingface import HuggingFaceEmbeddings
                embeddings = HuggingFaceEmbeddings()
            case _:
                error_msg = f"IN Config._get_embeddings_provider - Embedding provider not found. [{embeddings_provider_nm}]"
                logger.error(error_msg)
                
        return embeddings

    def _get_contextual_retriever(self):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        relevance_filter = EmbeddingsFilter(
            embeddings=self.embeddings, similarity_threshold=self.similarity_threshold
        )
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[splitter, relevance_filter]
        )
        base_retriever = SearchAPIRetriever(pages=self.documents)
        contextual_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=base_retriever
        )
        return contextual_retriever

    def _pretty_print_docs(self, docs, top_n):
        return f"\n".join(
            f"Source: {doc.metadata.get('source')}\n"
            f"Title: {doc.metadata.get('title')}\n"
            f"Content: {doc.page_content}\n"
            for i, doc in enumerate(docs)
            if i < top_n
        )


    @trace(logger)
    def get_context(self, query, max_results=5):
        compressed_docs = self._get_contextual_retriever()
        # relevant_docs = compressed_docs.get_relevant_documents(query)
        relevant_docs = compressed_docs.invoke(query)
        self.unique_documents_visited.update(
            doc.metadata.get("source")
            for i, doc in enumerate(relevant_docs)
            if i < max_results
        )
        return self._pretty_print_docs(relevant_docs, max_results)
