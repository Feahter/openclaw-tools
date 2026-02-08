"""
ChromaDB Operations Module

Provides functions for ChromaDB vector database operations including:
- Collection management
- Document embedding and storage
- Similarity search
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any


class ChromaDBManager:
    """Manager for ChromaDB operations."""
    
    def __init__(self, persist_directory: str = None, embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize ChromaDB manager.
        
        Args:
            persist_directory: Directory to persist database. If None, uses in-memory database.
            embedding_model: Name of the sentence-transformers model to use.
        """
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
        else:
            self.client = chromadb.Client(
                Settings(anonymized_telemetry=False)
            )
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, str]] = None,
        embedding_function=None
    ) -> Any:
        """
        Create a new collection.
        
        Args:
            name: Name of the collection.
            metadata: Optional metadata for the collection.
            embedding_function: Custom embedding function (optional).
        
        Returns:
            The created collection.
        """
        if embedding_function is None:
            embedding_function = self._default_embedding_function
        
        return self.client.create_collection(
            name=name,
            metadata=metadata,
            embedding_function=embedding_function
        )
    
    def delete_collection(self, name: str) -> None:
        """
        Delete a collection by name.
        
        Args:
            name: Name of the collection to delete.
        """
        self.client.delete_collection(name=name)
    
    def list_collections(self) -> List[str]:
        """
        List all collection names.
        
        Returns:
            List of collection names.
        """
        return [col.name for col in self.client.list_collections()]
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadata: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """
        Add documents to a collection with automatic chunking and embedding.
        
        Args:
            collection_name: Name of the collection.
            documents: List of documents to add.
            metadata: Optional metadata for each document.
            ids: Optional custom IDs for each document.
            embeddings: Pre-computed embeddings (if None, will be generated).
            chunk_size: Size of text chunks for splitting long documents.
            chunk_overlap: Overlap between chunks.
        
        Returns:
            Dictionary containing count of added documents.
        """
        # Get or create collection
        collection = self.client.get_collection(collection_name)
        
        # Auto-chunk documents if needed
        if chunk_size > 0:
            chunked_documents = []
            chunked_metadata = []
            chunked_ids = []
            
            for i, doc in enumerate(documents):
                if len(doc) <= chunk_size:
                    chunked_documents.append(doc)
                    chunked_metadata.append(metadata[i] if metadata else None)
                    chunked_ids.append(ids[i] if ids else f"doc_{i}")
                else:
                    # Simple text chunking
                    chunks = self._chunk_text(doc, chunk_size, chunk_overlap)
                    for j, chunk in enumerate(chunks):
                        chunked_documents.append(chunk)
                        chunked_metadata.append(metadata[i] if metadata else None)
                        chunked_ids.append(f"{ids[i] if ids else f'doc_{i}'}_chunk_{j}" if ids else f"doc_{i}_chunk_{j}")
            
            documents = chunked_documents
            metadata = chunked_metadata
            ids = chunked_ids
        
        # Generate embeddings if not provided
        if embeddings is None:
            embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        collection.add(
            documents=documents,
            metadatas=metadata,
            ids=ids,
            embeddings=embeddings
        )
        
        return {"count": len(documents)}
    
    def search(
        self,
        query: str,
        collection_name: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        query_embeddings: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Perform similarity search in a collection.
        
        Args:
            query: Query text.
            collection_name: Name of the collection to search.
            n_results: Number of results to return.
            where: Optional metadata filter (e.g., {"source": "file1"}).
            where_document: Optional document content filter.
            query_embeddings: Pre-computed query embedding (if None, will be generated).
        
        Returns:
            Dictionary containing search results with documents, distances, and metadata.
        """
        collection = self.client.get_collection(collection_name)
        
        if query_embeddings is None:
            query_embedding = self.embedding_model.encode([query]).tolist()
        else:
            query_embedding = query_embeddings
        
        results = collection.query(
            query_texts=[query],
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"]
        )
        
        return {
            "ids": results.get("ids", [[]])[0],
            "documents": results.get("documents", [[]])[0],
            "metadatas": results.get("metadatas", [[]])[0],
            "distances": results.get("distances", [[]])[0]
        }
    
    def get_collection(self, name: str) -> Any:
        """
        Get a collection by name.
        
        Args:
            name: Name of the collection.
        
        Returns:
            The collection object.
        """
        return self.client.get_collection(name)
    
    def _default_embedding_function(self, input: List[str]) -> List[List[float]]:
        """
        Default embedding function using sentence-transformers.
        
        Args:
            input: List of texts to embed.
        
        Returns:
            List of embedding vectors.
        """
        return self.embedding_model.encode(input).tolist()
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk.
            chunk_size: Maximum size of each chunk.
            overlap: Overlap between chunks.
        
        Returns:
            List of text chunks.
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            
            if end >= len(text):
                break
            
            start = end - overlap
        
        return chunks


# Global manager instance
_manager: Optional[ChromaDBManager] = None


def _get_manager(persist_directory: str = None) -> ChromaDBManager:
    """Get or create the global manager instance."""
    global _manager
    if _manager is None:
        _manager = ChromaDBManager(persist_directory=persist_directory)
    return _manager


def create_collection(
    name: str,
    metadata: Optional[Dict[str, str]] = None,
    persist_directory: str = None
) -> Any:
    """
    Create a new collection.
    
    Args:
        name: Name of the collection.
        metadata: Optional metadata for the collection.
        persist_directory: Directory to persist database.
    
    Returns:
        The created collection.
    """
    manager = _get_manager(persist_directory)
    return manager.create_collection(name=name, metadata=metadata)


def add_documents(
    collection_name: str,
    documents: List[str],
    metadata: Optional[List[Dict]] = None,
    ids: Optional[List[str]] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    persist_directory: str = None
) -> Dict[str, Any]:
    """
    Add documents to a collection with automatic chunking and embedding.
    
    Args:
        collection_name: Name of the collection.
        documents: List of documents to add.
        metadata: Optional metadata for each document.
        ids: Optional custom IDs for each document.
        chunk_size: Size of text chunks for splitting long documents.
        chunk_overlap: Overlap between chunks.
        persist_directory: Directory to persist database.
    
    Returns:
        Dictionary containing count of added documents.
    """
    manager = _get_manager(persist_directory)
    return manager.add_documents(
        collection_name=collection_name,
        documents=documents,
        metadata=metadata,
        ids=ids,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )


def search(
    query: str,
    collection_name: str,
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None,
    persist_directory: str = None
) -> Dict[str, Any]:
    """
    Perform similarity search in a collection.
    
    Args:
        query: Query text.
        collection_name: Name of the collection to search.
        n_results: Number of results to return.
        where: Optional metadata filter.
        persist_directory: Directory to persist database.
    
    Returns:
        Dictionary containing search results with documents, distances, and metadata.
    """
    manager = _get_manager(persist_directory)
    return manager.search(
        query=query,
        collection_name=collection_name,
        n_results=n_results,
        where=where
    )


def delete_collection(name: str, persist_directory: str = None) -> None:
    """
    Delete a collection by name.
    
    Args:
        name: Name of the collection to delete.
        persist_directory: Directory to persist database.
    """
    manager = _get_manager(persist_directory)
    manager.delete_collection(name=name)


def list_collections(persist_directory: str = None) -> List[str]:
    """
    List all collection names.
    
    Args:
        persist_directory: Directory to persist database.
    
    Returns:
        List of collection names.
    """
    manager = _get_manager(persist_directory)
    return manager.list_collections()
