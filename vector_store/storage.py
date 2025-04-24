import json
import os
import pickle
import streamlit as st
from pathlib import Path
import numpy as np

class VectorStore:
    """A simple vector store implementation for document chunks."""

    def __init__(self, vector_dir):
        """Initialize the vector store."""
        self.vector_dir = Path(vector_dir)
        self.embeddings_file = self.vector_dir / "embeddings.pkl"
        self.documents_file = self.vector_dir / "documents.json"
        self.metadata_file = self.vector_dir / "metadata.json"

        self.document_embeddings = []
        self.document_texts = []
        self.metadata = {}  

        
        self.vector_dir.mkdir(exist_ok=True, parents=True)

        
        self._load()

    def add_documents(self, texts, embeddings, metadata=None):
        """Add documents and their embeddings to the store."""
        if (not texts or len(texts) == 0 or
                embeddings is None or
                (isinstance(embeddings, np.ndarray) and embeddings.size == 0)):
            return

        if len(texts) != len(embeddings):
            raise ValueError("Number of texts and embeddings must match")

        
        self.document_texts.extend(texts)

        
        if isinstance(embeddings, np.ndarray):
            embeddings_list = embeddings.tolist()
        else:
            embeddings_list = embeddings

        self.document_embeddings.extend(embeddings_list)

        
        if metadata:
            if isinstance(metadata, list):
                for i, text in enumerate(texts):
                    self.metadata[text] = metadata[i]  
            else:
                for text in texts:
                    self.metadata[text] = metadata  
        else:
            for text in texts:
                self.metadata[text] = {}  

        self._save()

    def _save(self):
        """Save state to disk."""
        

    def _load(self):
        """Load state from disk if available."""
        

    def get_stats(self):
        """Get statistics about the vector store."""
        return {
            "document_count": len(self.document_texts),
            "metadata": len(self.metadata)
        }

    def clear(self):
        """Clear the vector store."""
        self.document_embeddings = []
        self.document_texts = []
        self.metadata = {}
        self._save()

    def search(self, query_embedding, top_k=5, score_threshold=0.0):
        """Search for similar embeddings."""
        
        """Search for documents similar to the query embedding."""
        if not self.document_embeddings:
            return []
        
        
        query_np = np.array(query_embedding)
        
        
        docs_np = np.array(self.document_embeddings)
        
       
        similarities = np.dot(docs_np, query_np) / (
            np.linalg.norm(docs_np, axis=1) * np.linalg.norm(query_np)
        )
        
        
        valid_indices = [i for i, score in enumerate(similarities) if score >= score_threshold]
        sorted_indices = sorted(valid_indices, key=lambda i: similarities[i], reverse=True)[:top_k]
        
        
        results = []
        for idx in sorted_indices:
            results.append({
                "text": self.document_texts[idx],
                "score": float(similarities[idx]),
                "index": idx
            })
        
        return results
    
    def clear(self):
        """Clear all documents and embeddings."""
        self.document_embeddings = []
        self.document_texts = []
        self.metadata = {}
        
        
        if self.embeddings_file.exists():
            self.embeddings_file.unlink()
        if self.documents_file.exists():
            self.documents_file.unlink()
        if self.metadata_file.exists():
            self.metadata_file.unlink()
    
    def _save(self):
        """Save current state to disk."""
        
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.document_embeddings, f)
        
        
        with open(self.documents_file, 'w', encoding='utf-8') as f:
            json.dump(self.document_texts, f, ensure_ascii=False, indent=2)
        
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _load(self):
        """Load state from disk if available."""
        try:
            
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'rb') as f:
                    self.document_embeddings = pickle.load(f)
            
            
            if self.documents_file.exists():
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    self.document_texts = json.load(f)
            
            
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    
        except Exception as e:
            st.error(f"Error loading vector store: {str(e)}")
            
            self.document_embeddings = []
            self.document_texts = []
            self.metadata = {}
    
    def get_stats(self):
        """Get statistics about the vector store."""
        return {
            "document_count": len(self.document_texts),
            "metadata": self.metadata
        }