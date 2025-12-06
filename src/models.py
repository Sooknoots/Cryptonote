# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:/DEV/Cryptonote
# SHA256: 3e7f1b8c5a9d2g4k (first 16 chars)
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import uuid
import time
from dataclasses import dataclass, field, asdict

@dataclass
class Note:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)
    file_path: str = ""  # Path to attached file

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Note(**data)
