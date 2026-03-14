import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, 'venv', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def process_reviews_with_llm(reviews):
    """
    Sends the reviews to Groq LLM to extract themes, quotes, and action ideas.
    Returns a structured dictionary (JSON-like) response.
    """
    # Initialize Groq client
    # Try getting from standard os.env or Streamlit Secrets (for cloud deployment)
    try:
        import streamlit as st
        api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    except (ImportError, FileNotFoundError):
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please check your .env file or Streamlit secrets.")
        
    client = Groq(api_key=api_key)
    
    # Prepare the input data
    reviews_text = ""
    for idx, review in enumerate(reviews):
        # Limit to 150 reviews for token size constraints (TPM limits)
        if idx >= 150: 
            break
        text = review.get('text', '').strip()
        rating = review.get('rating', '')
        if text:
            reviews_text += f"[Rating: {rating}] {text}\n"

    # Define the prompt
    prompt = f"""
    You are an AI assistant analyzing app store reviews for the Groww app.
    I will provide you with a list of recent user reviews.
    
    Your task is to analyze these reviews and provide a structured JSON output with the following EXACT format:
    {{
        "top_themes": [
            {{"theme": "Theme 1", "description": "Brief description of the theme based on reviews"}},
            {{"theme": "Theme 2", "description": "Brief description of the theme based on reviews"}},
            {{"theme": "Theme 3", "description": "Brief description of the theme based on reviews"}}
        ],
        "user_quotes": [
            {{"theme": "Theme 1", "quote": "Exact relevant quote from a user without PII"}},
            {{"theme": "Theme 2", "quote": "Exact relevant quote from a user without PII"}},
            {{"theme": "Theme 3", "quote": "Exact relevant quote from a user without PII"}}
        ],
        "action_ideas": [
            {{"idea": "Actionable idea 1", "justification": "Why this idea based on negative/feature-request reviews"}},
            {{"idea": "Actionable idea 2", "justification": "Why this idea based on negative/feature-request reviews"}},
            {{"idea": "Actionable idea 3", "justification": "Why this idea based on negative/feature-request reviews"}}
        ]
    }}
    
    Ensure you output VALID JSON only. Do not wrap it in markdown block quotes like ```json ... ```. Just the raw JSON object.
    
    Here are the reviews:
    {reviews_text}
    """

    print("Sending request to Groq LLM...")
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful data analyst that only outputs valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant", 
            temperature=0.2, # Low temperature for more deterministic/consistent output
            response_format={"type": "json_object"} # Force JSON output
        )
        
        response_content = chat_completion.choices[0].message.content
        return json.loads(response_content)
        
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

def main():
    print("Starting LLM Processing Phase 3...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # Input file from Phase 2
    input_file = os.path.join(project_root, "Phase_2_Data_Preprocessing", "data", "sanitized_reviews.json")
    
    # Output directory
    output_dir = os.path.join(current_dir, "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created data directory at: {output_dir}")
        
    output_file = os.path.join(output_dir, "llm_output.json")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        reviews = json.load(f)
        
    print(f"Loaded {len(reviews)} sanitized reviews. Processing...")
    
    llm_result = process_reviews_with_llm(reviews)
    
    if llm_result:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(llm_result, f, indent=4, ensure_ascii=False)
        print(f"Successfully processed reviews and saved insights to {output_file}")
    else:
        print("Failed to get a valid response from the LLM.")

if __name__ == "__main__":
    main()
