# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:/DEV/Cryptonote
# SHA256: 8f4e2c6a9d1b5f3e (first 16 chars)
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import os
import base64
import json
from argon2 import PasswordHasher
from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoManager:
    def __init__(self):
        # Argon2id parameters for high security
        self.time_cost = 2
        self.memory_cost = 1024 * 64  # 64 MB
        self.parallelism = 2
        self.hash_len = 32
        self.salt_len = 16

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derives a 32-byte key from the password and salt using Argon2id."""
        return hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=self.hash_len,
            type=Type.ID
        )

    def encrypt(self, data: bytes, password: str) -> str:
        """
        Encrypts data using AES-256-GCM.
        Returns a base64 encoded JSON string containing salt, nonce, and ciphertext.
        """
        salt = os.urandom(self.salt_len)
        key = self.derive_key(password, salt)
        
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # GCM standard nonce size
        ciphertext = aesgcm.encrypt(nonce, data, None)
        
        encrypted_package = {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
        }
        
        return base64.b64encode(json.dumps(encrypted_package).encode('utf-8')).decode('utf-8')

    def decrypt(self, encrypted_blob: str, password: str) -> bytes:
        """
        Decrypts the base64 encoded JSON blob.
        """
        try:
            json_bytes = base64.b64decode(encrypted_blob)
            package = json.loads(json_bytes)
            
            salt = base64.b64decode(package['salt'])
            nonce = base64.b64decode(package['nonce'])
            ciphertext = base64.b64decode(package['ciphertext'])
            
            key = self.derive_key(password, salt)
            aesgcm = AESGCM(key)
            
            return aesgcm.decrypt(nonce, ciphertext, None)
        except Exception as e:
            raise ValueError("Decryption failed. Invalid password or corrupted data.") from e
