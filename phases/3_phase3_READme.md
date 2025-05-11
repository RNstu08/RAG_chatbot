Let's move on to **Phase 3: Knowledge Base Preparation**.

This phase is all about creating and processing the information our chatbot will use to answer questions. In a RAG (Retrieval Augmented Generation) system, the quality and structure of your knowledge base are critical for the chatbot's performance.

---

**Phase 3: Knowledge Base Preparation**

**1. Create FAQ/Knowledge Base Content:**

* **What:** We need to create a collection of frequently asked questions (FAQs) and their corresponding answers. These will form the "knowledge" that our chatbot retrieves information from. For this project, the context is general queries related to debt management or account issues.
* **Why:**
    * **Grounding the LLM:** The RAG model relies on this content to provide factual and relevant answers. Without a good knowledge base, the LLM might hallucinate or give generic, unhelpful responses.
    * **Defining Scope:** The content of the knowledge base implicitly defines what the chatbot can answer accurately.
    * **Empathetic Tone:** We can bake empathy and helpfulness directly into the answers we provide in the knowledge base.
* **How:**
    1.  **Identify Common Questions:** Think about typical questions someone might have if they are contacted about an outstanding account or have queries about managing payments. Examples:
        * "What are my payment options?"
        * "How can I verify this communication is legitimate?"
        * "What happens if I can't pay the full amount right now?"
        * "Can I set up a payment plan?"
        * "Who can I speak to if I have a dispute?"
        * "I don't believe this account relates to me, what should I do?"
        * "How can I update my contact information?"
        * "What resources are available if I'm facing financial difficulty?"
    2.  **Craft Clear, Empathetic Answers:**
        * Keep answers concise but comprehensive.
        * Use simple, easy-to-understand language.
        * Maintain a helpful, understanding, and non-judgmental tone.
    3.  **Format:** We'll store this data in a structured format. A JSON file is a good choice. Each entry could be an object with "id", "question", and "answer" fields.
* **Example FAQ entries (conceptual):**
    ```json
    [
      {
        "id": "faq001",
        "question": "What are the available methods for making a payment?",
        "answer": "You can make a payment through several convenient methods, including online bank transfer, setting up a direct debit, or speaking with one of our agents to process a card payment over the phone. We are here to help you find the option that works best for you."
      },
      {
        "id": "faq002",
        "question": "How can I confirm that this communication is genuinely from your organization?",
        "answer": "We understand the importance of security. You can verify our legitimacy by checking our official contact details on our website or by calling us back on a publicly listed phone number. Please never share full passwords or sensitive personal details unless you are certain of the contact's authenticity."
      },
      {
        "id": "faq003",
        "question": "I'm worried I can't afford to pay the full amount immediately.",
        "answer": "We understand that financial situations can be challenging. Please contact us to discuss your circumstances. We have various options, such as setting up a manageable payment plan, and we're committed to working with you to find a suitable solution."
      }
    ]
    ```
* **Action:** Create a file named `faqs.json` inside the `rag_chatbot_coeo/app/knowledge_base/` directory. Populate it with at least 5-10 FAQs relevant to general account/payment queries, following the structure above. The more comprehensive and well-written your FAQs, the better your chatbot will be.
* **Edge Cases/Considerations:**
    * **Vagueness:** Try to make questions distinct enough to avoid too much overlap, though some overlap is natural.
    * **Updates:** In a real system, this knowledge base would need regular updates.

**2. Load and Preprocess Documents (FAQs):**

