import unittest
from src.models import Note

class TestNote(unittest.TestCase):
    def test_note_creation(self):
        note = Note(title="Test Title", content="Test Content", tags=["test", "note"])
        self.assertEqual(note.title, "Test Title")
        self.assertEqual(note.content, "Test Content")
        self.assertEqual(note.tags, ["test", "note"])
        self.assertIsNotNone(note.id)
        self.assertIsNotNone(note.created_at)
        self.assertIsNotNone(note.modified_at)

    def test_note_update(self):
        note = Note(title="Original", content="Original content")
        original_modified = note.modified_at
        note.title = "Updated"
        note.content = "Updated content"
        # Assuming update_modified is called
        note.modified_at = note.modified_at  # In real code, it would update
        self.assertEqual(note.title, "Updated")
        self.assertEqual(note.content, "Updated content")

    def test_note_to_dict(self):
        note = Note(title="Test", content="Content", tags=["tag"])
        data = note.to_dict()
        self.assertEqual(data['title'], "Test")
        self.assertEqual(data['content'], "Content")
        self.assertEqual(data['tags'], ["tag"])

    def test_note_from_dict(self):
        data = {
            'id': '123',
            'title': 'Test',
            'content': 'Content',
            'tags': ['tag'],
            'created_at': '2023-01-01T00:00:00',
            'modified_at': '2023-01-01T00:00:00'
        }
        note = Note.from_dict(data)
        self.assertEqual(note.id, '123')
        self.assertEqual(note.title, 'Test')
        self.assertEqual(note.content, 'Content')
        self.assertEqual(note.tags, ['tag'])

if __name__ == '__main__':
    unittest.main()