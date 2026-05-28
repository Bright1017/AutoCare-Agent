import json
import os

RAW_BUSINESS_FILE = "data/yelp_academic_dataset_business.json"
OUTPUT_FILTERED_FILE = "data/filtered_yelp_auto_shops.json"

# Real Lagos co-ordinates that matches Nigerian maps
LAGOS_COORDINATES = {
    "Yaba": (6.5165, 3.3712),
    "Lekki Phase 1": (6.4474, 3.4716),
    "Ikeja": (6.5913, 3.3411)
}

def extract_and_localize_mechanics():
    print("Starting extraction from Yelp dataset...")
    
    if not os.path.exists(RAW_BUSINESS_FILE):
        print(f"Error: Could not find '{RAW_BUSINESS_FILE}'.")
        return

    filtered_count = 0
    target_categories = ["Auto Repair", "Mechanic", "Automotive", "Oil Change", "Brake Repair"]

    with open(RAW_BUSINESS_FILE, "r", encoding="utf-8", errors="ignore") as infile, \
         open(OUTPUT_FILTERED_FILE, "w", encoding="utf-8", errors="ignore") as outfile:
        
        for line in infile:
            cleaned_line = line.strip()
            if not cleaned_line: continue

            try:
                business = json.loads(cleaned_line)
            except json.JSONDecodeError:
                continue

            categories = business.get("categories")
            
            if categories and any(keyword in categories for keyword in target_categories):
                
                # Determine sector based on existing sequential % 3 loop
                if filtered_count % 3 == 0:
                    sector = "Yaba"
                    address_suffix = "Yaba"
                elif filtered_count % 3 == 1:
                    sector = "Lekki Phase 1"
                    address_suffix = "Lekki Phase 1"
                else:
                    sector = "Ikeja"
                    address_suffix = "Ikeja"
                
                # Localize text fields
                business["city"] = "Lagos"
                business["state"] = "LAG"
                business["address"] = f"{business.get('address', 'Main Street')}, {address_suffix}"
                
                # OVERWRITE FOREIGN COORDINATES WITH REAL LAGOS COORDINATES
                business["latitude"] = LAGOS_COORDINATES[sector][0]
                business["longitude"] = LAGOS_COORDINATES[sector][1]
                
                # ADD AN EXPLICIT METADATA SEARCH TAG 
                business["location_sector"] = sector
                
                outfile.write(json.dumps(business) + "\n")
                filtered_count += 1

    print(f"Success! Extracted and localized {filtered_count} auto shops with accurate Lagos GPS anchors.")

if __name__ == "__main__":
    extract_and_localize_mechanics()