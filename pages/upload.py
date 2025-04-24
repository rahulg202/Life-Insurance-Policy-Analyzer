import streamlit as st
import os
import tempfile
from pathlib import Path
from models.extraction import PolicyExtractor
from utils.policy_type import detect_policy_type
from vector_store.retrieval import RAGRetriever
from utils.text_processing import chunk_text

def upload_policy_page(upload_dir, vector_dir):
    """Page for uploading and processing policy documents."""
    st.header("Upload Insurance Policy")
    st.write("Upload your life insurance policy document for analysis")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
    
    # Initialize RAG retriever
    retriever = RAGRetriever(vector_dir)
    
    if uploaded_file is not None:
        with st.spinner("Processing document..."):
            # Save uploaded file to temporary location
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Create permanent save path
            save_path = os.path.join(upload_dir, uploaded_file.name)
            
            # Extract policy information
            policy_extractor = PolicyExtractor()
            document_text, doc_info, extraction_stats, annuity_option_explanation = policy_extractor.process_document(
                uploaded_file, temp_file_path
            )
            
            if document_text and doc_info:
                # Store document information in session state
                st.session_state.uploaded_document = uploaded_file.name
                st.session_state.document_text = document_text
                st.session_state.document_info = doc_info
                st.session_state.extraction_stats = extraction_stats
                st.session_state.annuity_option_explanation = annuity_option_explanation
                
                # Save document to permanent location
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Process document for RAG system
                metadata = {
                    "filename": uploaded_file.name,
                    "policy_number": doc_info.get("policy_identification", {}).get("policy_number"),
                    "insurer": doc_info.get("policy_identification", {}).get("insurer_name"),
                    "plan_name": doc_info.get("policy_identification", {}).get("plan_name")
                }
                
                with st.spinner("Creating vector database for chat functionality..."):
                    # Clear existing data for this document
                    retriever.clear()
                    
                    # Add document to vector store
                    retriever.process_document(document_text, metadata)
                    
                    # Mark as initialized
                    st.session_state.vector_store_initialized = True
                
                st.success(f"Document processed successfully: {uploaded_file.name}")
                
                # Show extraction statistics
                st.markdown("<div class='extraction-stats'>", unsafe_allow_html=True)
                st.markdown(f"**Extraction Summary:**")
                st.markdown(f"- Fields analyzed: {extraction_stats['total_fields']}")
                st.markdown(f"- Fields successfully extracted: {extraction_stats['filled_fields']} ({int(extraction_stats['percentage'])}%)")
                policy_type = detect_policy_type(doc_info)
                st.markdown(f"- Detected policy type: **{policy_type}**")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Show help message
                st.info("👈 Use the sidebar navigation to explore different aspects of your policy")
                
                # Display a sample of the extracted text
                with st.expander("Document Preview"):
                    st.text(document_text[:1500] + "..." if len(document_text) > 1500 else document_text)
                
                # Show extracted information preview if available
                with st.expander("Extracted Information Preview"):
                    policy_identification = st.session_state.document_info.get("policy_identification", {})
                    
                    # Display policy identification info if available
                    if policy_identification.get("policy_number"):
                        st.markdown(f"**Policy Number:** {policy_identification.get('policy_number')}")
                    else:
                        st.markdown("<div class='missing-info'>Policy number could not be extracted from the document.</div>", unsafe_allow_html=True)
                        
                    if policy_identification.get("insurer_name"):
                        st.markdown(f"**Insurer:** {policy_identification.get('insurer_name')}")
                    else:
                        st.markdown("<div class='missing-info'>Insurer name could not be extracted from the document.</div>", unsafe_allow_html=True)
                        
                    if policy_identification.get("plan_name"):
                        st.markdown(f"**Plan Name:** {policy_identification.get('plan_name')}")
                    else:
                        st.markdown("<div class='missing-info'>Plan name could not be extracted from the document.</div>", unsafe_allow_html=True)
                        
                    if policy_identification.get("uin"):
                        st.markdown(f"**UIN:** {policy_identification.get('uin')}")
                    
                    # Show policy term and premium payment term if available
                    if policy_identification.get("policy_term"):
                        st.markdown(f"**Policy Term:** {policy_identification.get('policy_term')}")
                    
                    if policy_identification.get("premium_payment_term"):
                        st.markdown(f"**Premium Payment Term:** {policy_identification.get('premium_payment_term')}")
                    
                    # Preview financial details if available
                    financial_details = st.session_state.document_info.get("financial_details", {})
                    
                    st.markdown("---")
                    st.markdown("**Financial Highlights:**")
                    
                    financial_items = [
                        ("Sum Assured", "sum_assured"),
                        ("Premium Amount", "premium_amount"),
                        ("Purchase Price", "purchase_price"),
                        ("Annuity Amount", "annuity_amount")
                    ]
                    
                    found_any = False
                    for label, key in financial_items:
                        if financial_details.get(key):
                            st.markdown(f"- **{label}:** {financial_details.get(key)}")
                            found_any = True
                    
                    if not found_any:
                        st.markdown("<div class='missing-info'>Financial details could not be extracted from the document.</div>", unsafe_allow_html=True)
                    
                    # Show number of exclusions found
                    exclusions = st.session_state.document_info.get("exclusions_clauses", {}).get("all_exclusions", [])
                    if exclusions:
                        st.markdown(f"**Exclusions Found:** {len(exclusions)}")
                        # Show first few exclusions as preview
                        for i, exclusion in enumerate(exclusions[:2]):  # Show only first 2
                            if isinstance(exclusion, dict):
                                title = exclusion.get('title', f'Exclusion {i+1}')
                                st.markdown(f"- **{title}**")
                        if len(exclusions) > 2:
                            st.markdown(f"*... and {len(exclusions) - 2} more exclusions*")
                    else:
                        # Check if traditional exclusions are available
                        suicide_clause = st.session_state.document_info.get("exclusions_clauses", {}).get("suicide_clause")
                        if suicide_clause:
                            st.markdown("- **Suicide Clause** is present")
                        else:
                            st.markdown("<div class='missing-info'>Exclusions could not be extracted from the document.</div>", unsafe_allow_html=True)
            else:
                st.error("Failed to extract information from the document. Please try again with a different file.")