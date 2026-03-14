import json
import re
import os

def sanitize_text(text):
    """
    Removes emails and phone numbers from the text using regex.
    """
    if not text:
        return text
    
    # 1. Remove Email Addresses
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    text = re.sub(email_pattern, '[EMAIL REDACTED]', text)
    
    # 2. Remove Phone Numbers
    # Matches generic phone numbers including Indian formats like +91-9876543210 or 9876543210
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, '[PHONE REDACTED]', text)
    
    return text

def main():
    print("Starting Data Pre-processing Phase 2...")
    
    # Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Input file from Phase 1
    input_file = os.path.join(project_root, "Phase_1_Data_Ingestion", "data", "fetched_reviews.json")
    
    # Output directory
    output_dir = os.path.join(current_dir, "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created data directory at: {output_dir}")
        
    output_file = os.path.join(output_dir, "sanitized_reviews.json")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
        
    print(f"Loaded {len(reviews)} reviews from Phase 1. Sanitizing data...")
    
    sanitized_reviews = []
    for review in reviews:
        sanitized_review = review.copy()
        sanitized_review['text'] = sanitize_text(review.get('text', ''))
        sanitized_reviews.append(sanitized_review)
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sanitized_reviews, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully sanitized reviews and saved to {output_file}")

if __name__ == "__main__":
    main()
