# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:\DEV\Cryptonote
# SHA256: placeholder
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import unittest
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.storage import StorageManager
from src.models import Note

class TestStorageManager(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.enc')
        self.temp_file.close()
        self.storage = StorageManager(self.temp_file.name)
        self.test_password = "test_password"

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_create_and_load(self):
        self.storage.create_new(self.test_password)
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 0)

        storage2 = StorageManager(self.temp_file.name)
        storage2.load(self.test_password)
        notes2 = storage2.list_notes()
        self.assertEqual(len(notes2), 0)

    def test_add_and_list_notes(self):
        self.storage.create_new(self.test_password)
        
        note1 = Note(title="Note 1", content="Content 1")
        note2 = Note(title="Note 2", content="Content 2")
        
        self.storage.add_note(note1)
        self.storage.add_note(note2)
        
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes[0].title, "Note 1")

if __name__ == '__main__':
    unittest.main()