import numpy as np
import re
import streamlit as st
import os
import google.generativeai as genai

class Embeddings:
    """Class to handle embeddings for RAG system using Google Generative AI."""
    
    def __init__(self, max_text_length=10000):
        """Initialize the embeddings model."""
        self.api_key = "AIzaSyA0gqQS8UEF1CtDC1SRlAH9CI8kLrlLA64"  
        self.model = None
        self.embedding_dimension = 768  
        self.max_text_length = max_text_length
        self._setup()
    
    def _setup(self):
        """Set up the embeddings model."""
        try:
            
            genai.configure(api_key=self.api_key)
            
            
            try:
               
                self.model = genai.GenerativeModel('embedding-001')
            except Exception:
                
                try:
                    self.model = genai.embedding.get_embedding_model('embedding-001')
                except Exception as e:
                    st.warning(f"Error setting up embeddings: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            st.warning(f"Error configuring embeddings: {str(e)}")
            return False
    
    def _truncate_text(self, text):
        """Truncate text to avoid size limits."""
        
        cleaned_text = self._clean_text(text)
        return cleaned_text[:self.max_text_length]
    
    def get_embedding(self, text):
        """Get embedding for a single text using Google's embedding model."""
        if not text:
            return np.zeros(self.embedding_dimension)
        
        
        text = self._truncate_text(text)
        
        try:
            if self.model:
                
                try:
                    
                    result = self.model.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    
                    
                    embedding = result["embedding"]
                    return np.array(embedding)
                except Exception:
                    
                    result = genai.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    return np.array(result["embedding"])
            else:
                
                return self._fallback_embedding(text)
        except Exception as e:
            st.warning(f"Error getting embedding: {str(e)}")
            return self._fallback_embedding(text)
    
    def get_embeddings(self, texts):
        """Get embeddings for multiple texts."""
        if not texts:
            return []
        
        
        cleaned_texts = [self._truncate_text(text) for text in texts]
        
        
        embeddings = []
        for text in cleaned_texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def _clean_text(self, text):
        """Clean text for better embedding quality."""
        if not text:
            return ""
            
        
        text = str(text)
        
        
        text = re.sub(r'\s+', ' ', text)
        
        
        text = re.sub(r'[^\w\s.,;:?!-]', '', text)
        
        return text.strip()
    
    def _fallback_embedding(self, text):
        """Create a simple fallback embedding when API is not available."""
        
        
        words = re.findall(r'\w+', text.lower())
        unique_words = list(set(words))
        
        
        embedding = np.zeros(min(self.embedding_dimension, len(unique_words) + 100))
        
        for i, word in enumerate(unique_words[:self.embedding_dimension-100]):
            
            count = words.count(word)
            # Normalize by text length
            if len(words) > 0:
                embedding[i] = count / len(words)
        
        
        if len(embedding) < self.embedding_dimension:
            embedding = np.pad(embedding, (0, self.embedding_dimension - len(embedding)))
        
        
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def similarity_search(self, query_embedding, document_embeddings, top_k=5):
        """Find the most similar documents to the query."""
        if len(document_embeddings) == 0:
            return []
        
        
        query_embedding = np.array(query_embedding)
        document_embeddings = np.array(document_embeddings)
        
        
        similarities = np.dot(document_embeddings, query_embedding) / (
            np.linalg.norm(document_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        
        results = [
            {"index": int(idx), "score": float(similarities[idx])}
            for idx in top_indices
        ]
        
        return results