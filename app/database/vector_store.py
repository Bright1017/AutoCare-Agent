import json
import os
import chromadb
from app.config import settings
from dotenv import load_dotenv

# Force load the .env file attributes into system environment memory
load_dotenv()

# 1. Initialize Dual-Mode Connection (Dynamically switches to Chroma Cloud)
cloud_key = os.getenv("CHROMA_API_KEY")
tenant = os.getenv("CHROMA_TENANT")
database = os.getenv("CHROMA_DATABASE", "AutoCare-Agent-Database")

if cloud_key and tenant:
    print("Connecting to secure serverless Chroma Cloud instance...")
    chroma_client = chromadb.CloudClient(
        api_key=cloud_key,
        tenant=tenant,
        database=database
    )

    # Serverless Chroma Cloud handles embeddings automatically when raw text is passed.
    collection = chroma_client.get_or_create_collection(
        name="lagos_mechanic_catalog_cloud"
    )
else:
    print("Cloud keys missing. Defaulting to local persistent storage...")
    from chromadb.utils import embedding_functions
    persist_dir = getattr(settings, "CHROMA_PERSIST_DIRECTORY", getattr(settings, "CHROMA_DB_PATH", "./chroma_db"))
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    
    # Local fallback only requires embedding libraries locally
    local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = chroma_client.get_or_create_collection(
        name="lagos_mechanic_catalog_local",
        embedding_function=local_ef
    )

def seed_vector_db():
    """Reads the filtered Lagos auto repair shop JSON file and populates ChromaDB."""
    print("Checking Vector Database status...")
    
    existing_count = collection.count()
    if existing_count > 0:
        print(f"Vector database already seeded with {existing_count} auto shops.")
        return

    # Fallback to absolute or config path safely
    data_path = getattr(settings, "YELP_DATA_PATH", "data/filtered_yelp_auto_shops.json")
    if not os.path.exists(data_path):
        print(f"Error: Seed file missing at {data_path}. Run extract/update scripts first!")
        return
        
    print(f"Seeding ChromaDB from {data_path}...")
    
    ids = []
    documents = []
    metadatas = []


    # define a helper function to process each shop entry and extract the relevant fields for ChromaDB ingestion
    with open(data_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                shop = json.loads(line)
                _process_shop(shop, ids, documents, metadatas)
            except Exception as e:
                continue

    # BATCH FOR CLOUD TRANSFERS
    batch_size = 300  # Adjust based on your memory and API limits  
    total_records = len(ids) # Ensure all three lists are the same length before proceeding with batch insertion
    print(f"Loaded {total_records} records into memory. Initiating cloud sync...")
    
    for i in range(0, total_records, batch_size):
        end_idx = min(i + batch_size, total_records)
        collection.add(
            ids=ids[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        print(f"Indexed records {i} to {end_idx} of {total_records}...")

    print(f"Database Seeding Complete! {collection.count()} shops safely stored in Cloud storage!")


def _process_shop(shop, ids, documents, metadatas):
    """Helper extraction utility function matching your business schema logic"""
    shop_id = shop.get("business_id", f"shop_{len(ids)}")
    name = shop.get("name", "Unknown Shop")
    address = shop.get("address", "Lagos, Nigeria")
    stars = float(shop.get("stars", 0.0))
    sector = shop.get("location_sector", "Ikeja") # Capture our custom ingestion router key!
    
    cats = shop.get("categories", "Auto Repair")
    categories = ", ".join(cats) if isinstance(cats, list) else str(cats)
    
    semantic_document = (
        f"Mechanic Shop: {name}. Located at: {address} within the {sector} neighborhood. "
        f"Services and Specialities: {categories}. Historical Rating: {stars} stars."
    )
    
    ids.append(shop_id)
    documents.append(semantic_document)
    metadatas.append({
        "name": name, # retain the name as metadata for potential future use in recommendations or user-facing details
        "address": address, # retain the address as metadata for potential future use in recommendations or user-facing details
        "stars": stars, # ensure numeric ratings are stored as floats for accurate filtering and display in recommendations
        "categories": categories, # capture the categories as metadata for enhanced filtering and display in recommendations
        "location_sector": sector  # adding the sector metadata for enhanced query filtering
    })

def query_mechanics(query_text: str, location_sector: str = None, n_results: int = 3) -> list:
    """Performs an isolated semantic vector search based on user neighborhood context."""
    try:
        # Build strict location query dict matching your UI inputs
        query_kwargs = {"query_texts": [query_text], "n_results": n_results}
        
        if location_sector:
            query_kwargs["where"] = {"location_sector": location_sector}
            
        results = collection.query(**query_kwargs)
        formatted_shops = []
        
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            ids = results["ids"][0]
            
            for i in range(len(ids)):
                formatted_shops.append({
                    "id": ids[i],
                    "name": metadatas[i].get("name", "Unknown Shop"),
                    "stars": metadatas[i].get("stars", 3.0),
                    "categories": metadatas[i].get("categories", "General Auto Repair"),
                    "location_sector": metadatas[i].get("location_sector", "Unknown"),
                    "review_context": documents[i] 
                })
                
        return formatted_shops

    except Exception as e:
        print(f"Error executing ChromaDB semantic lookup: {e}")
        return []