* **What:** Write Python code to load the `faqs.json` file. For this project, our "documents" are the answers, and potentially the questions too, or a combination. We need to decide what text goes into the embedding process. A common approach is to embed the answers, or sometimes question-answer pairs. For simplicity and effectiveness in an FAQ scenario, embedding the *concatenation of question and answer* can be very effective for retrieval, as queries are often similar to the stored questions.
* **Why:** To get the text data into our Python program for further processing (embedding and indexing).
* **How (Python):**
    Let's create a utility script for building our knowledge base. Create a new file, for example, `rag_chatbot_coeo/scripts/build_knowledge_base.py`.

    ```python
    # scripts/build_knowledge_base.py
    import json
    import os

    # Construct the path to the faqs.json file relative to this script
    # This assumes 'scripts' and 'app' are sibling directories in the project root
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(CURRENT_DIR) # This should be rag_chatbot_coeo
    FAQ_PATH = os.path.join(PROJECT_ROOT, 'app', 'knowledge_base', 'faqs.json')

    def load_faqs(file_path=FAQ_PATH):
        """Loads FAQs from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                faqs = json.load(f)
            print(f"Successfully loaded {len(faqs)} FAQs from {file_path}")
            return faqs
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
            return []
        except json.JSONDecodeError:
            print(f"Error: The file {file_path} is not a valid JSON.")
            return []
        except Exception as e:
            print(f"An unexpected error occurred while loading {file_path}: {e}")
            return []

    def preprocess_faqs(faqs_data):
        """
        Prepares FAQs for embedding.
        Each document will be a combination of question and answer.
        We also store metadata (like the original question and answer separately, and the ID).
        """
        documents = [] # This will be the text we embed
        metadatas = [] # This will store associated info for each document

        for faq in faqs_data:
            # We'll embed the combination of question and answer for better semantic matching.
            combined_text = f"Question: {faq['question']} Answer: {faq['answer']}"
            documents.append(combined_text)
            
            # Store original question, answer, and ID as metadata.
            # This metadata can be retrieved alongside the document.
            metadatas.append({
                'original_question': faq['question'],
                'original_answer': faq['answer'],
                'faq_id': faq['id']
            })
        
        print(f"Preprocessed {len(documents)} documents for embedding.")
        return documents, metadatas

    if __name__ == "__main__":
        faqs_data = load_faqs()
        if faqs_data:
            documents, metadatas = preprocess_faqs(faqs_data)
            # In the next steps, we will add embedding and storage logic here.
            # For now, let's just see the output:
            # for i in range(len(documents)):
            #     print(f"Document {i+1}: {documents[i]}")
            #     print(f"Metadata {i+1}: {metadatas[i]}\n")
        else:
            print("No FAQs loaded, knowledge base build process aborted.")

    ```
    * **Key Concepts:**
        * **Document Loading:** Reading data from a file.
        * **Text Preprocessing:** Preparing text for ML models. In our case, it's quite minimal (combining Q&A). More complex scenarios might involve HTML stripping, lowercasing, stop-word removal, stemming/lemmatization, but for modern transformer-based embedding models, minimal preprocessing is often better.
        * **Chunking (Not strictly needed for short FAQs):** For long documents, you'd split them into smaller, manageable chunks before embedding. Since FAQs are usually short, each Q&A pair can be a single "document" for embedding. If an answer were very long, we might consider chunking it.
    * **Modularity:** This script is separate from the main application logic. You'd run it once (or whenever the FAQs change) to build/update the vector store.

**3. Generate Embeddings:**

