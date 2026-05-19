import json
import os


# Define file paths
RAW_BUSINESS_FILE = "data/yelp_academic_dataset_business.json"
OUTPUT_FILTERED_FILE = "data/filtered_yelp_auto_shops.json"

def extract_and_localize_mechanics():
    print("Starting extraction from Yelp dataset...")
    
    # Check if the raw file exists where it should be
    if not os.path.exists(RAW_BUSINESS_FILE):
        print(f"Error: Could not find '{RAW_BUSINESS_FILE}'.")
        print("Please ensure the unzipped 'yelp_academic_dataset_business.json' is moved inside your 'data/' folder.")
        return

    filtered_count = 0
    
    # Target keywords for AutoCare related businesses
    target_categories = ["Auto Repair", "Mechanic", "Automotive", "Oil Change", "Brake Repair"]

    # this function will open the raw file for reading and a new file for writing the small subset
    with open(RAW_BUSINESS_FILE, "r", encoding="utf-8", errors="ignore") as infile, \
         open(OUTPUT_FILTERED_FILE, "w", encoding="utf-8", errors="ignore") as outfile:
        
        for line in infile:
            cleaned_line = line.strip()
            if not cleaned_line:                
                continue

            try:
                business = json.loads(cleaned_line)
            except json.JSONDecodeError:
                print(f"Warning: Skipping invalid JSON line: {cleaned_line}")
                continue

            categories = business.get("categories")
            
            # Check if this business belongs to the automotive sector
            if categories and any(keyword in categories for keyword in target_categories):
                
                # this dynamically map US/Canada data to Lagos neighborhoods!
                if filtered_count % 3 == 0:
                    business["city"] = "Lagos"
                    business["state"] = "LAG"
                    business["address"] = f"{business.get('address', 'Main Street')}, Yaba"
                elif filtered_count % 3 == 1:
                    business["city"] = "Lagos"
                    business["state"] = "LAG"
                    business["address"] = f"{business.get('address', 'Expressway')}, Lekki Phase 1"
                else:
                    business["city"] = "Lagos"
                    business["state"] = "LAG"
                    business["address"] = f"{business.get('address', 'Avenue')}, Ikeja"
                
                # Write the modified line immediately to our output file
                outfile.write(json.dumps(business) + "\n")
                filtered_count += 1

    print(f"Success! Extracted {filtered_count} auto shops.")
    print(f"Saved cleanly to: {OUTPUT_FILTERED_FILE}")

if __name__ == "__main__":
    extract_and_localize_mechanics()