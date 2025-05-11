# rag_chatbot_coeo/app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging # For better logging

# Import our ChatbotService
# Assuming main.py is in the 'app' directory, alongside 'chatbot_service.py'
from .chatbot_service import ChatbotService 

# --- Logging Setup ---
# It's good practice to set up basic logging for your API.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Models for Request and Response ---

class QueryRequest(BaseModel):
    """Request model for user query."""
    query: str # The user's question

class ChatResponse(BaseModel):
    """Response model for chatbot's answer."""
    answer: str
    # You could add more fields later, e.g., retrieved_context_ids, confidence_score

# --- FastAPI Application Setup ---

app = FastAPI(
    title="RAG Chatbot API",
    description="An API for interacting with the RAG chatbot powered by a local LLM via Ollama.",
    version="0.1.0"
)

# --- Initialize Chatbot Service ---
# This creates a single instance of ChatbotService when the API starts.
# Error handling during service initialization is important.
try:
    logger.info("Attempting to initialize ChatbotService...")
    chatbot_service_instance = ChatbotService()
    logger.info("ChatbotService initialized successfully via main.py.")
except Exception as e:
    logger.error(f"Fatal error during ChatbotService initialization in main.py: {e}", exc_info=True)
    # If the service can't start, the API is not usable.
    # You might choose to exit or prevent FastAPI from fully starting,
    # but FastAPI will likely start and then endpoints will fail if the instance is None.
    # For now, we'll let it be None and handle it in the endpoint.
    chatbot_service_instance = None 

# --- API Endpoints ---

@app.post("/chat/", response_model=ChatResponse)
async def handle_chat_query(request: QueryRequest):
    """
    Receives a user query, gets a response from the RAG chatbot,
    and returns the chatbot's answer.
    """
    logger.info(f"Received query: {request.query}")

    if chatbot_service_instance is None:
        logger.error("ChatbotService is not available.")
        raise HTTPException(status_code=503, detail="Chatbot service is currently unavailable. Please check server logs.")

    if not request.query or not request.query.strip():
        logger.warning("Received empty query.")
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Get response from our RAG chatbot service
        bot_answer = chatbot_service_instance.get_rag_response(request.query)
        logger.info(f"Sending response: {bot_answer}")
        return ChatResponse(answer=bot_answer)
    except HTTPException:
        # Re-raise HTTPException if it's one we've deliberately raised
        raise
    except Exception as e:
        # Catch any other unexpected errors from the chatbot service
        logger.error(f"An unexpected error occurred while processing query '{request.query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/")
async def read_root():
    """A simple root endpoint to check if the API is running."""
    return {"message": "Welcome to the RAG Chatbot API. Use the /docs endpoint to see API documentation."}

# --- To run this application (from the project root 'rag_chatbot_coeo'): ---
# Ensure Ollama server is running and the model is available.
# Ensure your virtual environment is activated.
# Command: uvicorn app.main:app --reload
#
# Then open your browser to http://127.0.0.1:8000
# Or go to http://127.0.0.1:8000/docs for interactive API documentation.