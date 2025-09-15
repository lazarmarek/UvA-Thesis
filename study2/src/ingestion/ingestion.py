from __future__ import annotations
import uuid
from typing import Sequence, Union, List, Optional, Dict, Any, Tuple
import os

from embeddings.embeddings import TextEmbedding, EmbeddingsFactory
from langchain_chroma import Chroma
from langchain_core.documents import Document

class Ingestor:
    """
    A class to handle the ingestion pipeline: embedding text and storing it in a vector store.
    """
    def __init__(self, embedder: TextEmbedding):
        self.embedder = embedder

    def _get_vector_store(self, persist_directory: str, collection_name: str) -> Chroma:
        """
        Initializes and returns a ChromaDB vector store instance.
        """
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embedder.inner,
            persist_directory=persist_directory,
        )

    def _prepare_documents(
        self,
        docs_or_texts: Union[str, Sequence[str], Sequence[Document]],
        ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[Document], List[str]]:
        """
        Converts input strings to Document objects or validates existing ones, and prepares IDs.
        """
        if isinstance(docs_or_texts, str):
            docs_or_texts = [docs_or_texts]

        # Check if the input is already Document objects
        if isinstance(docs_or_texts[0], Document):
            documents = list(docs_or_texts)
        else: # It's a list of strings, so we convert them
            if metadata:
                documents = [Document(page_content=text, metadata=meta) for text, meta in zip(docs_or_texts, metadata)]
            else:
                documents = [Document(page_content=text) for text in docs_or_texts]

        if ids is None:
            # Generate unique IDs if none are provided
            doc_ids = [str(uuid.uuid4()) for _ in documents]
        elif len(ids) != len(documents):
            raise ValueError("The number of documents and IDs must be the same.")
        else:
            doc_ids = ids
            
        return documents, doc_ids

    def ingest(
        self,
        texts: Union[str, Sequence[str], Sequence[Document]],
        collection_name: str,
        persist_directory: str,
        ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Embeds documents and adds them to a specified ChromaDB collection.
        Accepts raw strings or pre-formatted LangChain Document objects.
        """
        # Initialize the vector store
        vector_store = self._get_vector_store(persist_directory, collection_name)

        # Prepare the Document objects and their IDs
        docs, doc_ids = self._prepare_documents(texts, ids, metadata)

        # Add the Document objects to the collection
        vector_store.add_documents(
            documents=docs,
            ids=doc_ids
        )

        print(f"Successfully ingested {len(docs)} documents into collection '{collection_name}'.")
        return doc_ids

if __name__ == "__main__":
    # --- Example Usage ---

    # 1. Create the BGE embedder using your factory
    bge_embedder = EmbeddingsFactory.create(kind="bge")

    # 2. Instantiate the Ingestor with the embedder
    ingestor = Ingestor(embedder=bge_embedder)

    # 3. Define the data to be ingested
    docs_with_context = [
        "Chart Description: This bar chart shows a 50% increase in user engagement after the new feature launch. Context: The surrounding text discusses the success of the Q3 product update.",
        "Chart Description: A pie chart illustrating market share, with our company holding 30%. Context: The annual report highlights our competitive standing."
    ]
    docs_without_context = [
        "This is a bar chart with two bars.",
        "A pie chart is shown with three distinct segments."
    ]

    # 4. Ingest the data into two separate collections
    print("--- Ingesting documents with context ---")
    ingestor.ingest(
        texts=docs_with_context,
        collection_name="with_context",
        metadata=[{"source": "report_q3"}, {"source": "annual_report"}]
    )

    print("\n--- Ingesting documents without context ---")
    ingestor.ingest(
        texts=docs_without_context,
        collection_name="without_context"
    )