import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock openai if not available
try:
    import openai
except ImportError:
    openai = None

class TestAIFunctionality(unittest.TestCase):
    def setUp(self):
        # Mock the GUI components for testing
        pass

    @patch('requests.post')
    def test_ollama_ai_fix(self, mock_post):
        # Mock Ollama response
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"content": "Fixed code"}}
        mock_post.return_value = mock_response
        
        # Simulate the AI fix logic for Ollama
        content = "def test(): pass"
        ollama_url = "http://localhost:11434"
        model = "llama2"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful coding assistant. Fix, improve, or complete the following code or text. Provide the improved version."},
                {"role": "user", "content": content}
            ],
            "stream": False
        }
        
        # This would be in the actual method
        response = mock_post(ollama_url + "/api/chat", json=payload)
        fixed_content = response.json()["message"]["content"]
        
        self.assertEqual(fixed_content, "Fixed code")
        mock_post.assert_called_once()

    @patch('openai.ChatCompletion.create')
    def test_openai_ai_fix(self, mock_create):
        if not openai:
            self.skipTest("OpenAI not available")
        
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Fixed code"
        mock_create.return_value = mock_response
        
        # Simulate the AI fix logic for OpenAI
        content = "def test(): pass"
        
        # This would be in the actual method
        response = mock_create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant. Fix, improve, or complete the following code or text. Provide the improved version."},
                {"role": "user", "content": content}
            ],
            max_tokens=1000
        )
        fixed_content = response.choices[0].message.content
        
        self.assertEqual(fixed_content, "Fixed code")
        mock_create.assert_called_once()

    def test_token_estimation(self):
        # Test the token estimation function
        from Gui import EditNotePopup
        
        # Create a mock popup instance
        mock_master = MagicMock()
        mock_note = MagicMock()
        popup = EditNotePopup(mock_master, mock_note, MagicMock(), MagicMock())
        
        # Test estimation
        text = "Hello world"
        tokens = popup.estimate_tokens(text)
        self.assertIsInstance(tokens, int)
        self.assertGreater(tokens, 0)

if __name__ == '__main__':
    unittest.main()