* **What:** Convert the preprocessed text documents (our Q&A pairs) into numerical vectors (embeddings) using a sentence-transformer model.
* **Why:**
    * **Semantic Meaning:** Embeddings capture the semantic meaning of the text. Texts with similar meanings will have similar vector representations (i.e., they'll be "close" to each other in the vector space).
    * **Similarity Search:** This allows us to take a user's query, embed it using the same model, and then find the most similar (i.e., most relevant) FAQs from our knowledge base by comparing their embeddings.
* **Key Concepts:**
    * **Embeddings:** Dense vector representations of text (or other data).
    * **Sentence-Transformers:** A Python library that provides easy access to many pre-trained models for generating high-quality sentence and text embeddings. `all-MiniLM-L6-v2` is a popular choice: fast and good quality.
* **How (Python):**
    Add to `scripts/build_knowledge_base.py`:
    ```python
    # ... (keep previous imports and functions: load_faqs, preprocess_faqs)
    # Add new import for sentence-transformers
    from sentence_transformers import SentenceTransformer

    MODEL_NAME = 'all-MiniLM-L6-v2' # A good, widely used model

    def generate_embeddings(documents, model_name=MODEL_NAME):
        """Generates embeddings for a list of documents using a SentenceTransformer model."""
        try:
            print(f"Loading sentence transformer model: {model_name}...")
            model = SentenceTransformer(model_name)
            print("Model loaded. Generating embeddings...")
            embeddings = model.encode(documents, show_progress_bar=True)
            print(f"Successfully generated {len(embeddings)} embeddings.")
            return embeddings
        except Exception as e:
            print(f"Error during embedding generation: {e}")
            return None

    if __name__ == "__main__":
        faqs_data = load_faqs()
        if faqs_data:
            documents_to_embed, metadatas_for_store = preprocess_faqs(faqs_data)
            
            if documents_to_embed:
                embeddings_data = generate_embeddings(documents_to_embed)
                
                if embeddings_data is not None:
                    # In the next step, we'll store these embeddings and metadatas.
                    # For now, you could print the shape of the embeddings array:
                    # print(f"Shape of embeddings array: {embeddings_data.shape}")
                    pass # Placeholder for storage step
                else:
                    print("Embedding generation failed.")
            else:
                print("No documents to embed.")
        else:
            print("No FAQs loaded, knowledge base build process aborted.")
    ```
    * When you run this, `sentence-transformers` will download the `all-MiniLM-L6-v2` model the first time (if you don't have it cached) and then compute the embeddings.

**4. Store Embeddings in a Vector Database (ChromaDB):**

* **What:** Store the generated embeddings along with their corresponding documents (or references/IDs) and metadata in ChromaDB.
* **Why:**
    * **Efficient Similarity Search:** Vector databases are specifically designed to perform fast similarity searches over high-dimensional vectors. Given a query vector, they can quickly find the "nearest" vectors in the stored collection.
    * **Persistence:** ChromaDB can persist the database to disk, so we don't have to rebuild it every time our main application starts.
    * **Metadata Storage:** Allows storing additional information with each vector, which can be retrieved during a search (e.g., the original answer text).
* **Key Concepts:**
    * **Vector Store/Database:** A database optimized for storing and querying vector embeddings.
    * **Indexing:** The process of organizing the vectors in a way that speeds up search.
    * **Collection:** In ChromaDB, a collection is like a table where you store your embeddings, documents, and metadatas.
* **How (Python):**
    Add to `scripts/build_knowledge_base.py`:
    ```python
    # ... (keep previous imports and functions)
    # Add new import for chromadb
    import chromadb
    import chromadb.utils.embedding_functions as embedding_functions # For later if we use Chroma's embedder

    # Define path for ChromaDB persistence
    CHROMA_DB_PATH = os.path.join(PROJECT_ROOT, 'app', 'knowledge_base', 'vector_store')
    COLLECTION_NAME = "faq_collection"

    def store_in_chromadb(documents, embeddings, metadatas, db_path=CHROMA_DB_PATH, collection_name=COLLECTION_NAME):
        """Stores documents, embeddings, and metadatas in ChromaDB."""
        try:
            print(f"Initializing ChromaDB client for path: {db_path}")
            # persistent_client = chromadb.PersistentClient(path=db_path) # This will save to disk
            
            # For simplicity in setup and ensuring it's always fresh when script runs,
            # let's use an in-memory client first for illustration, then switch to persistent.
            # For a build script, you usually want persistent:
            if not os.path.exists(db_path):
                os.makedirs(db_path)
                print(f"Created directory for ChromaDB: {db_path}")

            persistent_client = chromadb.PersistentClient(path=db_path)

            # If you want to use ChromaDB's own embedding function (e.g., with SentenceTransformer)
            # you can specify it when getting or creating the collection.
            # For now, we are providing our own pre-computed embeddings.
            
            print(f"Getting or creating collection: {collection_name}")
            # If the collection exists, you might want to delete it to rebuild, or update it.
            # For a simple build script, deleting and rebuilding is often easiest.
            try:
                persistent_client.delete_collection(name=collection_name)
                print(f"Deleted existing collection: {collection_name}")
            except Exception: # Handles cases where collection doesn't exist or other errors
                print(f"Collection {collection_name} either did not exist or could not be deleted. Proceeding to create.")

            collection = persistent_client.get_or_create_collection(
                name=collection_name
                # If you wanted Chroma to handle embeddings, you would add:
                # embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
            )
            
            # Generate unique IDs for each document if your FAQs don't have them,
            # or use existing IDs. Chroma requires string IDs.
            doc_ids = [f"doc_{i}" for i in range(len(documents))]
            # If your 'faq_id' in metadatas is unique and suitable, you could use those.
            # For this example, let's ensure they are string and unique for Chroma.
            # doc_ids = [str(meta['faq_id']) for meta in metadatas]


            print(f"Adding {len(documents)} items to the collection...")
            # When providing your own embeddings, use the 'embeddings' argument.
            # The 'documents' argument here is the actual text content you want to associate and retrieve.
            collection.add(
                embeddings=embeddings.tolist(), # Chroma expects list of lists or numpy array
                documents=documents, # The text content we embedded (e.g., "Question: ... Answer: ...")
                metadatas=metadatas, # Our list of metadata dictionaries
                ids=doc_ids # List of unique string IDs for each item
            )
            print(f"Successfully stored {collection.count()} items in ChromaDB collection '{collection_name}'.")
            return True
        except Exception as e:
            print(f"Error storing data in ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        faqs_data = load_faqs()
        if faqs_data:
            documents_to_embed, metadatas_for_store = preprocess_faqs(faqs_data)
            
            if documents_to_embed:
                embeddings_data = generate_embeddings(documents_to_embed)
                
                if embeddings_data is not None:
                    success = store_in_chromadb(documents_to_embed, embeddings_data, metadatas_for_store)
                    if success:
                        print("Knowledge base build process completed successfully.")
                    else:
                        print("Knowledge base build process failed during storage.")
                else:
                    print("Embedding generation failed. Aborting storage.")
            else:
                print("No documents to embed.")
        else:
            print("No FAQs loaded, knowledge base build process aborted.")
    ```

* **To run this script:**
    1.  Make sure your `faqs.json` is created and populated in `app/knowledge_base/`.
    2.  Ensure your virtual environment `(venv)` is active.
    3.  From your project root (`rag_chatbot_coeo`), run:
        ```bash
        python scripts/build_knowledge_base.py
        ```
    This will load FAQs, generate embeddings, and store them in a ChromaDB instance located at `rag_chatbot_coeo/app/knowledge_base/vector_store/`. You should see files appearing in that directory.

---

This concludes Phase 3. You now have:
1.  A set of FAQs in `faqs.json`.
2.  A Python script (`scripts/build_knowledge_base.py`) that can:
    * Load these FAQs.
    * Preprocess them for embedding.
    * Generate embeddings using `sentence-transformers`.
    * Store these embeddings, along with the source text and metadata, into a persistent ChromaDB vector store.

This vector store is the "retrieval" part of our RAG system. In the next phase, we'll build the logic to query this store and use the results to generate answers with Ollama.

**Key Takeaways:**
* The quality of your FAQs directly impacts chatbot performance.
* Embeddings allow for semantic search.
* Vector databases like ChromaDB make this search efficient.
* Keeping the knowledge base build process as a separate script is good for modularity.
