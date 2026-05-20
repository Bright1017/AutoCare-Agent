import json
import os
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

# 1. Initialize the ChromaDB persistent client using settings paths
chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

# 2. Configure OpenAI Embedding Function to vectorise our search context
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name="text-embedding-3-small" 
)

# 3. Create or get our specialized Lagos auto shops vector collection
collection = chroma_client.get_or_create_collection(
    name="lagos_mechanic_catalog",
    embedding_function=openai_ef
)

def seed_vector_db():
    """
    Reads the filtered Lagos auto repair shop JSON file and populates ChromaDB.
    This skips automatically if data is already present to prevent duplicates.
    """
    print("Checking Vector Database status...")
    
    # Check if we already loaded the dataset previously
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Vector database already seeded with {existing_count} auto shops.")
        return

    # Check if our custom data file exists
    if not os.path.exists(settings.YELP_DATA_PATH):
        print(f"Error: Seed file missing at {settings.YELP_DATA_PATH}. Run extract.py first!")
        return

    print("Seeding ChromaDB Vector Database from filtered dataset...")
    
    ids = []
    documents = []
    metadatas = []

    with open(settings.YELP_DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            
            shop = json.loads(line)
            
            # Formulate unique string IDs and clear metadata properties
            shop_id = shop["business_id"]
            name = shop["name"]
            address = shop.get("address", "Lagos, Nigeria")
            stars = float(shop.get("stars", 0.0))
            categories = shop.get("categories", "Auto Repair")
            
            # Create a rich semantic document description string.
            # This is what the LLM embedding engine analyzes for conceptual matching!
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

    # Batch insert into ChromaDB (handling large datasets systematically)
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
        print(f"  ↳ Indexed records {i} to {min(i+batch_size, len(ids))}...")

    print(f"Database Seeding Complete! {collection.count()} shops successfully vectorized.")

def search_nearby_mechanics(query_context: str, limit: int = 3):
    """
    this function performs a semantic vector search based on Chika's contextual mood or vehicle problems.
    """
    results = collection.query(
        query_texts=[query_context],
        n_results=limit
    )
    return results