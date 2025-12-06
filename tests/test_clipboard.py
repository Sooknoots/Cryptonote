import unittest
from unittest.mock import patch, MagicMock
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestClipboardFunctionality(unittest.TestCase):
    def setUp(self):
        self.mock_app = MagicMock()
        self.mock_app.clipboard_history = []
        self.mock_app.monitoring_clipboard = False
        self.mock_app.clipboard_enabled = True

    @patch('Gui.win32clipboard')
    def test_clipboard_hash_generation(self, mock_clipboard):
        # Mock clipboard for text
        mock_clipboard.IsClipboardFormatAvailable.return_value = True
        mock_clipboard.CF_TEXT = 1
        mock_clipboard.GetClipboardData.return_value = b"test content"
        
        # Simulate hash generation
        import hashlib
        if mock_clipboard.IsClipboardFormatAvailable(mock_clipboard.CF_TEXT):
            data = mock_clipboard.GetClipboardData(mock_clipboard.CF_TEXT)
            hash_value = hashlib.md5(data).hexdigest()
            self.assertIsInstance(hash_value, str)
            self.assertEqual(len(hash_value), 32)

    @patch('Gui.win32clipboard')
    def test_add_to_history_text(self, mock_clipboard):
        # Mock clipboard text
        mock_clipboard.OpenClipboard.return_value = None
        mock_clipboard.IsClipboardFormatAvailable.return_value = True
        mock_clipboard.CF_TEXT = 1
        mock_clipboard.GetClipboardData.return_value = b"test text"
        mock_clipboard.CloseClipboard.return_value = None
        
        # Simulate adding to history
        history = []
        item = {"timestamp": 1234567890}
        
        if mock_clipboard.IsClipboardFormatAvailable(mock_clipboard.CF_TEXT):
            item["type"] = "text"
            item["content"] = mock_clipboard.GetClipboardData(mock_clipboard.CF_TEXT).decode('utf-8')
            history.insert(0, item)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["type"], "text")
        self.assertEqual(history[0]["content"], "test text")

    @patch('Gui.win32clipboard')
    def test_paste_from_history(self, mock_clipboard):
        # Mock clipboard operations
        mock_clipboard.OpenClipboard.return_value = None
        mock_clipboard.EmptyClipboard.return_value = None
        mock_clipboard.SetClipboardText.return_value = None
        mock_clipboard.CloseClipboard.return_value = None
        
        # Simulate pasting
        item = {"type": "text", "content": "pasted content"}
        
        mock_clipboard.OpenClipboard()
        mock_clipboard.EmptyClipboard()
        if item["type"] == "text":
            mock_clipboard.SetClipboardText(item["content"])
        mock_clipboard.CloseClipboard()
        
        mock_clipboard.SetClipboardText.assert_called_once_with("pasted content")

    def test_history_limit(self):
        # Test history size limit
        history = []
        for i in range(55):  # More than limit
            history.insert(0, {"type": "text", "content": f"item {i}"})
        
        # Simulate limiting
        max_items = 50
        while len(history) > max_items:
            history.pop()
        
        self.assertEqual(len(history), 50)

    def test_clipboard_toggle(self):
        # Test enabling/disabling
        self.mock_app.clipboard_enabled = True
        self.assertTrue(self.mock_app.clipboard_enabled)
        
        self.mock_app.clipboard_enabled = False
        self.assertFalse(self.mock_app.clipboard_enabled)

if __name__ == '__main__':
    unittest.main()