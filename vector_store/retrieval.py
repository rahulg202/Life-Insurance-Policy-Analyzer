import streamlit as st
from .embeddings import Embeddings
from .storage import VectorStore
from utils.text_processing import chunk_text, clean_policy_text

class RAGRetriever:
    """Retrieval-Augmented Generation (RAG) system for policy documents."""
    
    def __init__(self, vector_dir):
        """Initialize the RAG system."""
        self.vector_dir = vector_dir
        self.embeddings = Embeddings()
        self.vector_store = VectorStore(vector_dir)
    
    def process_document(self, document_text, metadata=None):
        """Process a document and add it to the vector store."""
        if not document_text:
            return False
        
        # Clean the document text
        cleaned_text = clean_policy_text(document_text)
        
        # Chunk the document
        chunks = chunk_text(cleaned_text, chunk_size=1000, overlap=200)
        
        if not chunks:
            return False
        
        # Create embeddings for chunks
        chunk_embeddings = self.embeddings.get_embeddings(chunks)
        
        # Add to vector store
        self.vector_store.add_documents(chunks, chunk_embeddings, metadata)
        
        return True
    
    def retrieve(self, query, top_k=5):
        """Retrieve relevant document chunks for a query."""
        if not query:
            return []
        
        # Get query embedding
        query_embedding = self.embeddings.get_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k, score_threshold=0.3)
        
        return results
    
    def get_augmented_prompt(self, query, top_k=3):
        """Create an augmented prompt with retrieved context."""
        # Retrieve relevant chunks
        results = self.retrieve(query, top_k=top_k)
        
        if not results:
            return query, []
        
        # Format retrieved context
        contexts = []
        for i, result in enumerate(results):
            context = {
                "text": result["text"],
                "score": result["score"]
            }
            contexts.append(context)
        
        # Create augmented prompt
        context_text = "\n\n".join([f"Context [{i+1}]: {context['text']}" for i, context in enumerate(contexts)])
        
        augmented_prompt = f"""Use the following contexts to answer the question. If the contexts don't contain relevant information, use your general knowledge but prioritize the information in the contexts.

{context_text}

Question: {query}

Answer:"""
        
        return augmented_prompt, contexts
    
    def clear(self):
        """Clear the vector store."""
        self.vector_store.clear()
    
    def get_stats(self):
        """Get statistics about the RAG system."""
        return self.vector_store.get_stats()