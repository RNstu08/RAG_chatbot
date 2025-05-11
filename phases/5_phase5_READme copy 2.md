In this phase, we'll wrap our `ChatbotService` with a web API. This will allow other applications (like a future web frontend, mobile app, or other backend services) to interact with our chatbot over the network using standard HTTP requests. FastAPI is an excellent choice for this due to its high performance, ease of use, and automatic interactive documentation.

---

**Phase 5: API Development with FastAPI**

**1. API Design:**

* **What:** We'll design a simple RESTful API endpoint. For a chatbot, a common pattern is a `POST` request to a `/chat` or `/query` endpoint, sending the user's message in the request body and receiving the chatbot's response in the response body.
* **Why:**
    * **Standardization:** RESTful APIs are a widely adopted standard for web service communication.
    * **Decoupling:** Separates the chatbot logic (our `ChatbotService`) from how it's accessed.
    * **Interoperability:** Allows various clients to use the chatbot.
* **Key Concepts:**
    * **REST (Representational State Transfer):** An architectural style for designing networked applications.
    * **Endpoint:** A specific URL where an API can be accessed (e.g., `/chat`).
    * **HTTP Methods:** `POST` is suitable here as the client is sending data (the query) to create a new resource (the chatbot's response).
    * **Request/Response Body:** Data sent to and received from the API, typically in JSON format.
    * **Pydantic:** A Python library for data validation and settings management using Python type annotations. FastAPI uses it extensively to define request and response models, ensuring data integrity and providing clear schemas.

**2. Implement API Endpoint with FastAPI:**

* **File:** We'll create `rag_chatbot_coeo/app/main.py`.
* **Steps:**
    1.  Import necessary modules: `FastAPI` from `fastapi`, `BaseModel` from `pydantic` for request/response data structures, and our `ChatbotService` from `app.chatbot_service`.
    2.  Define Pydantic models for the request (containing the user's query) and the response (containing the chatbot's answer).
    3.  Create an instance of `FastAPI`.
    4.  Create an instance of our `ChatbotService`. For simplicity in this MVP, we'll create a global instance when the API server starts. For more complex applications, you might use FastAPI's dependency injection system.
    5.  Define the `/chat` endpoint function, which will use the `ChatbotService` to process the query and return the response.

Let's write the code for `app/main.py`:

```python
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
```

**Explanation:**

* **`QueryRequest` and `ChatResponse`**: These Pydantic models define the expected JSON structure for requests to `/chat/` and responses from it. FastAPI will automatically validate incoming requests against `QueryRequest` and serialize responses according to `ChatResponse`.
* **`app = FastAPI(...)`**: Creates an instance of the FastAPI application. We've added a title, description, and version, which will appear in the auto-generated documentation.
* **`chatbot_service_instance = ChatbotService()`**: We create one instance of our `ChatbotService` when the application starts. This instance will be shared across all requests. The `try-except` block around its initialization is important for catching startup errors.
* **`@app.post("/chat/", response_model=ChatResponse)`**:
    * `@app.post("/chat/")`: This decorator tells FastAPI that the function `handle_chat_query` should handle `POST` requests to the `/chat/` URL.
    * `response_model=ChatResponse`: This tells FastAPI to validate and serialize the return value of the function using the `ChatResponse` model.
    * `async def handle_chat_query(request: QueryRequest)`:
        * `async def`: FastAPI supports asynchronous code, which can be beneficial for I/O-bound operations. Our LLM call might be I/O-bound.
        * `request: QueryRequest`: FastAPI uses this type hint to validate the request body against the `QueryRequest` model. If validation fails, FastAPI automatically returns a 422 Unprocessable Entity error.
* **Error Handling:**
    * We check if `chatbot_service_instance` initialized correctly and raise a 503 Service Unavailable if not.
    * We check for empty queries and raise a 400 Bad Request.
    * A general `try-except` block catches other errors from the service and returns a 500 Internal Server Error.
* **`@app.get("/")`**: A simple root endpoint.
* **Logging**: Basic logging is added to help trace requests and errors.

**3. Run and Test API Locally:**

* **What:** Use `uvicorn`, an ASGI server, to run your FastAPI application locally.
* **Why:** `uvicorn` is a high-performance server recommended for FastAPI.
* **Commands (run from the root of your project, `rag_chatbot_coeo/`):**

    1.  **Ensure Ollama is Running:** Your Ollama server must be active, and the model (`koesn/llama3-8b-instruct:latest` or as specified in your `chatbot_service.py`) must be available to it.
    2.  **Activate Virtual Environment:**
        ```bash
        # On Windows Command Prompt
        .\venv\Scripts\activate.bat
        # Or on PowerShell
        # .\venv\Scripts\Activate.ps1
        ```
    3.  **Run Uvicorn:**
        ```bash
        uvicorn app.main:app --reload
        ```
        * `app.main`: Refers to the `main.py` file inside the `app` directory.
        * `:app`: Refers to the `FastAPI` instance named `app` inside `app/main.py`.
        * `--reload`: Enables auto-reloading. Uvicorn will restart the server whenever you save changes to your Python files. This is very useful during development.

        You should see output similar to:
        ```
        INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
        INFO:     Started reloader process [xxxxx] using statreload
        INFO:     Started server process [xxxxx]
        INFO:     Waiting for application startup.
        INFO:     Attempting to initialize ChatbotService...
        INFO:     Loading embedding model: all-MiniLM-L6-v2...
        INFO:     Embedding model loaded.
        INFO:     Connecting to ChromaDB at: D:\Machine_learning\Projects\genAI\rag_chatbot\app\knowledge_base\vector_store...
        INFO:     Getting collection: faq_collection...
        INFO:     Connected to ChromaDB collection 'faq_collection' with 3 items.
        INFO:     Initializing OpenAI client for Ollama at: http://localhost:11434/v1 with model: koesn/llama3-8b-instruct:latest...
        INFO:     OpenAI client for Ollama initialized.
        INFO:     ChatbotService initialized successfully via main.py.
        INFO:     Application startup complete.
        ```

* **Test with FastAPI's Automatic Interactive Docs (Swagger UI):**
    1.  Open your web browser and go to: **`http://127.0.0.1:8000/docs`**
    2.  You'll see the Swagger UI documentation for your API.
    3.  Expand the `/chat/` endpoint section.
    4.  Click "Try it out".
    5.  In the "Request body" text area, enter a JSON query like:
        ```json
        {
          "query": "What are my payment options?"
        }
        ```
    6.  Click "Execute".
    7.  You should see the server's response below, including the chatbot's answer, response headers, and the `curl` command equivalent.

* **Alternative Docs (ReDoc):** FastAPI also provides ReDoc documentation at `http://127.0.0.1:8000/redoc`.

* **Test with `curl` or Postman (Optional):**
    * **curl (from another terminal):**
      ```bash
      curl -X POST "http://127.0.0.1:8000/chat/" -H "Content-Type: application/json" -d "{\"query\": \"How can I verify this communication?\"}"
      ```
    * **Postman:** You can use Postman to send a `POST` request to `http://127.0.0.1:8000/chat/` with a JSON body.

---

This concludes Phase 5! You now have a working REST API for your RAG chatbot. This is a significant step towards making your chatbot accessible and integratable.

**Key Takeaways:**
* FastAPI makes it easy to build robust and performant APIs.
* Pydantic models ensure data validation and clear API contracts.
* `uvicorn` is used to serve the FastAPI application.
* Automatic API documentation (`/docs`, `/redoc`) is a huge productivity booster.

Next, we can briefly discuss **Phase 6: Simple User Interface (Optional)**, or move towards containerization and MLOps concepts.

How did the API setup go? Were you able to run it and test it via the `/docs` UI?