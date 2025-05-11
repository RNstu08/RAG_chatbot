
In this phase, we'll focus on packaging our FastAPI backend application using Docker. This is a foundational step for creating portable, reproducible, and scalable applications, which are core tenets of MLOps (Machine Learning Operations).

---

**Phase 7: Containerization with Docker & Basic MLOps Introduction**

**1. Introduction to Containerization and Docker:**

* **What is Containerization?**
    * Containerization is a lightweight form of virtualization that allows you to package an application with all its dependencies (libraries, system tools, code, runtime) into a single, isolated unit called a "container."
    * Unlike traditional virtual machines (VMs) that virtualize an entire operating system, containers virtualize the operating system at the user-space level, sharing the host system's kernel. This makes them much more lightweight, faster to start, and more efficient in terms of resource usage.
* **What is Docker?**
    * Docker is the leading open-source platform for developing, shipping, and running applications in containers. It provides tools to build container images (blueprints for containers) and run those images as containers.
* **Why use Docker for our project?**
    * **Consistency ("It works on my machine"):** Docker ensures that your application runs the same way regardless of where it's deployed (your local machine, a teammate's machine, staging, or production servers) because the container includes all its dependencies.
    * **Portability:** Docker containers can run on any system that has Docker installed (Windows, macOS, Linux, cloud platforms).
    * **Dependency Management:** Explicitly defines and isolates all project dependencies, avoiding conflicts with other projects or system-wide packages.
    * **Scalability:** Containerized applications are easier to scale up or down.
    * **MLOps Foundation:** Docker is a cornerstone of MLOps practices, enabling reproducible training environments, consistent model serving deployments, and integration into CI/CD pipelines.
* **Key Concepts:**
    * **`Dockerfile`:** A text file that contains instructions for Docker to build an image. It's like a recipe.
    * **Image:** A read-only template used to create containers. It's built from a `Dockerfile`. Think of it as a blueprint or a snapshot.
    * **Container:** A runnable instance of an image. You can run multiple containers from the same image.
    * **Docker Hub / Container Registry:** A place to store and share Docker images (like Docker Hub, Azure Container Registry, Google Container Registry, AWS ECR).

**2. Docker Installation (Brief Reminder):**

* To work with Docker, you'll need Docker Desktop installed on your Windows machine. If you haven't already, download it from the official Docker website and install it. Ensure it's running when you're performing Docker operations.

**3. Writing a Dockerfile for the FastAPI Backend:**

* **What:** We'll create a `Dockerfile` in the root of our project (`rag_chatbot_coeo/Dockerfile`). This file will contain the instructions to package our FastAPI application (the `app` directory).
* **Why:** The `Dockerfile` defines the environment and steps to build a reusable image of our backend service.
* **`Dockerfile` Content:**

Create a new file named `Dockerfile` (no extension) in your project root directory (`rag_chatbot_coeo/Dockerfile`) with the following content:

