# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:\DEV\Cryptonote
# SHA256: placeholder
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock openai if not available
try:
    import openai
except ImportError:
    openai = None

class TestAITokenVerification(unittest.TestCase):
    def setUp(self):
        # Mock the GUI components
        self.mock_master = MagicMock()
        self.mock_master.token_balance = 5
        self.mock_master.total_tokens_used = 0
        self.mock_master.save_config = MagicMock()
        self.mock_master.record_tps_stats = MagicMock()
        
        # Mock the popup
        self.popup = Mock()
        self.popup.master = self.mock_master
        self.popup.estimate_tokens = Mock(return_value=10)
        self.popup.after = Mock()
        
        # Import after mocking
        from Gui import EditNotePopup
        self.popup_class = EditNotePopup
        # Bind methods to mock instance
        self.popup._fix_with_openai = self.popup_class._fix_with_openai.__get__(self.popup, self.popup_class)
        self.popup._fix_with_ollama = self.popup_class._fix_with_ollama.__get__(self.popup, self.popup_class)

    @patch('openai.ChatCompletion.create')
    def test_openai_success_deducts_token(self, mock_create):
        # Mock successful OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Fixed code"
        mock_response.usage.total_tokens = 20
        mock_create.return_value = mock_response
        
        initial_balance = self.mock_master.token_balance
        content = "def test(): pass"
        
        result = self.popup._fix_with_openai(content)
        
        self.assertEqual(result, "Fixed code")
        self.assertEqual(self.mock_master.token_balance, initial_balance - 1)
        self.assertEqual(self.mock_master.total_tokens_used, 20)
        self.mock_master.save_config.assert_called()

    @patch('openai.ChatCompletion.create')
    def test_openai_empty_response_no_deduct(self, mock_create):
        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""
        mock_create.return_value = mock_response
        
        initial_balance = self.mock_master.token_balance
        content = "def test(): pass"
        
        with self.assertRaises(ValueError):
            self.popup._fix_with_openai(content)
        
        # Token not deducted
        self.assertEqual(self.mock_master.token_balance, initial_balance)
        self.mock_master.save_config.assert_not_called()

    @patch('openai.ChatCompletion.create')
    def test_openai_exception_no_deduct(self, mock_create):
        # Mock exception
        mock_create.side_effect = Exception("API Error")
        
        initial_balance = self.mock_master.token_balance
        content = "def test(): pass"
        
        with self.assertRaises(Exception):
            self.popup._fix_with_openai(content)
        
        # Token not deducted
        self.assertEqual(self.mock_master.token_balance, initial_balance)
        self.mock_master.save_config.assert_not_called()

    @patch('Gui.requests.post')
    def test_ollama_success_no_deduct(self, mock_post):
        # Mock successful Ollama response
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"content": "Fixed code"}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        initial_balance = self.mock_master.token_balance
        content = "def test(): pass"
        
        result = self.popup._fix_with_ollama(content)
        
        self.assertEqual(result, "Fixed code")
        # No token deduction for Ollama
        self.assertEqual(self.mock_master.token_balance, initial_balance)
        self.assertEqual(self.mock_master.total_tokens_used, 10)  # estimated
        self.mock_master.save_config.assert_called()

    @patch('Gui.requests.post')
    def test_ollama_empty_response_error(self, mock_post):
        # Mock empty response
        mock_response = MagicMock()
        mock_response.json.return_value = {"message": {"content": ""}}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        content = "def test(): pass"
        
        with self.assertRaises(ValueError):
            self.popup._fix_with_ollama(content)

if __name__ == '__main__':
    unittest.main()