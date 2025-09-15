from __future__ import annotations
import os
from typing import List, Tuple
from langchain_chroma import Chroma
from langchain_core.documents import Document
import chromadb
from embeddings.embeddings import TextEmbedding, EmbeddingsFactory

class Retriever:
    """
    A class to retrieve documents and their similarity scores from a ChromaDB vector store.
    """
    def __init__(self, embedder: TextEmbedding, persist_directory: str = "./db"):
        """
        Initializes the Retriever.

        Args:
            embedder: An embedding model instance that conforms to the TextEmbedding interface.
            persist_directory: The directory where the ChromaDB database is stored.

        Raises:
            FileNotFoundError: If the persist_directory does not exist.
        """
        if not os.path.isdir(persist_directory):
            raise FileNotFoundError(
                f"Persistence directory not found: '{persist_directory}'. "
                "Please ensure the database has been created and the path is correct."
            )
        self.embedder = embedder
        self.persist_directory = persist_directory
        # This client is used for lightweight operations like checking for collections
        self._client = chromadb.PersistentClient(path=self.persist_directory)

    def _collection_exists(self, collection_name: str) -> bool:
        """Checks if a collection exists in the database."""
        collections = self._client.list_collections()
        return any(c.name == collection_name for c in collections)

    def retrieve_with_scores(
        self,
        query: str,
        collection_name: str,
        k: int = 4,
    ) -> List[Tuple[Document, float]]:
        """
        Retrieves the top k most similar documents for a given query and returns them 
        with their cosine similarity scores.

        Args:
            query: The query string to search for.
            collection_name: The name of the collection to search within.
            k: The number of documents to retrieve.

        Raises:
            ValueError: If the specified collection_name does not exist.

        Returns:
            A list of tuples, where each tuple contains a retrieved Document and its 
            cosine similarity score (higher is better, 1.0 is a perfect match).
        """
        if not self._collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist in the database at '{self.persist_directory}'.")

        # Initialize the specific vector store for this query
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedder.inner,
            persist_directory=self.persist_directory,
        )

        # Retrieve documents with their distance scores.
        # For cosine metrics, Chroma returns a distance score (0 for identical, >0 for different).
        docs_with_distance = vector_store.similarity_search_with_score(query, k=k)

        # Convert distance scores to cosine similarity scores (1 - distance)
        docs_with_similarity = []
        for doc, distance_score in docs_with_distance:
            similarity_score = 1 - distance_score
            docs_with_similarity.append((doc, similarity_score))

        return docs_with_similarity

if __name__ == "__main__":
    # --- This block demonstrates how to use the Retriever on an EXISTING database ---
    
    print("--- 1. Initializing Retriever and Embedder ---")
    try:
        bge_embedder = EmbeddingsFactory.create(kind="bge")
        # Assumes the database is in the default './db' directory
        retriever = Retriever(embedder=bge_embedder, persist_directory="./vector_db")
        print("Retriever initialized successfully.\n")

        # --- 2. Retrieving documents from an existing collection ---
        print("--- 2. Retrieving documents from 'with_context' collection ---")
        query = "How does the WERSA algorithm work?"
        collection_to_query = "with_context" # Change this to your desired collection name

        retrieved_docs = retriever.retrieve_with_scores(
            query=query,
            collection_name=collection_to_query,
            k=1
        )

        if retrieved_docs:
            print(f"Query: '{query}'")
            print(f"Top {len(retrieved_docs)} retrieved documents from '{collection_to_query}':")
            for doc, score in retrieved_docs:
                print(f"  - Cosine Similarity: {score:.4f}")
                print(f"    Content: '{doc.page_content}'")
                print(f"    Metadata: {doc.metadata}\n")
        else:
            print(f"No documents found in '{collection_to_query}' for the query: '{query}'\n")

    except (FileNotFoundError, ValueError) as e:
        print(f"An error occurred during retrieval: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")