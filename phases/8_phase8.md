
---

**Phase 8: Deployment to Azure (Simplified)**

**1. Understanding Azure Costs:**

* **Is Azure Paid?**
    * **Yes, generally.** Most Azure services operate on a **pay-as-you-go** model, meaning you pay for what you use (e.g., compute time, storage, data transfer).
    * **Azure Free Account:** When you sign up for Azure for the first time, you typically get an **Azure Free Account**. This usually includes:
        * A certain amount of **free credit** (e.g., $200, but check the current offer) to spend on any Azure services for the first 30 days.
        * **12 months of popular services for free** up to certain monthly limits (e.g., specific types of VMs, storage, databases).
        * **Always Free services:** A selection of services that have a free tier with specific usage limits that you can use indefinitely (e.g., Azure Functions has a free grant of executions, Azure App Service has a free tier for small apps).
* **Key for This Project:**
    * We'll try to use services that have an "Always Free" tier or fit within the initial free credits/12-month free services for learning purposes.
    * **Azure Container Registry (ACR):** Has a 'Basic' tier which is very low cost and sometimes might be covered by free tier offers for new accounts (e.g., a certain amount of storage for a limited time). The 'Basic' tier includes 10GB of storage, which is usually enough for several images.
    * **Azure App Service for Containers:** Has a **Free (F1) tier** for Linux. This tier has limitations (shared CPU, limited RAM/storage, no custom domains with SSL in some scenarios, CPU quotas per day), but it's excellent for deploying small test applications like ours for learning.
* **Important Note on Costs:** Always monitor your usage in the Azure portal and set up budget alerts if you're concerned about costs, especially if you venture beyond free tier limits or after any initial free credits expire. Delete resources you're no longer using.

**2. The "Simplified" Deployment Challenge: Ollama and ChromaDB**

This is the most crucial part to understand for a "simplified" deployment:

* **Our Current Setup:**
    * **Ollama LLM:** Running locally on your machine.
    * **ChromaDB Vector Store:** Data is stored locally on your machine (in `app/knowledge_base/vector_store/`).
    * **FastAPI Backend:** We Dockerized this. It expects to connect to Ollama and ChromaDB based on its current configuration (e.g., `OLLAMA_BASE_URL="http://host.docker.internal:11434/v1"` and local file paths for ChromaDB when running Docker locally with volume mounts).

* **The Problem with Deploying *Only* the FastAPI Container to Azure:**
    * If we deploy *only* our `rag-chatbot-api` Docker container to Azure App Service, it **will not be able to connect** to your local Ollama instance or your local ChromaDB files. Azure App Service runs in Azure's cloud, isolated from your local machine.
    * `host.docker.internal` only works for Docker Desktop connecting to the host it's running on; it doesn't work for an Azure service trying to reach your personal computer.
    * Local file paths for ChromaDB (`/app_code/app/knowledge_base/vector_store` inside the container if volume mounted from host) won't point to your data when the container runs in Azure without a similar data persistence strategy in Azure.

* **What "Simplified" Means for This Phase:**
    * We will focus on the **mechanics of deploying the Dockerized FastAPI backend to Azure App Service**. This means you'll learn how to get a Docker container running in the cloud.
    * **Acknowledgement:** The deployed API in Azure **will likely not fully function** as intended (i.e., generate RAG responses) because it won't be able to reach its Ollama LLM and ChromaDB data dependencies that are currently local.
    * The goal here is to learn the Azure deployment process for a container. Making the *entire RAG application* cloud-native is a more advanced step.

