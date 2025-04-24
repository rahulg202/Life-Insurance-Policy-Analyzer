import streamlit as st
import os
from pathlib import Path


from pages.upload import upload_policy_page
from pages.dashboard import policy_dashboard_page
from pages.benefits import policy_benefits_page
from pages.financial import financial_details_page
from pages.terms import terms_provisions_page
from pages.chat import chat_with_policy_page


from utils.ui_components import setup_css

def setup_directories():
    
    base_dir = Path("data")
    upload_dir = base_dir / "uploads"
    vector_dir = base_dir / "vector_db"
    
    for directory in [base_dir, upload_dir, vector_dir]:
        directory.mkdir(exist_ok=True)
    
    return str(upload_dir), str(vector_dir)

def main():
    
    upload_dir, vector_dir = setup_directories()
    
    
    st.set_page_config(
        page_title="Life Insurance Policy Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    
    setup_css()
    
    
    st.title("📄 Life Insurance Policy Analyzer")
    
    
    if 'uploaded_document' not in st.session_state:
        st.session_state.uploaded_document = None
    if 'document_text' not in st.session_state:
        st.session_state.document_text = None
    if 'document_info' not in st.session_state:
        st.session_state.document_info = None
    if 'extraction_stats' not in st.session_state:
        st.session_state.extraction_stats = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'annuity_option_explanation' not in st.session_state:
        st.session_state.annuity_option_explanation = None
    if 'vector_store_initialized' not in st.session_state:
        st.session_state.vector_store_initialized = False
    
    
    st.sidebar.markdown('<div class="sidebar-title">Navigation</div>', unsafe_allow_html=True)
    page = st.sidebar.radio("", ["Upload Policy", "Policy Dashboard", "Policy Benefits", "Financial Details", "Terms & Provisions", "Chat with Policy"])
    
    
    with st.sidebar.expander("About This Tool"):
        st.markdown("""
        This application helps you analyze your life insurance policy documents, extract key information, and understand your policy benefits.
        
        **Features:**
        - Extract policy details automatically
        - Visualize key policy information
        - Understand benefits and provisions
        - Calculate financial projections
        - Chat with AI about your policy using RAG technology
        
        **Supported File Types:**
        - PDF (.pdf)
        - Word (.docx)
        - Text (.txt)
        """)
    
    
    if page == "Upload Policy":
        upload_policy_page(upload_dir, vector_dir)
    elif page == "Policy Dashboard":
        policy_dashboard_page()
    elif page == "Policy Benefits":
        policy_benefits_page()
    elif page == "Financial Details":
        financial_details_page()
    elif page == "Terms & Provisions":
        terms_provisions_page()
    elif page == "Chat with Policy":
        chat_with_policy_page(vector_dir)

if __name__ == "__main__":
    main()