```dockerfile
# Dockerfile for the FastAPI backend

# 1. Base Image: Start with an official Python base image.
# Using a slim version reduces the image size. Specify a Python version.
FROM python:3.9-slim

# 2. Set Environment Variables (Optional but good practice)
ENV PYTHONUNBUFFERED=1    # Ensures Python output (e.g., print statements) is sent straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1 # Prevents Python from writing .pyc files to disc (not needed in container)

# 3. Set Working Directory: Define the working directory inside the container.
WORKDIR /app_code 
# All subsequent commands (COPY, RUN, CMD) will be relative to this directory.

# 4. Copy Requirements First & Install Dependencies:
# This step is crucial for Docker layer caching. If requirements.txt doesn't change,
# Docker can reuse this layer, speeding up subsequent builds.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code: Copy the 'app' directory from your project
# (containing main.py, chatbot_service.py, etc.) into the WORKDIR/app.
# We'll map it to an 'app' subdirectory inside /app_code for clarity.
COPY ./app ./app

# 6. Expose Port: Inform Docker that the container listens on port 8000 at runtime.
# This doesn't actually publish the port; that's done with `docker run -p`.
EXPOSE 8000

# 7. Define the Command to Run the Application:
# This is the command that will be executed when the container starts.
# We run uvicorn, making it listen on all available network interfaces (0.0.0.0)
# inside the container, on port 8000.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

* **Create a `.dockerignore` file:**
    Similar to `.gitignore`, a `.dockerignore` file tells Docker to ignore certain files and directories when building the image. This can prevent unwanted files from being copied into the image, reduce image size, and speed up builds.
    Create a `.dockerignore` file in your project root (`rag_chatbot_coeo/.dockerignore`) with content like:
    ```dockerignore
    __pycache__
    *.pyc
    *.pyo
    *.pyd
    .Python
    env
    venv
    .env
    .git
    .gitignore
    .vscode
    .pytest_cache
    *.log
    # Add any other files/folders you don't want in your image
    app/knowledge_base/vector_store/* # Usually, you build this once, or mount it as a volume.
                                     # For a stateless API server, the vector store might be
                                     # accessed differently or rebuilt. For simplicity now,
                                     # we might copy it, but long term it's better managed outside.
                                     # Let's exclude it for now to keep the image lean.
                                     # The build_knowledge_base.py script can be run separately
                                     # or data could be mounted.
    scripts/
    streamlit_app.py
    ```
    *The treatment of `vector_store` is important. For a production app, you wouldn't typically bake a large, frequently changing database into your image. You'd use a volume mount or connect to an external/managed vector database. For now, if your `build_knowledge_base.py` script creates it inside `app/knowledge_base/vector_store`, and if you want the container to *use* it, you would *not* ignore it and *ensure* it's copied. However, for a clean API image, often data stores are kept separate. Let's assume for this phase the ChromaDB will be accessed from the host if running `build_knowledge_base.py` locally, and the Dockerized API needs to connect to it (or an equivalent). This brings us to the Ollama connection challenge.*

**4. Building the Docker Image:**

* **What:** Use the `docker build` command to create an image from your `Dockerfile`.
* **Command (run from the root of your project, `rag_chatbot_coeo/`):**
    ```bash
    docker build -t rag-chatbot-api:latest .
    ```
    * `docker build`: The command to build an image.
    * `-t rag-chatbot-api:latest`: Tags the image with a name (`rag-chatbot-api`) and a tag (`latest`). This makes it easier to refer to the image later. You can use other tags, like version numbers (e.g., `rag-chatbot-api:0.1.0`).
    * `.`: Specifies that the build context (the set of files Docker can access during the build) is the current directory.

    This command will execute the steps in your `Dockerfile`. You'll see output for each step.

**5. Running the Docker Container Locally:**

* **What:** Run a container from the image you just built.
* **Why:** To test if your application works correctly inside the containerized environment.
* **Command (from any terminal where Docker commands work):**
    ```bash
    docker run --rm -p 8001:8000 --name my-rag-api rag-chatbot-api:latest
    ```
    * `docker run`: The command to run a container.
    * `--rm`: Automatically removes the container when it exits (useful for testing).
    * `-p 8001:8000`: Publishes port 8000 from the container to port 8001 on your host machine. So, you'll access the API via `http://localhost:8001` on your host. The first number is the host port, the second is the container port (which we `EXPOSE`d as 8000 and run `uvicorn` on).
    * `--name my-rag-api`: Gives your running container a memorable name.
    * `rag-chatbot-api:latest`: The name and tag of the image to run.

* **CRUCIAL: Connecting to Host-Running Ollama from Docker:**
    Your FastAPI app, now running inside a Docker container, needs to connect to the Ollama server, which is likely running directly on your Windows host machine.
    Inside the Docker container, `localhost` or `127.0.0.1` refers to the container itself, *not* your host machine.
    * **Solution for Docker Desktop (Windows/Mac):**
        Docker Desktop provides a special DNS name `host.docker.internal` that resolves to the internal IP address of your host machine.
        1.  **Modify your `.env` file (the one *outside* the container, that your `chatbot_service.py` reads when building the image, OR pass it as an environment variable during `docker run`):**
            Change:
            `OLLAMA_BASE_URL="http://localhost:11434/v1"`
            To:
            `OLLAMA_BASE_URL="http://host.docker.internal:11434/v1"`
        2.  **Rebuild your Docker image** if you changed `.env` and it's copied into the image (our current Dockerfile doesn't copy `.env`, which is good practice for secrets. `chatbot_service.py` loads it from the environment where Python runs).
        3.  **Alternative: Pass as Environment Variable during `docker run`:**
            This is often a better approach for configuration that changes between environments.
            ```bash
            docker run --rm -p 8001:8000 \
                       -e OLLAMA_BASE_URL="http://host.docker.internal:11434/v1" \
                       -e OLLAMA_API_KEY="ollama" \
                       --name my-rag-api \
                       rag-chatbot-api:latest
            ```
            If you use this method, your `chatbot_service.py` will pick up `OLLAMA_BASE_URL` from the container's environment.

    * **Accessing ChromaDB:**
        Similarly, ChromaDB is running on your host (data in `app/knowledge_base/vector_store/` which is on your host filesystem). The container needs access.
        * **If the vector store was copied into the image:** The `CHROMA_DB_PATH` in `chatbot_service.py` would resolve correctly *inside* the container (e.g., `/app_code/app/knowledge_base/vector_store`). This is simpler for a quick start but makes the image larger and less flexible if the data changes. *Our `.dockerignore` currently excludes it, which is generally better for image hygiene.*
        * **Using Docker Volumes (Recommended for data):** Mount the host directory containing ChromaDB data into the container.
            ```bash
            # Assuming your PWD is rag_chatbot_coeo
            docker run --rm -p 8001:8000 \
                       -e OLLAMA_BASE_URL="http://host.docker.internal:11434/v1" \
                       -e OLLAMA_API_KEY="ollama" \
                       -v ./app/knowledge_base/vector_store:/app_code/app/knowledge_base/vector_store \
                       --name my-rag-api \
                       rag-chatbot-api:latest
            ```
            This mounts your local `./app/knowledge_base/vector_store` directory into the expected path inside the container. The `chatbot_service.py` inside the container can then read/write to it as if it were a local path.

    After running the container with the correct Ollama URL and volume mount for ChromaDB, test your API at `http://localhost:8001/docs` (or the host port you chose).

**6. Basic MLOps Concepts Introduction:**

* **How Docker fits into MLOps:**
    * **Reproducible Environments:** Docker ensures that the environment for running your model serving API (and potentially model training or data processing jobs) is identical everywhere. This eliminates "works on my machine" problems.
    * **Deployment Artifacts:** Docker images become the standard unit of deployment. You build an image once and can deploy that exact same image to development, staging, and production environments.
    * **Version Control:** Docker images can be versioned (using tags) and stored in a container registry, just like you version your code with Git.
    * **Scalability & Orchestration:** Container orchestrators like Kubernetes are designed to manage and scale containerized applications, including ML model serving endpoints.
* **CI/CD (Continuous Integration / Continuous Deployment) for ML:**
    * **What:** CI/CD is a set of practices that automate the building, testing, and deployment of software (including ML models and applications).
    * **How Docker is used:**
        1.  **Code Change:** A developer pushes code changes to a Git repository.
        2.  **CI Trigger:** A CI server (e.g., GitHub Actions, Jenkins, Azure Pipelines) detects the change.
        3.  **Build & Test:** The CI server checks out the code, runs automated tests. If tests pass, it builds a new Docker image using the `Dockerfile`.
        4.  **Push to Registry:** The newly built and tagged Docker image is pushed to a container registry (e.g., Docker Hub, Azure Container Registry).
        5.  **CD Trigger (Optional):** A CD system can then automatically (or manually) deploy this new image version to a server or Kubernetes cluster.
    * This pipeline ensures that every change is automatically tested and a deployable artifact (the Docker image) is produced, making deployments faster and more reliable. We won't implement a full CI/CD pipeline in this project, but understanding where Docker fits in is key.

---

This is a dense but critical phase! Containerizing your application is a major step towards professional software development and MLOps practices.

**Key Takeaways:**
* Docker provides consistent and portable application environments.
* A `Dockerfile` defines how to build your application image.
* `docker build` creates the image, `docker run` starts a container from it.
* Connecting containerized applications to host services (like Ollama) or host data (like ChromaDB via volumes) requires specific configurations (e.g., `host.docker.internal`, volume mounts).
* Docker is a foundational technology for MLOps and CI/CD pipelines.

Take your time to:
1.  Install Docker Desktop if you haven't.
2.  Create the `Dockerfile` and `.dockerignore` file.
3.  Try building the image.
4.  Experiment with `docker run`, especially focusing on how to correctly set the `OLLAMA_BASE_URL` environment variable for the container and mount the ChromaDB data volume.

This can be tricky, so don't hesitate to ask questions if you encounter issues. Let me know how it goes!