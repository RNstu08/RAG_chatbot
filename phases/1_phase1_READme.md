
**Let's begin with Phase 1: Project Foundation & Planning.**

---

**Phase 1: Project Foundation & Planning**

This phase is about setting a clear direction and understanding the "what" and "why" before we dive into coding.

**1. Project Goal & Scope Definition:**

* **What:**
    * **Goal:** To develop a Proof-of-Concept (PoC) AI chatbot that can answer common customer queries related to debt collection in an empathetic, accurate, and helpful manner. It will use a Retrieval Augmented Generation (RAG) architecture.
    * **MVP (Minimum Viable Product) Scope:**
        1.  The chatbot will answer questions based *solely* on a predefined knowledge base of FAQs (which we will create).
        2.  It will handle single-turn conversations (user asks a question, chatbot answers). No memory of past interactions in this MVP.
        3.  Interactions will be text-based.
        4.  Focus on empathetic response generation through prompt engineering.
        5.  Provide a REST API endpoint for the chatbot.
* **Why:**
    * This directly addresses AI platform that are customer-centric and leverage Generative AI.
    * The RAG approach is specifically mentioned as a desired skill (making LLMs more factual).
    * Building this provides hands-on experience with key technologies uses/values and using Ollama demonstrates adaptability with different LLM hosting solutions.
* **Key Concepts:**
    * **MVP (Minimum Viable Product):** The simplest version of a product that can be released to get user feedback. It helps in focusing on core functionality first.
    * **User Stories (Example):**
        * "As a customer, I want to ask about my payment options so that I can understand how to resolve my debt."
        * "As a customer, I want to understand why I have been contacted so that I can verify the legitimacy of the communication."
        * "As a Coeo agent (or for internal quality check), I want the chatbot to provide empathetic responses so that it aligns with our customer-centric values."

**2. Technology Stack Selection:**

* **What & Why:**
    * **Programming Language: Python**
        * *Why:* Industry standard for AI/ML; rich ecosystem of libraries (Scikit-learn, PyTorch, TensorFlow); Coeo explicitly requires strong Python skills.
    * **LLM: OpenAI API (e.g., gpt-3.5-turbo, gpt-4o)**
        * *Why:* High-quality models, easy to integrate via API for a PoC. Good for focusing on RAG logic rather than model hosting initially. 
    * **LLM Engine: Ollama (running open-source models like Llama 3, Mistral, Phi-3, etc., locally)**
        * *Why*:
            - Cost-effective: No API call costs for generation.
            Privacy: Data (prompts and generated text) stays on your local machine.
            - Control & Flexibility: Allows experimentation with various open-source models. Many models are highly capable.
            Offline Capability: Can work without an internet connection once models are downloaded.
            - OpenAI-Compatible API: Ollama provides a local server endpoint that mimics the OpenAI API structure. This means we can often use the openai Python library with minimal changes, simply by redirecting it to our local Ollama URL. This is a huge advantage for development and aligns with the skills Coeo might look for (interfacing with RESTful AI services).
        * *Alternatives*: Directly using Hugging Face transformers library for local models (more complex setup), other local LLM runners (like LM Studio), or cloud-based APIs (OpenAI, Google Gemini API, Azure OpenAI – these would involve costs or free tier limitations).
    * **Embedding Model: Sentence-Transformers (e.g., `all-MiniLM-L6-v2` or `nomic-embed-text` if run via Ollama)**
        * *Why:* Good quality, runs locally, easy to use for creating document embeddings for RAG. `sentence-transformers` is a widely used Python library. Some embedding models can also be served via Ollama, which offers another integration path. We'll likely start with `sentence-transformers` directly in Python for simplicity.
        * *Alternatives:* OpenAI Embeddings API (ada-002), other open-source embedding models.
    * **Vector Database (Local): FAISS (Facebook AI Similarity Search) or ChromaDB**
        * *Why:*
            * `FAISS`: Very efficient for similarity search, runs in memory. Good for smaller datasets and local development.
            * `ChromaDB`: Simpler API, designed for AI applications, good for local development, persists to disk easily. Let's lean towards **ChromaDB** for its ease of use for this project.
        * *Why (Cloud/Production):* For stack, **Azure AI Search** (formerly Azure Cognitive Search) would be the go-to for its vector search capabilities and integration within the Azure ecosystem.
        * *Alternatives:* Pinecone, Weaviate, Milvus (more complex setup).
    * **API Framework: FastAPI**
        * *Why:* Modern, high-performance Python framework for building APIs. Automatic data validation (with Pydantic) and API documentation (Swagger UI).
        * *Alternatives:* Flask (simpler for very small APIs, but FastAPI offers more out-of-the-box for robust services), Django (full-stack, overkill for just an API).
    * **Containerization: Docker**
        * *Why:* Package the application and its dependencies for consistent deployment. *Note*: Dockerizing an application that relies on a system-installed Ollama needs careful consideration for deployment, but for local development and the API part, it's fine.
    * **Cloud Platform (Eventual Deployment): Microsoft Azure**
        * *Why:* explicitly states Azure as their cloud platform (Azure AI/ML, Azure Cognitive Services, Azure Bot Service, etc.). We will design with Azure in mind for later phases.

