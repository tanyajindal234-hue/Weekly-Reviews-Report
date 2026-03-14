import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so we can import from other phases
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def load_environment():
    dotenv_path = os.path.join(project_root, 'venv', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    
    try:
        import streamlit as st
        sender_email = st.secrets.get("EMAIL_SENDER", os.getenv("EMAIL_SENDER"))
        sender_password = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
        recipient_email = st.secrets.get("EMAIL_RECIPIENT", os.getenv("EMAIL_RECIPIENT"))
        recipient_name = st.secrets.get("EMAIL_RECIPIENT_NAME", os.getenv("EMAIL_RECIPIENT_NAME", "Team"))
    except (ImportError, FileNotFoundError):
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        recipient_email = os.getenv("EMAIL_RECIPIENT")
        recipient_name = os.getenv("EMAIL_RECIPIENT_NAME", "Team")
        
    return {
        "EMAIL_SENDER": sender_email,
        "EMAIL_PASSWORD": sender_password,
        "EMAIL_RECIPIENT": recipient_email,
        "EMAIL_RECIPIENT_NAME": recipient_name
    }

def main():
    print("Starting Weekly Pulse Automation Pipeline...")
    
    # 1. Load configuration
    env_vars = load_environment()
    if not all([env_vars["EMAIL_SENDER"], env_vars["EMAIL_PASSWORD"], env_vars["EMAIL_RECIPIENT"]]):
        print("Error: Missing critical email configurations in .env file.")
        sys.exit(1)
        
    print(f"Loaded config. Reporting to: {env_vars['EMAIL_RECIPIENT_NAME']} <{env_vars['EMAIL_RECIPIENT']}>")
    
    # Normally we would import and call the pipeline functions here sequentially:
    # 2. Phase 1: Ingestion
    print("\n--- Phase 1: Data Ingestion (Simulated) ---")
    # from Phase_1_Data_Ingestion.fetch_reviews import fetch_reviews
    # fetch_reviews()
    
    # 3. Phase 2: Pre-processing
    print("\n--- Phase 2: Data Pre-processing (Simulated) ---")
    # from Phase_2_Data_Preprocessing.preprocess import clean_data
    # clean_data()
    
    # 4. Phase 3: LLM Processing
    print("\n--- Phase 3: Core LLM Processing ---")
    from Phase_3_LLM_Processing.llm_processor import main as run_llm
    try:
        run_llm()
    except Exception as e:
        print(f"Error during LLM Processing: {e}")
        sys.exit(1)
        
    # 5. Phase 4: Formatting & Email Drafting
    print("\n--- Phase 4: Formatting and Emailing ---")
    import json
    from Phase_4_Formatting_and_Email.email_drafter import generate_email_html, send_email
    
    llm_output_path = os.path.join(project_root, "Phase_3_LLM_Processing", "data", "llm_output.json")
    if not os.path.exists(llm_output_path):
        print("Error: Could not find LLM output file. Pipeline failed.")
        sys.exit(1)
        
    with open(llm_output_path, 'r', encoding='utf-8') as f:
        llm_data = json.load(f)
        
    html_content = generate_email_html(llm_data, recipient_name=env_vars["EMAIL_RECIPIENT_NAME"])
    
    success = send_email(
        sender_email=env_vars["EMAIL_SENDER"],
        sender_password=env_vars["EMAIL_PASSWORD"],
        recipient_email=env_vars["EMAIL_RECIPIENT"],
        recipient_name=env_vars["EMAIL_RECIPIENT_NAME"],
        html_content=html_content
    )
    
    if success:
        print("\nPipeline completed successfully!")
    else:
        print("\nPipeline finished with email errors.")
        sys.exit(1)

if __name__ == "__main__":
    main()
