import PyPDF2
import docx
import os
import tempfile
import streamlit as st
import re

def extract_text_from_pdf(file_path):
    """Extract text content from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"  # Add page breaks for better chunking later
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
    return text

def extract_text_from_docx(file_path):
    """Extract text content from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        return "\n\n".join(paragraphs)  # Add paragraph breaks for better chunking
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text content from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try another encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            st.error(f"Error reading text file: {str(e)}")
            return ""
    except Exception as e:
        st.error(f"Error reading text file: {str(e)}")
        return ""

def extract_text(file, file_path):
    """Extract text from various file formats."""
    if file.name.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file.name.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file.name.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        st.error("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
        return None

def chunk_text(text, chunk_size=1000, overlap=200):
    """
    Split text into chunks with specified size and overlap.
    This helps to maintain context across chunks for vector search.
    """
    if not text:
        return []
    
    # Split by paragraphs and then recombine into chunks of approximately chunk_size
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        paragraph_size = len(paragraph)
        
        if current_size + paragraph_size <= chunk_size:
            # Add to current chunk if it fits
            current_chunk.append(paragraph)
            current_size += paragraph_size
        else:
            # Save current chunk and start a new one
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                
                # Create overlap by keeping some paragraphs from the end of the previous chunk
                overlap_size = 0
                overlap_paragraphs = []
                
                for p in reversed(current_chunk):
                    p_size = len(p)
                    if overlap_size + p_size <= overlap:
                        overlap_paragraphs.insert(0, p)
                        overlap_size += p_size
                    else:
                        break
                        
                current_chunk = overlap_paragraphs
                current_size = overlap_size
            
            # Add the new paragraph to the current chunk
            current_chunk.append(paragraph)
            current_size += paragraph_size
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    
    return chunks

def clean_policy_text(text):
    """Clean and normalize policy text for better processing."""
    if not text:
        return ""
        
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common OCR errors in policy documents
    text = text.replace('|', 'I')  # Vertical bar often misrecognized as letter I
    text = text.replace('Rs.', '₹')  # Standardize rupee symbol
    text = text.replace('INR', '₹')
    
    # Fix numbered lists that might have been broken
    text = re.sub(r'(\d+)\s*\.\s*', r'\1. ', text)
    
    # Remove footer/header patterns that might appear throughout the document
    text = re.sub(r'Page \d+ of \d+', '', text)
    
    # Standardize section headings
    text = re.sub(r'SECTION\s+(\d+)', r'SECTION \1', text, flags=re.IGNORECASE)
    
    return text.strip()