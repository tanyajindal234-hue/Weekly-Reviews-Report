import os
import json
from scraper import fetch_groww_play_store_reviews

def main():
    print("Starting Data Ingestion Phase 1...")
    
    # Define data directory relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory at: {data_dir}")
        
    # Fetch reviews (Limit to 1000 MAX, up to 12 weeks back)
    print("Fetching Google Play Store reviews for Groww (up to 1000, last 12 weeks, English only)...")
    reviews = fetch_groww_play_store_reviews(max_results=1000, weeks_back=12)
    
    print(f"Successfully fetched {len(reviews)} reviews within the date range.")
    
    # Save the reviews to a JSON file
    output_file = os.path.join(data_dir, "fetched_reviews.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=4, ensure_ascii=False)
        
    print(f"Saved reviews to {output_file}")

if __name__ == "__main__":
    main()
