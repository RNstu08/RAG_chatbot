# rag_chatbot_coeo/app/chatbot_service.py

import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI # Yes, we use the OpenAI client for Ollama's compatible API

# --- Configuration Loading ---
load_dotenv() # Load variables from .env file in the project root

# Embedding model configuration (must match the one used in build_knowledge_base.py)
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# ChromaDB configuration
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) # This should be 'app', so one more dirname for project root
#PROJECT_ROOT_DIR = os.path.dirname(PROJECT_ROOT) # This should be rag_chatbot_coeo
CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, 'app', 'knowledge_base', 'vector_store')
COLLECTION_NAME = "faq_collection"

# Ollama/LLM configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
# The API key can be a dummy string for Ollama, but the client might expect something.
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama") 
# Specify the Ollama model you are using (the one you pulled)
# IMPORTANT: Replace this with the exact name from `ollama list` if different
OLLAMA_MODEL_NAME = "koesn/llama3-8b-instruct:latest" 

class ChatbotService:
    def __init__(self):
        print("Initializing ChatbotService...")
        try:
            # 1. Initialize SentenceTransformer model for embedding queries
            print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print("Embedding model loaded.")

            # 2. Initialize ChromaDB client and get the collection
            print(f"Connecting to ChromaDB at: {CHROMA_DB_PATH}...")
            self.chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
            print(f"Getting collection: {COLLECTION_NAME}...")
            self.collection = self.chroma_client.get_collection(name=COLLECTION_NAME)
            print(f"Connected to ChromaDB collection '{COLLECTION_NAME}' with {self.collection.count()} items.")

            # 3. Initialize OpenAI client to connect to Ollama
            print(f"Initializing OpenAI client for Ollama at: {OLLAMA_BASE_URL} with model: {OLLAMA_MODEL_NAME}...")
            self.llm_client = OpenAI(
                base_url=OLLAMA_BASE_URL,
                api_key=OLLAMA_API_KEY, # Required by the client, but Ollama doesn't check the value
            )
            print("OpenAI client for Ollama initialized.")
            print("ChatbotService initialized successfully.")

        except Exception as e:
            print(f"Error during ChatbotService initialization: {e}")
            # Potentially re-raise or handle more gracefully depending on application structure
            raise

    def _embed_query(self, query: str):
        """Embeds the user query using the SentenceTransformer model."""
        print(f"Embedding query: '{query}'")
        query_embedding = self.embedding_model.encode(query)
        return query_embedding

    def _retrieve_context(self, query_embedding, n_results=3):
        """Retrieves relevant context from ChromaDB based on query embedding."""
        print(f"Retrieving context from ChromaDB (top {n_results} results)...")
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()], # ChromaDB expects a list of embeddings
                n_results=n_results,
                include=['documents', 'metadatas', 'distances'] # Request documents, metadatas, and distances
            )
            # results is a dictionary-like object. 'documents', 'metadatas', 'distances' are lists of lists.
            # Since we query with one embedding, we take the first element of these lists.
            retrieved_docs = results.get('documents', [[]])[0]
            retrieved_metadatas = results.get('metadatas', [[]])[0]
            retrieved_distances = results.get('distances', [[]])[0]
            
            print(f"Retrieved {len(retrieved_docs)} documents.")
            # for i, doc in enumerate(retrieved_docs):
            #     print(f"  Doc {i+1} (Distance: {retrieved_distances[i]:.4f}): {doc[:100]}...") # Print snippet
            return retrieved_docs, retrieved_metadatas, retrieved_distances
        except Exception as e:
            print(f"Error retrieving context from ChromaDB: {e}")
            return [], [], []

    def _construct_prompt(self, query: str, context_documents: list):
        """Constructs the prompt for the LLM, including retrieved context."""
        print("Constructing prompt for LLM...")
        if not context_documents:
            # Edge Case: No relevant context found
            # You might have a specific way to handle this, e.g., a different prompt
            # or a direct "I don't know" response. For now, we'll let the LLM try.
            print("Warning: No relevant context documents found for the query.")
            context_str = "No specific information found in the knowledge base for this query."
        else:
            context_str = "\n\n".join(context_documents)

        # Prompt Engineering: This is crucial for guiding the LLM.
        # We instruct it to be empathetic, use only the provided context, and answer the user's query.
        prompt = f"""You are an empathetic and helpful AI assistant. Your primary goal is to assist users with their questions based *only* on the information provided in the "Knowledge Base Context" below.
If the context does not contain the answer to the question, clearly state that you don't have enough information from the knowledge base. Do not make up information or answer from your general knowledge.
Be polite, understanding, and aim to provide clear and concise answers.

Knowledge Base Context:
---
{context_str}
---

User's Question: {query}

Helpful and Empathetic Answer (based *only* on the Knowledge Base Context):
"""
        # print(f"Constructed Prompt:\n{prompt}") # For debugging
        return prompt

    def _generate_llm_response(self, prompt: str):
        """Generates a response from the Ollama LLM using the constructed prompt."""
        print(f"Sending prompt to Ollama model: {OLLAMA_MODEL_NAME}...")
        try:
            response = self.llm_client.chat.completions.create(
                model=OLLAMA_MODEL_NAME, # Specify the model to use in Ollama
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant designed to answer questions based on provided context."}, # System message (optional but good practice)
                    {"role": "user", "content": prompt} # The actual detailed prompt
                ],
                temperature=0.3, # Lower temperature for more factual, less creative responses
                # max_tokens=500 # Optional: limit response length
            )
            generated_text = response.choices[0].message.content.strip()
            print("LLM response received.")
            # print(f"Generated Text: {generated_text}") # For debugging
            return generated_text
        except Exception as e:
            print(f"Error communicating with Ollama LLM: {e}")
            return "I'm sorry, but I encountered an issue while trying to generate a response. Please try again later."

    def get_rag_response(self, query: str) -> str:
        """
        Main method to get a RAG response for a user query.
        Orchestrates embedding, retrieval, prompt construction, and LLM generation.
        """
        print(f"\nProcessing RAG request for query: '{query}'")
        # 1. Embed the user query
        query_embedding = self._embed_query(query)

        # 2. Retrieve relevant context from ChromaDB
        #    We ask for the top 3 results; you can adjust this.
        context_documents, context_metadatas, context_distances = self._retrieve_context(query_embedding, n_results=3)
        
        # Optional: Filter context based on distance/relevance score
        # For example, if distances[0] (most relevant) is too high, maybe don't use context.
        # For now, we'll use all retrieved documents.

        # 3. Construct the prompt for the LLM
        prompt = self._construct_prompt(query, context_documents)

        # 4. Generate response from LLM (Ollama)
        final_response = self._generate_llm_response(prompt)
        
        print(f"Final response for query '{query}': '{final_response}'")
        return final_response

# --- Quick Test (optional, for direct script execution) ---
if __name__ == '__main__':
    print("Running ChatbotService test...")
    try:
        # Ensure Ollama is running and the model 'koesn/llama3-8b-instruct:latest' is available.
        # Also ensure your 'faqs.json' and vector store are populated from Phase 3.
        
        chatbot = ChatbotService() # This will print initialization messages

        # Test queries - replace with questions relevant to your FAQs
        test_queries = [
            "What are my payment options?",
            "How can I verify this communication?",
            "What if I cannot pay now?",
            "Tell me about financial difficulty resources.", # Example for which you might not have context
            "What is the capital of France?" # Irrelevant query
        ]

        for q in test_queries:
            print(f"\n--- Test Query: {q} ---")
            response = chatbot.get_rag_response(q)
            print(f"Chatbot's Answer: {response}")

    except Exception as e:
        print(f"An error occurred during the test: {e}")
        import traceback
        traceback.print_exc()