import json
import os
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

# 1. Initialize the ChromaDB persistent client using settings paths
persist_dir = getattr(settings, "CHROMA_PERSIST_DIRECTORY", getattr(settings, "CHROMA_DB_PATH", "./chroma_db"))
chroma_client = chromadb.PersistentClient(path=persist_dir)

# 2. Configure a FREE, LOCAL Embedding Function (Bypasses OpenAI completely!)
# This model downloads a small mathematical matrix locally and computes vectors on your CPU
local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 3. Create or get our specialized Lagos auto shops vector collection using the free engine
collection = chroma_client.get_or_create_collection(
    name="lagos_mechanic_catalog_local",
    embedding_function=local_ef
)

def seed_vector_db():
    """
    Reads the filtered Lagos auto repair shop JSON file and populates ChromaDB.
    Skips automatically if data is already present to prevent duplicates.
    """
    print("Checking Vector Database status...")
    
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Vector database already seeded with {existing_count} auto shops.")
        return

    # Checking if our custom data file exists
    if not os.path.exists(settings.YELP_DATA_PATH):
        print(f"Error: Seed file missing at {settings.YELP_DATA_PATH}. Run extract.py first!")
        return
        
    print("Seeding ChromaDB Vector Database from filtered dataset using local embeddings...")
    
    ids = []
    documents = []
    metadatas = []

    with open(settings.YELP_DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
        # Check if the file is a standard JSON list or line-by-line JSON (JSON Lines)
        content = f.read().strip()
        
        try:
            # Try parsing as a standard JSON array list first
            shops = json.loads(content)
            for shop in shops:
                _process_shop(shop, ids, documents, metadatas)
        except json.JSONDecodeError:
            # Fallback to your original line-by-line JSON parsing if it's a JSONL file
            f.seek(0)
            for line in f:
                if not line.strip():
                    continue
                shop = json.loads(line)
                _process_shop(shop, ids, documents, metadatas)

    # Inserting data by batches into ChromaDB
    batch_size = 100  # Smaller batches for local memory safety
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
        print(f"Indexed records {i} to {min(i+batch_size, len(ids))}...")

    print(f"Database Seeding Complete! {collection.count()} shops successfully stored!")


def _process_shop(shop, ids, documents, metadatas):
    """Helper extraction utility function matching your business schema logic"""
    shop_id = shop.get("business_id", f"shop_{len(ids)}")
    name = shop.get("name", "Unknown Shop")
    address = shop.get("address", "Lagos, Nigeria")
    stars = float(shop.get("stars", 0.0))
    
    # Safely handle list categories vs string categories
    cats = shop.get("categories", "Auto Repair")
    categories = ", ".join(cats) if isinstance(cats, list) else str(cats)
    
    # Rich semantic document description string for the Local embedding engine
    semantic_document = (
        f"Mechanic Shop: {name}. Located at: {address}. "
        f"Services and Specialities: {categories}. Historical Yelp Rating: {stars} stars."
    )
    
    ids.append(shop_id)
    documents.append(semantic_document)
    metadatas.append({
        "name": name,
        "address": address,
        "stars": stars,
        "categories": categories
    })


def query_mechanics(query_text: str, n_results: int = 3) -> list:
    """
    Performs a semantic vector search based on the user's vehicle problems.
    Flattens the nested ChromaDB output structure into clean dictionaries for the agents.
    """
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        formatted_shops = []
        
        # Unpacking the deep nested arrays that ChromaDB will return
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            ids = results["ids"][0]
            
            for i in range(len(ids)):
                shop_data = {
                    "id": ids[i],
                    "name": metadatas[i].get("name", "Unknown Shop"),
                    "stars": metadatas[i].get("stars", 3.0),
                    "categories": metadatas[i].get("categories", "General Auto Repair"),
                    "review_context": documents[i] 
                }
                formatted_shops.append(shop_data)
                
        return formatted_shops

    except Exception as e:
        print(f"Error executing ChromaDB semantic lookup: {e}")
        return []