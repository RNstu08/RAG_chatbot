This phase is crucial for setting up all the software components we need, including Ollama for our local LLM, a Python environment for our code, and the necessary libraries.

---

**Phase 2: Development Environment Setup (with Ollama)**

**1. Ollama Installation and Model Setup (Local LLM Engine):**

Ollama will allow us to run powerful open-source large language models directly on your Windows machine.

* **What:** Install Ollama and download an initial LLM to serve locally.
* **Why:** This provides a free, private, and controllable LLM for our chatbot's generative capabilities. Running it locally is excellent for development, iteration, and data privacy. Ollama simplifies the often complex process of setting up and running these models.
* **How (on Windows):**
    1.  **Download Ollama:**
        * Go to the official Ollama website: [https://ollama.com/](https://ollama.com/)
        * Download the Windows installer.
    2.  **Install Ollama:**
        * Run the downloaded installer and follow the on-screen instructions. Ollama typically installs and runs in the background. You might see an icon in your system tray.
    3.  **Verify Ollama Installation (Optional but Recommended):**
        * Open a new Command Prompt or PowerShell window.
        * Type the command:
            ```bash
            ollama --version
            ```
        * This should display the installed Ollama version if the installation added Ollama to your system's PATH. If it doesn't work, Ollama might still be running. The key is that it's running in the background.
    4.  **Download an LLM (Pull a Model):**
        Ollama uses a `pull` command similar to Docker to download models from its library. We need to choose a model. Good starting points are often models that balance performance with resource requirements. For our RAG chatbot, an instruction-following model is ideal.
        * **Recommended starter models:**
            * `llama3:8b-instruct` (Meta's Llama 3, 8 billion parameters, instruction-tuned - very capable)
            * `mistral:latest` (Mistral AI's 7B model, good all-rounder)
            * `phi3:medium` (Microsoft's Phi-3 medium, a strong small language model)
        * Let's start by pulling `llama3:8b-instruct` as it's a powerful and recent model. Open Command Prompt or PowerShell and run:
            ```bash
            ollama pull koesn/llama3-8b-instruct
            ```
        * This will download the model. It might take some time depending on your internet speed and the model size (several gigabytes).
        * You can pull other models similarly (e.g., `ollama pull mistral`).
    5.  **Run a Model (and start the server if not already running):**
        * To ensure a model is working and Ollama's server is active (it usually starts on demand or on system startup), you can run a model directly from the command line:
            ```bash
            ollama run koesn/llama3-8b-instruct
            ```
        * This will load the model and give you a prompt where you can chat with it directly in your terminal (e.g., `>>> Send a message (/? for help)`). Type a message, press Enter.
        * To exit this interactive session, type `/bye`.
        * **Crucially, when you run a model or if Ollama is set to start with your system, it starts a local API server, typically at `http://localhost:11434`. This is the endpoint our Python application will connect to.**
    6.  **List Local Models:**
        * To see which models you have downloaded locally:
            ```bash
            ollama list
            ```

* **Alternatives (to Ollama for local LLMs):**
    * **LM Studio:** Another popular GUI tool for running local LLMs, also provides an OpenAI-compatible server.
    * **Hugging Face `transformers` library with manual model download:** More complex, requires more coding to set up the model serving part.
    * **GPT4All:** Provides a chat client and backend for running quantized models.

**2. Python Virtual Environment:**

* **What:** Create an isolated Python environment for this project.
* **Why:** Prevents dependency conflicts between projects, ensures reproducibility, and keeps your global Python installation clean.
* **Key Concepts:** `venv` (Python's built-in module for virtual environments).
* **Commands (run in your `rag_chatbot_coeo` project root directory using your VS Code terminal or any other terminal):**

    1.  **Navigate to your project directory:**
        (You should already be there from Phase 1)
    2.  **Create the virtual environment (if you haven't already from the previous guide's initial run-through):**
        Name it `venv`.
        ```bash
        python -m venv venv
        ```
        You'll see a `venv` folder. This is correctly in your `.gitignore`.
    3.  **Activate the virtual environment:**
        * **On Windows (Command Prompt):**
            ```bash
            .\venv\Scripts\activate.bat
            ```
        * **On Windows (PowerShell):**
            (You might need to set execution policy: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`)
            ```bash
            .\venv\Scripts\Activate.ps1
            ```
        Your terminal prompt should now be prefixed with `(venv)`.

**3. Install Core Libraries:**

* **What:** Install the Python packages needed for our application using `pip`.
* **Why:** These libraries provide the tools for vector embeddings, the vector database, the API framework, and interacting with Ollama's API.
* **Commands (ensure your virtual environment `(venv)` is active):**
    ```bash
    python.exe -m pip install --upgrade pip
    pip install sentence-transformers chromadb fastapi "uvicorn[standard]" python-dotenv pydantic openai
    ```
    (Optional but Recommended for PyTorch): If the above step for sentence-transformers fails or if you want more control (e.g., you need a specific CUDA version for GPU support), it's often best to install PyTorch directly from their official website's instructions (https://pytorch.org/get-started/locally/). They provide specific pip install commands based on your OS, package manager, and CUDA version. Once torch is successfully installed, then try pip install sentence-transformers again.
    
    ```bash
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    ```
    
    Let's review why these are important for *this* project:
    
    * `sentence-transformers`: For generating text embeddings locally.
    * `chromadb`: Our chosen local vector database.
    * `fastapi`: The web framework for building our REST API.
    * `uvicorn[standard]`: The ASGI server to run our FastAPI app.
    * `python-dotenv`: For loading environment variables from a `.env` file (useful for any configurations).
    * `pydantic`: Used by FastAPI for data validation and settings.
    * `openai`: **Yes, we still install this!** Even though we are using Ollama, Ollama provides an OpenAI-compatible API endpoint. This means we can often use the OpenAI Python client library to interact with our local Ollama server, which simplifies our code and leverages a familiar library structure.

* **Create/Update `requirements.txt`:**
    After installing, update your dependencies list:
    ```bash
    pip freeze > requirements.txt
    ```
    Commit this file to Git:
    ```bash
    git add requirements.txt
    git commit -m "Update project dependencies for Phase 2"
    git remote add origin https://github.com/RNstu08/RAG_chatbot.git
    # git push origin main # Or your default branch
    ```

**4. IDE/Editor Setup (VS Code):**

* **What:** Ensure VS Code is configured for your project and virtual environment.
* **Why:** Improves productivity with code completion, linting, debugging.
* **VS Code Configuration Tips (as covered before):**
    1.  **Select Python Interpreter:** Make sure VS Code is using the Python interpreter from your `./venv/Scripts/python.exe`. Use `Ctrl+Shift+P` -> `Python: Select Interpreter`.
    2.  **Recommended Extensions:** Python (Microsoft), Pylance (Microsoft).
    3.  **Terminal Integration:** Use VS Code's integrated terminal. It should pick up your activated virtual environment.

**5. Environment Variable Management (`.env`):**

* **What:** We will use a `.env` file for managing configuration variables.
* **Why:**
    * **Security (General):** Even if we don't have an OpenAI API key *for the LLM itself* with Ollama, `.env` is good practice for any future sensitive info or environment-specific settings (e.g., database paths, external service keys if we add them later).
    * **Configuration:** Allows different settings for development vs. production without code changes.
* **How:**
    1.  **Your `.env` file:** You created this in Phase 1. It's in the root of `rag_chatbot_coeo` and correctly in `.gitignore`.
    2.  **What to put in it (for now):**
        For Ollama, we don't strictly need an `OPENAI_API_KEY` in the traditional sense for accessing the LLM. However, the `openai` Python library might still expect an API key to be configured. Often, when pointing the `openai` client to a local, non-OpenAI endpoint like Ollama's, you can use a placeholder or non-empty string as the API key.
        Let's define where our Ollama server is running. Ollama's default is `http://localhost:11434`.
        Open your `.env` file and add:
        ```env
        OLLAMA_BASE_URL="http://localhost:11434/v1"
        # If the openai library strictly requires an API key string even for local Ollama:
        OLLAMA_API_KEY="ollama" # Or any non-empty string, Ollama doesn't check this value
        ```
        We will use `OLLAMA_BASE_URL` in our Python code to tell the OpenAI client where to send requests. The `OLLAMA_API_KEY` can be used if the client library requires an API key parameter to be set, even if the server doesn't validate it.

    3.  **Loading in Python (Example for `chatbot_service.py` later):**
        ```python
        import os
        from dotenv import load_dotenv

        load_dotenv() # Load variables from .env

        ollama_base_url = os.getenv("OLLAMA_BASE_URL")
        ollama_api_key = os.getenv("OLLAMA_API_KEY", "ollama") # Default to "ollama" if not set

        # When using the OpenAI client with Ollama:
        # from openai import OpenAI
        # client = OpenAI(
        # base_url=ollama_base_url,
        # api_key=ollama_api_key, # The key is often a dummy for Ollama
        # )
        ```

---

This completes Phase 2. Your development environment is now enhanced with Ollama for local LLM serving, a Python virtual environment, necessary libraries, and a plan for configuration.

**Key Takeaways from Phase 2 with Ollama:**
* Ollama is installed and you've pulled an initial model (e.g., `llama3:8b-instruct`).
* Your Python virtual environment is active and has the required libraries.
* The `openai` Python library will be configured to point to your local Ollama server.
* The `.env` file is set up for this configuration.

**Next, we'll move to Phase 3: Knowledge Base Preparation.** This is where we create the FAQ content that our RAG chatbot will use to answer questions.

Please ensure you have:
1.  Successfully installed Ollama and pulled at least one model (e.g., `llama3:8b-instruct`).
2.  Verified your Python virtual environment is active and libraries are installed.
3.  Updated `requirements.txt`.
4.  Updated your `.env` file with the `OLLAMA_BASE_URL`.

Let me know if you encountered any issues with these steps, or if you're ready to proceed to Phase 3!