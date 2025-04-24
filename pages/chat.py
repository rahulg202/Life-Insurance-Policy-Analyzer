import streamlit as st
from models.extraction import HumanMessage, AIMessage
from models.ai_service import AIService
from vector_store.retrieval import RAGRetriever
from utils.policy_type import detect_policy_type

def chat_with_policy_page(vector_dir):
    """Page for chatting with the policy using RAG."""
    if st.session_state.document_info is None:
        st.warning("Please upload a policy document first!")
        return
    
    st.header("Chat with Your Policy")
    
    # Initialize components if not already done
    if 'chat_ai_service' not in st.session_state:
        st.session_state.chat_ai_service = AIService()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize RAG retriever
    retriever = RAGRetriever(vector_dir)
    
    # Check if vector store has been initialized
    if not st.session_state.vector_store_initialized:
        st.warning("Vector store not initialized. Please re-upload your policy document.")
        return
    
    # Display chat messages in a scrollable container
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    for message in st.session_state.chat_history:
        if message.type == "human":
            st.markdown(f"<div class='user-message'>{message.content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-message'>{message.content}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add some suggested questions based on policy type
    st.markdown("### Suggested Questions")
    
    policy_type = detect_policy_type(st.session_state.document_info)
    
    # Create different suggested questions based on policy type
    if "Annuity" in policy_type or "Pension" in policy_type:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("How much annuity will I receive?"):
                user_query = "How much annuity will I receive and how often?"
                process_chat_query(user_query, retriever)
        
        with col2:
            if st.button("What happens after vesting date?"):
                user_query = "What happens after my policy vesting date?"
                process_chat_query(user_query, retriever)
        
        with col3:
            if st.button("What are the surrender options?"):
                user_query = "What are my surrender options and how much would I get?"
                process_chat_query(user_query, retriever)
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("What is my policy term?"):
                user_query = "What is my policy term and premium payment term?"
                process_chat_query(user_query, retriever)
        
        with col2:
            if st.button("Explain my death benefits"):
                user_query = "Can you explain the death benefits in my policy?"
                process_chat_query(user_query, retriever)
        
        with col3:
            if st.button("What are the policy exclusions?"):
                user_query = "What are the major exclusions in my policy?"
                process_chat_query(user_query, retriever)
    
    # Additional useful questions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Can I take a loan on my policy?"):
            user_query = "Can I take a loan on my policy? What are the terms?"
            process_chat_query(user_query, retriever)
    
    with col2:
        if st.button("How to change nominee?"):
            user_query = "How can I change the nominee in my policy?"
            process_chat_query(user_query, retriever)
    
    with col3:
        if st.button("What if I miss premium payment?"):
            user_query = "What happens if I miss a premium payment?"
            process_chat_query(user_query, retriever)
    
    # Chat input with proper handling to prevent infinite loop
    user_query = st.text_input("Ask a question about your policy...", key="chat_input")
    
    # Only process if there's an actual query and the user has pressed Enter
    if user_query and user_query != "":
        # Check if this is a new query (not already in history)
        is_new_query = True
        if st.session_state.chat_history:
            last_message = st.session_state.chat_history[-1]
            if last_message.type == "human" and last_message.content == user_query:
                is_new_query = False
        
        if is_new_query:
            process_chat_query(user_query, retriever)

def process_chat_query(user_query, retriever):
    """Process a chat query using RAG."""
    # Check if query already exists in history to prevent duplicates
    for message in st.session_state.chat_history:
        if message.type == "human" and message.content == user_query:
        # Query already exists, don't add it again
            return
    
    # Add to chat history
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    # Generate response with RAG
    with st.spinner("Thinking..."):
        try:
            # Check if AI service is initialized
            if not st.session_state.chat_ai_service:
                st.session_state.chat_ai_service = AIService()
                if not st.session_state.chat_ai_service.setup():
                    error_message = "Sorry, I couldn't connect to the AI service. Please try again later."
                    st.session_state.chat_history.append(AIMessage(content=error_message))
                    st.rerun()
                    return
            
            # Get augmented prompt using RAG retriever
            augmented_prompt, contexts = retriever.get_augmented_prompt(user_query)
            
            # Generate response
            result = st.session_state.chat_ai_service.generate_content(
                augmented_prompt, 
                temperature=0.2, 
                max_tokens=1024
            )
            
            if "error" in result:
                error_message = f"Sorry, I couldn't process your question. Error: {result['error']}"
                st.session_state.chat_history.append(AIMessage(content=error_message))
                st.rerun()
                return
            
            ai_response = result["text"]
            
            # Add citations to response if contexts were found
            if contexts:
                ai_response += "\n\n**Sources:**"
                for i, context in enumerate(contexts[:2], 1):  # Show top 2 sources
                    score = context['score']
                    # Only include high confidence sources
                    if score > 0.6:
                        # Format and trim context for citation
                        ctx_text = context['text']
                        if len(ctx_text) > 150:
                            ctx_text = ctx_text[:150] + "..."
                        ai_response += f"\n<div class='citation'>{i}. {ctx_text}</div>"
            
            # Add to chat history
            st.session_state.chat_history.append(AIMessage(content=ai_response))
            
            # Clear input field by rerunning the app
            st.session_state.chat_input = ""
            st.rerun()
            
        except Exception as e:
            error_message = f"Sorry, I couldn't process your question. Error: {str(e)}"
            st.session_state.chat_history.append(AIMessage(content=error_message))
            st.rerun()