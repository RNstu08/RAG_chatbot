# scripts/build_knowledge_base.py
import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
import chromadb.utils.embedding_functions as embedding_functions # For later if we use Chroma's embedder


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

MODEL_NAME = 'all-MiniLM-L6-v2'

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
