import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
from email_drafter import generate_email_html, send_email

class TestEmailDrafter(unittest.TestCase):

    def test_generate_email_html(self):
        llm_data = {
            "top_themes": [{"theme": "Test Theme", "description": "Test Desc"}],
            "user_quotes": [{"theme": "Test Theme", "quote": "Test Quote"}],
            "action_ideas": [{"idea": "Test Action", "justification": "Test Justification"}]
        }
        recipient_name = "John Doe"
        
        html = generate_email_html(llm_data, recipient_name)
        
        # Verify the structure and data are present
        self.assertIn("Hi, John Doe", html)
        self.assertIn("Test Theme", html)
        self.assertIn("Test Desc", html)
        self.assertIn("Test Action", html)
        self.assertIn("Test Justification", html)
        self.assertTrue(html.strip().startswith("<html>"))

    @patch('email_drafter.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Setup mock STMP Server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        sender = "test@example.com"
        pwd = "password123"
        recipient = "recipient@example.com"
        name = "Jane"
        html = "<html><body>Test</body></html>"
        
        result = send_email(sender, pwd, recipient, name, html)
        
        self.assertTrue(result)
        mock_smtp.assert_called_with('smtp.gmail.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_with(sender, pwd)
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
        
    @patch('email_drafter.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        # Setup mock STMP Server to raise an exception
        mock_smtp.side_effect = Exception("Connection Refused")
        
        sender = "test@example.com"
        pwd = "password123"
        recipient = "recipient@example.com"
        name = "Jane"
        html = "<html><body>Test</body></html>"
        
        result = send_email(sender, pwd, recipient, name, html)
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