* **What Would a Fully Cloud-Native Solution Entail? (Beyond this simplified phase)**
    1.  **LLM in Azure:**
        * **Azure OpenAI Service:** Deploy models like GPT-3.5/4 (paid).
        * **VM with GPU + Ollama:** Set up an Azure Virtual Machine (likely with a GPU, which can be costly), install Ollama and your model there, and make it network accessible to your App Service.
        * **Azure Machine Learning:** Deploy models from the AML model catalog or custom models.
    2.  **Vector Database in Azure:**
        * **Azure AI Search:** Has built-in vector search capabilities (paid). You'd load your embeddings here.
        * **Managed Database with Vector Support:** E.g., Azure Cosmos DB for MongoDB with vector search.
        * **VM + ChromaDB:** Deploy ChromaDB on an Azure VM and manage it yourself.
    This involves more services, configuration, and potential costs.

For now, let's focus on getting the FastAPI container into Azure App Service.

**3. Deployment Steps (FastAPI Backend to Azure App Service):**

**Prerequisites:**
* An **Azure Account:** If you don't have one, sign up for a free account.
* **Azure CLI:** Install the Azure Command-Line Interface. ([Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
* **Docker Desktop:** Must be running and you should be logged into Docker.

**Step 1: Login to Azure CLI**
Open a terminal or PowerShell and run:
```bash
az login
```
This will open a browser window for you to authenticate.

**Step 2: Create an Azure Container Registry (ACR)**
ACR is a private Docker registry in Azure to store your container images.
* Choose a globally unique name for your registry (e.g., `yourinitialsragacr` - use lowercase letters and numbers only).
* Choose a resource group name (a logical container for Azure resources, e.g., `rag-chatbot-rg`).
* Choose a location (e.g., `eastus`, `westeurope`).
* SKU: 'Basic' is fine for this.

```bash
# Variables (customize these)
ACR_NAME="yourinitialsragacr" # MUST BE GLOBALLY UNIQUE, lowercase
RESOURCE_GROUP_NAME="rag-chatbot-rg"
LOCATION="eastus" # Choose a region near you

# Create Resource Group (if it doesn't exist)
az group create --name $RESOURCE_GROUP_NAME --location $LOCATION

# Create Azure Container Registry
az acr create --resource-group $RESOURCE_GROUP_NAME --name $ACR_NAME --sku Basic --admin-enabled true 
# --admin-enabled true is simpler for login initially, but service principals are better for CI/CD
```
*(For PowerShell, replace `$` with `$env:` for variables, e.g., `$env:ACR_NAME`)*

**Step 3: Log in to ACR with Docker**
```bash
az acr login --name $ACR_NAME
```
This configures your local Docker client to authenticate with your ACR.

**Step 4: Tag Your Local Docker Image for ACR**
Your local image is named `rag-chatbot-api:latest` (or similar). You need to tag it with your ACR login server name.
The login server name is typically `<acr_name>.azurecr.io`.
```bash
# Get the ACR login server (FQDN)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)

# Tag your local image
docker tag rag-chatbot-api:latest $ACR_LOGIN_SERVER/rag-chatbot-api:latest
docker tag rag-chatbot-api:latest $ACR_LOGIN_SERVER/rag-chatbot-api:v1 # Also good to have a versioned tag
```

**Step 5: Push the Image to ACR**
```bash
docker push $ACR_LOGIN_SERVER/rag-chatbot-api:latest
docker push $ACR_LOGIN_SERVER/rag-chatbot-api:v1
```
You can verify the image in the Azure portal under your Container Registry > Repositories.

**Step 6: Create an Azure App Service Plan**
This defines the underlying compute resources for your App Service. We'll aim for the Free tier.
* Choose a name for your App Service Plan (e.g., `rag-chatbot-plan`).
```bash
APP_SERVICE_PLAN_NAME="rag-chatbot-plan"

az appservice plan create --name $APP_SERVICE_PLAN_NAME \
                          --resource-group $RESOURCE_GROUP_NAME \
                          --location $LOCATION \
                          --is-linux \
                          --sku F1 # F1 is the Free tier for Linux
```

**Step 7: Create the Web App for Containers (Azure App Service)**
This will run your Docker container.
* Choose a globally unique name for your web app (e.g., `yourinitials-rag-app` - this will be part of its URL: `<app_name>.azurewebsites.net`).
```bash
WEB_APP_NAME="yourinitials-rag-app" # MUST BE GLOBALLY UNIQUE

az webapp create --resource-group $RESOURCE_GROUP_NAME \
                 --plan $APP_SERVICE_PLAN_NAME \
                 --name $WEB_APP_NAME \
                 --deployment-container-image-name $ACR_LOGIN_SERVER/rag-chatbot-api:v1 # Use your versioned tag
```

**Step 8: Configure Environment Variables for the Web App**
This is where you'd normally tell the App Service how to connect to dependencies. Since our dependencies (Ollama, ChromaDB) are local, the deployed app won't reach them.
However, your `chatbot_service.py` expects `OLLAMA_BASE_URL`, etc. We can set them to dummy values or acknowledge they won't work.
For the `CHROMA_DB_PATH`, the container in Azure won't have the volume mounted from your host. If the `vector_store` was *not* copied into the Docker image (because it was in `.dockerignore`), ChromaDB initialization in `chatbot_service.py` will likely fail or create an empty store inside the ephemeral container storage unless the image itself contained a pre-built store.

Let's set the Ollama URL to something to satisfy the code, even if it's not reachable from Azure:
```bash
az webapp config appsettings set --resource-group $RESOURCE_GROUP_NAME \
                                 --name $WEB_APP_NAME \
                                 --settings OLLAMA_BASE_URL="http://not-reachable-from-azure:11434/v1" \
                                            OLLAMA_API_KEY="ollama" \
                                            OLLAMA_MODEL_NAME="koesn/llama3-8b-instruct:latest" \
                                            WEBSITES_PORT=8000 # Tell App Service which port your app listens on
```
`WEBSITES_PORT=8000` is important to tell App Service that your container is listening on port 8000.

**Step 9: (Enable Continuous Deployment - Optional)**
You can configure the Web App to automatically redeploy when you push a new image with the same tag (e.g., `latest`) to ACR. This is often called the "CD webhook."
```bash
az webapp deployment container config --enable-cd true --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP_NAME
```

**4. Accessing the Deployed API:**

* Your app will be available at `http://<WEB_APP_NAME>.azurewebsites.net`.
* You can check the logs in the Azure portal (under your Web App > Monitoring > Log stream) to see if it started correctly or if there are errors (e.g., issues initializing `ChatbotService` due to unreachable Ollama or ChromaDB issues).
* If it starts, you could try accessing `http://<WEB_APP_NAME>.azurewebsites.net/docs`.
* **Expected Outcome for this Simplified Deployment:** The API might start, but calls to `/chat/` will likely fail or return error messages from `ChatbotService` because it can't connect to Ollama or properly access the ChromaDB vector store.

**5. Clean-up (Important to Avoid Costs!):**

When you're done experimenting, delete the resources to prevent ongoing charges (especially if you created services beyond the absolute free limits or your free trial/credits expire).
The easiest way is to delete the entire resource group:
```bash
az group delete --name $RESOURCE_GROUP_NAME --yes --no-wait
```
* `--yes`: Confirms deletion without prompting.
* `--no-wait`: Returns immediately without waiting for the deletion to complete.

---

This phase gives you a taste of deploying a Dockerized application to Azure. You've learned to:
* Use Azure Container Registry to store your Docker images.
* Use Azure App Service to run containers.
* Configure basic settings for your deployed app.

**Key Challenges Highlighted:**
* **Dependency Management in the Cloud:** The biggest takeaway is that local dependencies (like a desktop Ollama instance or local file-based databases) are not directly accessible by cloud-hosted applications. A full cloud deployment requires migrating or providing cloud-native alternatives for these dependencies.

This is a "simplified" deployment focusing on the mechanics. A production deployment would require more planning around networking, security, data management, and cost optimization for all components.