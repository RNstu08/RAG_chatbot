# rag_chatbot_coeo/streamlit_app.py

import streamlit as st
import requests
import json # For parsing JSON response if necessary

# Configuration for the FastAPI backend
# This should match the address where your FastAPI app is running.
FASTAPI_BACKEND_URL = "http://127.0.0.1:8000/chat/" 

# --- UI Setup ---
st.set_page_config(page_title="My RAG Chatbot", layout="wide")
st.title("💬 My RAG Chatbot")
st.caption("Ask questions and get answers from the local RAG-powered AI!")

# --- Initialize Conversation History in Session State ---
# Streamlit's session_state allows us to preserve variables across reruns (user interactions)
if "messages" not in st.session_state:
    st.session_state.messages = [] # List to store {'role': 'user'/'assistant', 'content': 'message'}

# --- Display Existing Messages ---
# Loop through the messages in session_state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]): # 'user' or 'assistant'
        st.markdown(message["content"])

# --- User Input Handling ---
# `st.chat_input` provides a specialized input field at the bottom of the app
user_query = st.chat_input("Ask your question here:")

if user_query:
    # 1. Add user's message to history and display it
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Get chatbot's response
    try:
        # Display a spinner while waiting for the backend
        with st.spinner("Thinking..."):
            payload = {"query": user_query}
            response = requests.post(FASTAPI_BACKEND_URL, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            response_data = response.json() # Parse JSON response
            bot_answer = response_data.get("answer", "Sorry, I couldn't get a proper answer.")

        # 3. Add chatbot's response to history and display it
        st.session_state.messages.append({"role": "assistant", "content": bot_answer})
        with st.chat_message("assistant"):
            st.markdown(bot_answer)

    except requests.exceptions.RequestException as e:
        error_message = f"Error connecting to the chatbot API: {e}"
        st.error(error_message)
        # Add error to chat so user sees it
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"): # Display error in assistant's bubble
            st.error(error_message) # Using st.error for visual distinction
            
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
             st.error(error_message)