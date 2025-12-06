import unittest
import os
import tempfile
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
        # Test creating new storage
        self.storage.create_new(self.test_password)
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 0)

        # Test loading
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
        self.assertEqual(notes[1].title, "Note 2")

    def test_update_note(self):
        self.storage.create_new(self.test_password)
        
        note = Note(title="Original", content="Original content")
        self.storage.add_note(note)
        
        note.title = "Updated"
        note.content = "Updated content"
        self.storage.update_note(note)
        
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Updated")
        self.assertEqual(notes[0].content, "Updated content")

    def test_delete_note(self):
        self.storage.create_new(self.test_password)
        
        note = Note(title="Test", content="Content")
        self.storage.add_note(note)
        
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 1)
        
        self.storage.delete_note(note.id)
        notes = self.storage.list_notes()
        self.assertEqual(len(notes), 0)

    def test_save_and_load_with_notes(self):
        self.storage.create_new(self.test_password)
        
        note = Note(title="Persistent", content="Persistent content")
        self.storage.add_note(note)
        self.storage.save(self.test_password)
        
        # Load in new instance
        storage2 = StorageManager(self.temp_file.name)
        storage2.load(self.test_password)
        notes = storage2.list_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Persistent")

    def test_wrong_password_load(self):
        self.storage.create_new(self.test_password)
        self.storage.save(self.test_password)
        
        storage2 = StorageManager(self.temp_file.name)
        with self.assertRaises(Exception):
            storage2.load("wrong_password")

if __name__ == '__main__':
    unittest.main()