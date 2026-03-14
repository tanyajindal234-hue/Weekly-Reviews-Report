import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime

def generate_email_html(llm_data, recipient_name="Team"):
    """
    Converts the structured LLM JSON data into an HTML email format.
    """
    current_time = datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')
    
    html = f"""
    <html>
      <head>
        <style>
          body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
          h2 {{ color: #0056b3; border-bottom: 2px solid #ccc; padding-bottom: 5px; }}
          h3 {{ color: #0056b3; }}
          .theme-box {{ background-color: #f9f9f9; border-left: 4px solid #0056b3; padding: 10px; margin-bottom: 15px; }}
          .quote-box {{ background-color: #eef; font-style: italic; padding: 10px; border-left: 4px solid #4CAF50; margin-bottom: 15px; }}
          .action-box {{ background-color: #fff3e6; padding: 10px; border-left: 4px solid #ff9900; margin-bottom: 15px; }}
        </style>
      </head>
      <body>
        <p>Hi, {recipient_name}</p>
        <p>Here is your Weekly Pulse Report based on the latest Google Play Store reviews for the Groww app:</p>
        <p><em>Generated on: {current_time}</em></p>
        
        <h2>Top Themes</h2>
    """
    
    for theme in llm_data.get("top_themes", []):
        html += f"""
        <div class="theme-box">
            <strong>{theme['theme']}</strong>: {theme['description']}
        </div>
        """
        
    html += "<h2>User Quotes</h2>"
    for quote in llm_data.get("user_quotes", []):
        html += f"""
        <div class="quote-box">
            " {quote['quote']} " <br>
            <small>- Regarding: {quote['theme']}</small>
        </div>
        """
        
    html += "<h2>Actionable Ideas</h2>"
    for action in llm_data.get("action_ideas", []):
        html += f"""
        <div class="action-box">
            <strong>{action['idea']}</strong><br>
            <em>Why:</em> {action['justification']}
        </div>
        """
        
    html += """
        <p><br>Best Regards,<br>Groww Pulse Automated System</p>
      </body>
    </html>
    """
    return html

def send_email(sender_email, sender_password, recipient_email, recipient_name, html_content):
    """
    Sends an HTML email using SMTP.
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Groww Weekly Reviews Pulse Report'
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # Attach the HTML content
        part = MIMEText(html_content, 'html')
        msg.attach(part)
        
        # Connect to the server
        # Using Gmail SMTP server as an assumption based on common usage
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login and send
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def main():
    print("Starting Formatting & Email Drafting Phase 4...")
    
    # Load environment variables from the parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    dotenv_path = os.path.join(project_root, 'venv', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    
    try:
        import streamlit as st
        sender_email = st.secrets.get("EMAIL_SENDER", os.getenv("EMAIL_SENDER"))
        sender_password = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
        recipient_email = st.secrets.get("EMAIL_RECIPIENT", os.getenv("EMAIL_RECIPIENT"))
    except (ImportError, FileNotFoundError):
        sender_email = os.getenv("EMAIL_SENDER")
        sender_password = os.getenv("EMAIL_PASSWORD")
        recipient_email = os.getenv("EMAIL_RECIPIENT")
    # For testing from backend, we will extract the name from the email roughly, 
    # but in Phase 5 it will come from the UI.
    recipient_name = recipient_email.split('@')[0] if recipient_email else "Team"
    
    if not all([sender_email, sender_password, recipient_email]):
        print("Error: Missing email credentials in .env file.")
        return
        
    # Input file from Phase 3
    input_file = os.path.join(project_root, "Phase_3_LLM_Processing", "data", "llm_output.json")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        llm_data = json.load(f)
        
    print("Formatting LLM data into HTML...")
    html_content = generate_email_html(llm_data, recipient_name=recipient_name)
    
    # Save the HTML for debugging/review
    output_dir = os.path.join(current_dir, "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    html_file = os.path.join(output_dir, "email_draft.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved email draft preview to {html_file}")
    
    print(f"Sending email from {sender_email} to {recipient_email}...")
    send_email(sender_email, sender_password, recipient_email, recipient_name, html_content)


if __name__ == "__main__":
    main()
