# Life Insurance Policy Analyzer

A comprehensive web application that uses AI to analyze life insurance policy documents, extract key information, and provide an interactive dashboard for users to understand their policies better. The application implements a Retrieval-Augmented Generation (RAG) pipeline for contextual Q&A with the policy document.

## Features

- **Document Processing**: Upload and analyze PDF, DOCX, or TXT insurance policy documents
- **Information Extraction**: Extract comprehensive policy details using AI
- **Interactive Dashboard**: Visualize key policy information
- **Financial Calculations**: Calculate surrender value, loan possibilities, and payment projections
- **Policy Benefits Analysis**: Understand survival, death, and maturity benefits
- **Terms & Provisions**: Review policy exclusions, clauses, and conditions
- **AI-powered Chat**: Ask questions about your policy using RAG technology

## Project Structure

```
.
├── app.py                  # Main application file
├── data/                   # Data storage directory
│   ├── uploads/            # Uploaded files directory
│   └── vector_db/          # Vector database storage
├── models/                 # AI model related code
│   ├── ai_service.py       # Interface for Gemini API
│   └── extraction.py       # Policy information extraction
├── pages/                  # Streamlit pages
│   ├── benefits.py         # Policy benefits page
│   ├── chat.py             # Chat with policy page
│   ├── dashboard.py        # Policy dashboard page
│   ├── financial.py        # Financial details page
│   ├── terms.py            # Terms & provisions page
│   └── upload.py           # Upload policy page
├── utils/                  # Utility functions
│   ├── date_utils.py       # Date formatting utilities
│   ├── financial_utils.py  # Financial calculations
│   ├── policy_type.py      # Policy type detection
│   ├── text_processing.py  # Text extraction and processing
│   └── ui_components.py    # UI components and styling
├── vector_store/           # RAG implementation
│   ├── embeddings.py       # Embeddings generation
│   ├── retrieval.py        # RAG retrieval system
│   └── storage.py          # Vector storage handling
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/rahulg202/Life-Insurance-Policy-Analyzer.git
   cd life-insurance-policy-analyzer
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. **Upload Policy**: Upload your life insurance policy document (PDF, DOCX, or TXT)
2. **Review Dashboard**: View extracted policy information on the dashboard
3. **Explore Policy Benefits**: Understand survival, death, and maturity benefits
4. **Review Financial Details**: Check premium/annuity projections and calculate surrender values
5. **Review Terms & Provisions**: Understand exclusions and special provisions
6. **Chat with Your Policy**: Ask questions about your policy using natural language

## Technology Stack

- **Frontend**: Streamlit
- **NLP & AI**: Google Gemini API, Sentence Transformers
- **Data Processing**: Pandas, NumPy
- **Text Extraction**: PyPDF2, python-docx
- **Data Visualization**: Matplotlib
- **Vector Database**: Custom implementation with sentence-transformers

## About RAG Implementation

This application features a Retrieval-Augmented Generation (RAG) pipeline for the chat functionality:

1. **Document Chunking**: The policy document is split into overlapping chunks during upload
2. **Vector Embeddings**: Each chunk is converted into embeddings using sentence-transformers
3. **Vector Storage**: Embeddings are stored in a custom vector database
4. **Retrieval**: When the user asks a question, the most relevant chunks are retrieved
5. **Augmented Prompt**: Retrieved chunks are combined with the user query to create a context-rich prompt
6. **Generation**: The Gemini API uses this augmented prompt to generate accurate, policy-specific answers

This approach ensures that responses are grounded in the actual policy document content.
