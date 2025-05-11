
---
# RAG Chatbot with Local LLM

## Overview

This project is a Retrieval Augmented Generation (RAG) powered chatbot designed to answer user queries based on a custom knowledge base. It leverages a locally running Large Language Model (LLM) via Ollama, ensuring data privacy and cost-effectiveness. The application features a FastAPI backend for its core logic, a Streamlit web interface for user interaction, and Docker support for containerizing the backend.

The primary goal is to provide empathetic and contextually accurate answers by retrieving relevant information from a predefined set of FAQs and then using an LLM to generate a human-like response.

## Features

* **RAG Pipeline:** Implements a full Retrieve-Augment-Generate pipeline.
* **Local LLM:** Utilizes Ollama to run open-source LLMs (e.g., Llama 3, Mistral, Phi-3) locally.
* **Custom Knowledge Base:** Uses a JSON file for FAQs and ChromaDB as a local vector store.
* **FastAPI Backend:** Provides a robust and fast API for the chatbot service.
* **Streamlit UI:** Offers a simple and interactive web interface for chatting.
* **Dockerized Backend:** The FastAPI application can be containerized using Docker for portability and consistent deployments.
* **Modular Design:** Code is structured into services for chatbot logic, API, and UI.

## Technology Stack

* **Programming Language:** Python 3.9+
* **LLM Serving:** Ollama
* **LLM Example:** `koesn/llama3-8b-instruct:latest` (or other models like `llama3:8b-instruct`, `mistral:latest`, `phi3:medium`)
* **Embedding Model:** Sentence Transformers (e.g., `all-MiniLM-L6-v2`)
* **Vector Database:** ChromaDB (local, persistent)
* **Backend API:** FastAPI
* **API Server:** Uvicorn
* **Frontend UI:** Streamlit
* **HTTP Client (for UI):** Requests
* **Containerization:** Docker
* **Dependency Management:** Pip, Virtual Environment (`venv`)
* **Environment Variables:** `python-dotenv`

## Project Structure

```
rag_chatbot/
├── app/                      # Core application logic
│   ├── __init__.py
│   ├── chatbot_service.py    # RAG pipeline and LLM interaction logic
│   ├── main.py               # FastAPI application definition
│   └── knowledge_base/       # Knowledge base assets
│       ├── faqs.json         # FAQ data
│       └── vector_store/     # ChromaDB persistent storage
├── scripts/                  # Utility scripts
│   └── build_knowledge_base.py # Script to process faqs.json and populate ChromaDB
├── tests/                    # (Placeholder for automated tests)
├── .env                      # Local environment variables (gitignored)
├── .gitignore
├── .dockerignore
├── Dockerfile                # Dockerfile for the FastAPI backend
├── README.md                 # This file
├── requirements.txt          # Python dependencies
└── streamlit_app.py          # Streamlit UI application
```

## Setup and Installation

### Prerequisites

