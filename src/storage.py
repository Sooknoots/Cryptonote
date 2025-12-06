import json
import os
from typing import List, Dict
from .models import Note
from .crypto import CryptoManager

class StorageManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.crypto = CryptoManager()
        self.notes: Dict[str, Note] = {}
        self.is_open = False

    def create_new(self, password: str):
        """Creates a new empty encrypted database."""
        self.notes = {}
        self.save(password)
        self.is_open = True

    def load(self, password: str):
        """Loads and decrypts the database."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError("Database file not found.")
        
        with open(self.filepath, 'r') as f:
            encrypted_blob = f.read()
        
        decrypted_bytes = self.crypto.decrypt(encrypted_blob, password)
        data = json.loads(decrypted_bytes.decode('utf-8'))
        
        self.notes = {n['id']: Note.from_dict(n) for n in data}
        self.is_open = True

    def save(self, password: str):
        """Encrypts and saves the current database."""
        data = [note.to_dict() for note in self.notes.values()]
        json_bytes = json.dumps(data).encode('utf-8')
        encrypted_blob = self.crypto.encrypt(json_bytes, password)
        
        with open(self.filepath, 'w') as f:
            f.write(encrypted_blob)

    def add_note(self, note: Note):
        self.notes[note.id] = note

    def get_note(self, note_id: str) -> Note:
        return self.notes.get(note_id)

    def list_notes(self) -> List[Note]:
        return list(self.notes.values())

    def delete_note(self, note_id: str):
        if note_id in self.notes:
            del self.notes[note_id]

    def import_library(self, import_filepath: str, import_password: str):
        """Imports notes from another encrypted file."""
        temp_storage = StorageManager(import_filepath)
        temp_storage.load(import_password)
        
        # Merge notes (simple merge: add all, overwrite if ID exists)
        for note in temp_storage.list_notes():
            self.notes[note.id] = note

    def export_library(self, export_filepath: str, export_password: str):
        """Exports current library to a new encrypted file."""
        # Create a temporary storage object to save to the new path
        temp_storage = StorageManager(export_filepath)
        temp_storage.notes = self.notes.copy()
        temp_storage.save(export_password)
