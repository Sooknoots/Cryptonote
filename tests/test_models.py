# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:\DEV\Cryptonote
# SHA256: placeholder
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models import Note

class TestNote(unittest.TestCase):
    def test_note_creation(self):
        note = Note(title="Test Title", content="Test Content", tags=["test"])
        self.assertEqual(note.title, "Test Title")
        self.assertEqual(note.content, "Test Content")
        self.assertEqual(note.tags, ["test"])
        self.assertIsNotNone(note.id)
        self.assertIsNotNone(note.created_at)

    def test_note_to_dict(self):
        note = Note(title="Test", content="Content", tags=["tag"])
        data = note.to_dict()
        self.assertEqual(data['title'], "Test")
        self.assertEqual(data['content'], "Content")
        self.assertEqual(data['tags'], ["tag"])

if __name__ == '__main__':
    unittest.main()