1.  **Python:** Version 3.9 or higher.
2.  **Ollama:** Installed and running. Download from [https://ollama.com/](https://ollama.com/).
3.  **Docker Desktop:** Installed and running (if you plan to use Docker for the backend). Download from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/).

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/RNstu08/RAG_chatbot.git](https://github.com/RNstu08/RAG_chatbot.git) # Replace with your repo URL if different
    cd RAG_chatbot
    ```

2.  **Create and Activate Python Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate.bat
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ollama Model Setup:**
    Pull your desired LLM via Ollama. For example, if you used `koesn/llama3-8b-instruct:latest` (as you mentioned):
    ```bash
    ollama pull koesn/llama3-8b-instruct:latest
    ```
    Ensure Ollama is running (usually an icon in the system tray or a background service).

5.  **Setup Environment Variables:**
    Create a `.env` file in the project root by copying from a template (if you provide one) or creating it manually. Add the following variables:
    ```env
    # .env
    OLLAMA_BASE_URL="http://localhost:11434/v1"
    OLLAMA_API_KEY="ollama" # Dummy key for Ollama, as it's not typically validated
    OLLAMA_MODEL_NAME="koesn/llama3-8b-instruct:latest" # Or your chosen Ollama model
    ```
    * **Note for Docker:** If running the backend in Docker and Ollama on the host, you might need to change `OLLAMA_BASE_URL` to `http://host.docker.internal:11434/v1` (see Docker running instructions).

## Building the Knowledge Base

1.  **Prepare FAQs:**
    Edit/Create `app/knowledge_base/faqs.json` with your questions and answers. Example format:
    ```json
    [
      {
        "id": "faq001",
        "question": "Sample question 1?",
        "answer": "This is the answer to sample question 1."
      },
      {
        "id": "faq002",
        "question": "Another sample question?",
        "answer": "Detailed answer for the second question."
      }
    ]
    ```

2.  **Run the Build Script:**
    Execute the script to process the FAQs, generate embeddings, and store them in ChromaDB.
    Make sure your virtual environment is active.
    ```bash
    python scripts/build_knowledge_base.py
    ```
    This will create/update the vector store in `app/knowledge_base/vector_store/`.

## Running the Application

Ensure Ollama is running with your chosen model available.

### Option 1: Local Development (FastAPI Backend + Streamlit UI, No Docker)

1.  **Start the FastAPI Backend Server:**
    In a terminal (with `venv` activated), from the project root:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    The API will be available at `http://127.0.0.1:8000`.

2.  **Start the Streamlit UI:**
    In another terminal (with `venv` activated), from the project root:
    ```bash
    streamlit run streamlit_app.py
    ```
    The UI will typically open in your browser at `http://localhost:8501`.

### Option 2: Running Backend with Docker (Streamlit UI still runs locally)

1.  **Build the Docker Image for the Backend:**
    From the project root:
    ```bash
    docker build -t rag-chatbot-api:latest .
    ```

2.  **Run the Dockerized Backend Container:**
    You need to ensure the container can reach Ollama running on your host and access the ChromaDB vector store.
    ```bash
    docker run --rm -p 8001:8000 \
               -e OLLAMA_BASE_URL="[http://host.docker.internal:11434/v1](http://host.docker.internal:11434/v1)" \
               -e OLLAMA_API_KEY="ollama" \
               -e OLLAMA_MODEL_NAME="koesn/llama3-8b-instruct:latest" \
               -v ./app/knowledge_base/vector_store:/app_code/app/knowledge_base/vector_store \
               --name my-rag-api \
               rag-chatbot-api:latest
    ```
    * The API will be available on your host at `http://localhost:8001` (or the host port you mapped).
    * `host.docker.internal` allows the container to connect to services on your Docker host machine (Windows/Mac Docker Desktop).
    * The volume mount (`-v ...`) ensures the container uses the ChromaDB data from your host.

3.  **Start the Streamlit UI:**
    In `streamlit_app.py`, make sure `FASTAPI_BACKEND_URL` points to the Dockerized backend (e.g., `http://127.0.0.1:8001/chat/` if you used host port 8001).
    Then, in a terminal (with `venv` activated), from the project root:
    ```bash
    streamlit run streamlit_app.py
    ```

## API Usage

The FastAPI backend provides the following:

* **Interactive API Documentation:**
    * Swagger UI: `http://<backend_address>/docs` (e.g., `http://127.0.0.1:8000/docs`)
    * ReDoc: `http://<backend_address>/redoc`
* **Chat Endpoint:**
    * `POST /chat/`
    * Request Body (JSON):
        ```json
        {
          "query": "Your question here"
        }
        ```
    * Response Body (JSON):
        ```json
        {
          "answer": "Chatbot's response here"
        }
        ```

## Using the Streamlit UI

1.  Ensure both the backend (FastAPI) and the Streamlit app are running.
2.  Open the Streamlit URL in your browser (e.g., `http://localhost:8501`).
3.  Type your question into the input box at the bottom of the page and press Enter.
4.  The chatbot's response will appear in the chat interface.

## Future Enhancements (Potential Next Steps)

* **Advanced Evaluation:** Implement more rigorous testing and evaluation metrics for RAG performance (e.g., RAGAS framework).
* **Cloud Deployment:** Deploy the FastAPI backend (and potentially Streamlit UI or a more robust frontend) to a cloud platform like Azure (e.g., Azure App Service for containers, Azure Functions).
* **CI/CD Pipeline:** Set up a CI/CD pipeline (e.g., GitHub Actions, Azure DevOps) to automate testing, Docker image builds, and deployments.
* **Improved Context Handling:** Implement more sophisticated context chunking, re-ranking, or summarization.
* **Conversation History Management:** Enhance the chatbot to handle multi-turn conversations with memory.
* **Fine-tuning:** Experiment with fine-tuning local LLMs on domain-specific data.
* **Scalable Vector Database:** For larger knowledge bases, integrate with a cloud-hosted or dedicated vector database solution.
* **User Authentication & Authorization:** If deploying for wider use.

---
