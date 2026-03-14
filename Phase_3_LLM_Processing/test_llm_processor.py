import os
import json
import unittest
from unittest.mock import patch, MagicMock
from llm_processor import process_reviews_with_llm

class TestLLMProcessor(unittest.TestCase):

    @patch('llm_processor.Groq')
    @patch('llm_processor.os.getenv')
    def test_process_reviews_valid_json(self, mock_getenv, mock_groq):
        # Setup mock environment variable
        mock_getenv.return_value = "fake_api_key"
        
        # Setup mock Groq client and response
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_completion = MagicMock()
        expected_json_string = '''
        {
            "top_themes": [{"theme": "Test Theme", "description": "Test Desc"}],
            "user_quotes": [{"theme": "Test Theme", "quote": "Test Quote"}],
            "action_ideas": [{"idea": "Test Action", "justification": "Test Justification"}]
        }
        '''
        mock_completion.choices[0].message.content = expected_json_string
        mock_client.chat.completions.create.return_value = mock_completion
        
        # Test input data
        test_reviews = [
            {"rating": 5, "text": "Great app!"},
            {"rating": 1, "text": "Terrible app!"}
        ]
        
        # Execute function
        result = process_reviews_with_llm(test_reviews)
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn("top_themes", result)
        self.assertIn("user_quotes", result)
        self.assertIn("action_ideas", result)
        self.assertEqual(len(result["top_themes"]), 1)
        self.assertEqual(result["top_themes"][0]["theme"], "Test Theme")

    @patch('llm_processor.os.getenv')
    def test_missing_api_key(self, mock_getenv):
        # Setup missing api key
        mock_getenv.return_value = None
        
        test_reviews = [{"rating": 5, "text": "Great app!"}]
        
        # Execute and Assert
        with self.assertRaises(ValueError):
            process_reviews_with_llm(test_reviews)

if __name__ == '__main__':
    unittest.main()