**3. Ethical Considerations & Data (Mock Data):**

* **What:**
    * **Empathy:** Debt collection is sensitive. Responses must be non-judgmental, understanding, and helpful, avoiding aggressive or accusatory language. This will be primarily enforced via prompt engineering and the tone of our FAQ content.
    * **Accuracy:** The chatbot must provide information based *only* on the provided knowledge base to avoid hallucinations or giving incorrect advice, which could have serious consequences.
    * **Privacy & Security:** No real customer data will be used. We will create **mock FAQs** that are generic and do not contain personally identifiable information (PII). In a real system, PII handling, data encryption, and access controls would be paramount.
    * **Bias:** AI models can inherit biases from their training data. While we are using pre-trained models, the content of our knowledge base should be carefully crafted to be fair and unbiased.
    * **Transparency:** Ideally, the chatbot should state that it's an AI assistant.
* **Why:**
    * Building trust is crucial, especially in finance and debt collection. "customer centricity" demands high ethical standards. Neglecting these can lead to reputational damage, legal issues, and harm to customers.

**4. Project Structure Setup:**

* **What:** Let's create a root directory for our project and a basic structure.
    ```
    rag_chatbot/
    ├── app/                  # Core application logic (API, chatbot service)
    │   ├── __init__.py
    │   ├── main.py           # FastAPI app definition
    │   ├── chatbot_service.py # RAG logic
    │   └── knowledge_base/   # Store FAQ documents and vector DB
    │       ├── faqs.json     # Example: our FAQ data
    │       └── vector_store/ # Directory for ChromaDB persistence
    ├── tests/                # For automated tests
    ├── scripts/              # Utility scripts (e.g., for embedding generation)
    ├── .env                  # For environment variables (API keys) - DO NOT COMMIT
    ├── .gitignore            # Specifies intentionally untracked files that Git should ignore
    ├── Dockerfile            # For containerizing the application
    └── README.md             # Project documentation
    ```
* **Why:**
    * **Modularity:** Separates concerns (API, chatbot logic, data).
    * **Maintainability:** Easier to understand, update, and debug.
    * **Scalability:** Provides a foundation that can grow.
    * **Collaboration:** Standard structures help team members navigate the codebase.
