import os
import sys
import json
import streamlit as st
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Add parent directory to path so we can import from other phases
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Import Phase wrappers (Assuming we wrap them nicely later, for now we will just use the outputs or mock for speed)
# In a real scenario, you'd trigger Phase 1, 2, 3 sequentially here.
# For this phase, we'll act on the existing LLM output to draft the email, and provide a button to "Run Pipeline"

from Phase_4_Formatting_and_Email.email_drafter import generate_email_html, send_email

def load_environment():
    # Try to load from .env file (for local development)
    dotenv_path = os.path.join(project_root, 'venv', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    
    # Try getting from standard os.env or Streamlit Secrets (for cloud deployment)
    try:
        sender = st.secrets.get("EMAIL_SENDER", os.getenv("EMAIL_SENDER"))
        password = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
    except FileNotFoundError:
        # st.secrets raises FileNotFoundError locally if .streamlit/secrets.toml is missing
        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")
        
    return {
        "EMAIL_SENDER": sender,
        "EMAIL_PASSWORD": password
    }

def main():
    st.set_page_config(page_title="Groww Pulse Dashboard", page_icon="📈", layout="wide")
    
    st.title("📈 Groww Weekly Reviews Pulse")
    st.markdown("Automatically extract recent Play Store reviews, compress them using LLMs, and draft a Weekly Pulse Email.")
    
    # Sidebar Inputs
    
    recipient_email = st.sidebar.text_input("Recipient Email Address", placeholder="e.g., product-team@groww.in")
    recipient_name = st.sidebar.text_input("Recipient Name", placeholder="e.g., Growth Team")
    
    # Load env vars
    env_vars = load_environment()
    if not env_vars["EMAIL_SENDER"] or not env_vars["EMAIL_PASSWORD"]:
        st.sidebar.error("⚠️ Sender Email or Password not found in .env")
        return
        
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Generate Report")
        
        if st.button("Generate Weekly Pulse", type="primary"):
            if not recipient_email or not recipient_name:
                st.error("Please provide both Recipient Email and Recipient Name in the sidebar.")
            else:
                with st.spinner("Pipeline running (simulated)..."):
                    # Normally here we would call Phase 1 -> Phase 2 -> Phase 3
                    # For now, we load the cached output from Phase 3
                    llm_output_path = os.path.join(project_root, "Phase_3_LLM_Processing", "data", "llm_output.json")
                    
                    if os.path.exists(llm_output_path):
                        with open(llm_output_path, 'r', encoding='utf-8') as f:
                            st.session_state['llm_data'] = json.load(f)
                            
                        # Generate HTML
                        st.session_state['html_report'] = generate_email_html(
                            st.session_state['llm_data'], 
                            recipient_name=recipient_name
                        )
                        st.success("Report Generated Successfully!")
                    else:
                        st.error("Phase 3 output not found. Please run Phase 3 first.")
                        
    with col2:
        st.subheader("2. Preview & Send")
        
        if 'html_report' in st.session_state:
            with st.expander("Preview Email Draft", expanded=True):
                st.components.v1.html(st.session_state['html_report'], height=400, scrolling=True)
                
            if st.button("Send Email", type="secondary"):
                with st.spinner("Sending Email..."):
                    success = send_email(
                        sender_email=env_vars["EMAIL_SENDER"],
                        sender_password=env_vars["EMAIL_PASSWORD"],
                        recipient_email=recipient_email,
                        recipient_name=recipient_name,
                        html_content=st.session_state['html_report']
                    )
                    if success:
                        st.toast("Email Sent Successfully!", icon="🚀")
                        st.balloons()
                    else:
                        st.error("Failed to send email. Check console logs.")
        else:
            st.info("Generate the report first to preview the email.")

if __name__ == "__main__":
    main()
