import streamlit as st
import os
import tempfile
from utils.text_processing import extract_text
from models.ai_service import AIService

class PolicyExtractor:
    """Extract structured information from policy documents."""
    
    def __init__(self):
        """Initialize the policy extractor."""
        self.ai_service = AIService()
    
    def process_document(self, uploaded_file, temp_file_path):
        """Process an uploaded document and extract structured information."""
        # Extract text from document
        document_text = extract_text(uploaded_file, temp_file_path)
        
        if not document_text:
            return None, None, None
        
        # Extract policy information using AI service
        doc_info, extraction_stats = self.ai_service.extract_policy_info(document_text)
        
        # Get explanation of annuity option if available
        annuity_option_explanation = None
        if doc_info:
            annuity_option = doc_info.get("annuity_benefits", {}).get("annuity_option")
            if annuity_option:
                annuity_option_explanation = self.ai_service.explain_annuity_option(annuity_option)
        
        return document_text, doc_info, extraction_stats, annuity_option_explanation
    
    def validate_extraction(self, doc_info):
        """Validate extraction results and fill in any missing required fields."""
        if not doc_info:
            return False
        
        # Check that some minimal amount of information was extracted
        policy_id = doc_info.get("policy_identification", {})
        if not policy_id.get("policy_number") and not policy_id.get("plan_name") and not policy_id.get("insurer_name"):
            return False
        
        return True

# Message class definitions for chat history
class Message:
    def __init__(self, content):
        self.content = content

class HumanMessage(Message):
    def __init__(self, content):
        super().__init__(content)
        self.type = "human"

class AIMessage(Message):
    def __init__(self, content):
        super().__init__(content)
        self.type = "ai"