* **Commands (run in your terminal/shell):**
    ```bash
    mkdir rag_chatbot
    cd rag_chatbot
    mkdir -p app/knowledge_base/vector_store app/models tests scripts
    touch app/__init__.py app/main.py app/chatbot_service.py app/models/__init__.py app/knowledge_base/faqs.json
    touch tests/__init__.py scripts/__init__.py
    touch .env .gitignore Dockerfile README.md
    ```
    *(Note: `mkdir -p` creates parent directories if they don't exist. `touch` creates empty files.)*

If above did nto work, PowerShell has different commands for creating directories and files.

Here's a breakdown of the issues and how to fix them:

**Error 1: `mkdir : A positional parameter cannot be found that accepts argument 'vector_store'.`**

* **Cause:** In PowerShell, `mkdir` (or its alias `md`) creates directories one by one or a nested structure with a single path. The Bash command `mkdir -p app/knowledge_base/vector_store app/models tests scripts` tries to create multiple separate directory trees in one go and uses the `-p` flag (which tells `mkdir` to create parent directories as needed, a behavior that's default for a single path in PowerShell's `mkdir` but doesn't work the same way for multiple distinct paths as you've listed them). Additionally, you've concatenated `scriptsmkdir -p` which is not a valid command.

* **PowerShell Solution:** You need to create these directories either one by one or by providing separate paths to the `New-Item` cmdlet.

**Error 2 & 3 & 4: `touch : The term 'touch' is not recognized as the name of a cmdlet, function, script file, or operable program.`**

* **Cause:** PowerShell does not have a direct equivalent of the `touch` command (which is used in Bash to create empty files or update timestamps).

* **PowerShell Solution:** You can use `New-Item` to create empty files.

**PowerShell Commands:**

```powershell
# Create the main directories
New-Item -ItemType Directory -Path "app"
New-Item -ItemType Directory -Path "app\knowledge_base"
New-Item -ItemType Directory -Path "app\knowledge_base\vector_store"
New-Item -ItemType Directory -Path "app\models"
New-Item -ItemType Directory -Path "tests"
New-Item -ItemType Directory -Path "scripts"

# Create the empty files within the app directory
New-Item -ItemType File -Path "app\__init__.py"
New-Item -ItemType File -Path "app\main.py"
New-Item -ItemType File -Path "app\chatbot_service.py"
New-Item -ItemType File -Path "app\models\__init__.py"
New-Item -ItemType File -Path "app\knowledge_base\faqs.json"

# Create the empty files within the tests and scripts directories
New-Item -ItemType File -Path "tests\__init__.py"
New-Item -ItemType File -Path "scripts\__init__.py"

# Create the empty files in the root project directory
New-Item -ItemType File -Path ".env"
New-Item -ItemType File -Path ".gitignore"
New-Item -ItemType File -Path "Dockerfile"
New-Item -ItemType File -Path "README.md"
```

**Explanation of PowerShell Cmdlets Used:**

* `New-Item`: This is a versatile cmdlet used to create new items in PowerShell.
    * `-ItemType Directory`: Specifies that you want to create a directory.
    * `-ItemType File`: Specifies that you want to create a file.
    * `-Path`: Specifies the path (including the name) of the item to be created.

By running these PowerShell commands, we will successfully create the desired project structure.

**5. Version Control with Git:**

* **What:** Initialize a Git repository to track our project's changes.
* **Why:**
    * **Change Tracking:** See history, revert to previous versions.
    * **Branching:** Work on new features in isolation without affecting the main codebase.
    * **Collaboration:** Essential for teams (though good practice even for solo projects).
    * **Backup:** When pushed to a remote repository (like GitHub, GitLab, Azure Repos).
* **Commands (run in the `rag_chatbot_coeo` directory):**
    ```bash
    git init
    ```
    Now, let's create a `.gitignore` file. This tells Git which files or directories to ignore (e.g., virtual environments, `.env` files, Python bytecode).
    Open `.gitignore` and add the following:
    ```gitignore
    # Byte-compiled / optimized / DLL files
    __pycache__/
    *.py[cod]
    *$py.class

    # C extensions
    *.so

    # Distribution / packaging
    .Python
    build/
    develop-eggs/
    dist/
    downloads/
    eggs/
    .eggs/
    lib/
    lib64/
    parts/
    sdist/
    var/
    wheels/
    pip-wheel-metadata/
    share/python-wheels/
    *.egg-info/
    .installed.cfg
    *.egg
    MANIFEST

    # PyInstaller
    #  Usually these files are written by a script, but as they are binary files,
    #  we ignore them.
    *.spec

    # Installer logs
    pip-log.txt
    pip-delete-this-directory.txt

    # Unit test / coverage reports
    htmlcov/
    .tox/
    .nox/
    .coverage
    .coverage.*
    .cache
    nosetests.xml
    coverage.xml
    *.cover
    *.log
    .hypothesis/
    .pytest_cache/

    # Translations
    *.mo
    *.pot

    # Django stuff:
    *.log
    local_settings.py
    db.sqlite3
    db.sqlite3-journal

    # Flask stuff:
    instance/
    .webassets-cache

    # Scrapy stuff:
    .scrapy

    # Sphinx documentation
    docs/_build/

    # PyBuilder
    target/

    # Jupyter Notebook
    .ipynb_checkpoints

    # IPython
    profile_default/
    ipython_config.py

    # pyenv
    #   For a library or package, you might want to ignore these files since the code is
    #   intended to run in multiple environments; otherwise, check them in:
    # .python-version

    # Celery stuff
    celerybeat-schedule
    celerybeat.pid

    # SageMath obscure files
    *.sage.py

    # Environments
    .env
    .venv
    env/
    venv/
    ENV/
    env.bak/
    venv.bak/

    # Spyder project settings
    .spyderproject
    .spyproject

    # Rope project settings
    .ropeproject

    # PyCharm settings
    .idea/

    # VSCode settings
    .vscode/

    # Vector store data (example for Chroma, adjust if using others locally)
    app/knowledge_base/vector_store/chroma.sqlite3 # or whatever Chroma uses
    app/knowledge_base/vector_store/*.parquet # if Chroma persists with parquet files in that dir

    # MyPy cache
    .mypy_cache/

    # pytest cache
    .pytest_cache/
    ```
    Now, let's make our first commit:
    ```bash
    git add .
    git commit -m "Initial project structure and .gitignore setup"
    ```
    *(It's good practice to also create a repository on a platform like GitHub or Azure Repos and push your code there regularly.)*

**6. Success Metrics (Initial):**

* **What:** For our MVP, success means:
    1.  The chatbot correctly retrieves relevant information from the FAQ knowledge base for a given query.
    2.  The chatbot uses the retrieved information to generate a coherent and contextually appropriate answer using the selected model running in Ollama.
    3.  The tone of the chatbot's response is generally empathetic and helpful (as guided by the system prompt).
    4.  The API endpoint successfully receives requests and returns responses.
    5.  The system does *not* answer questions for which it has no relevant information in its knowledge base (or clearly states it cannot answer).
* **Why:** - These metrics will help us evaluate if the core RAG functionality is working and if we are meeting the basic empathetic requirements. More sophisticated evaluation (e.g., RAGAS framework, human evaluation panels) would be for later stages.
- The choice of model within Ollama might affect the quality and nuance of responses, so iteration on model selection and prompting will be part of the process
---
---
