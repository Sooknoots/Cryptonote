# SECURITY MARKER: This file has been validated for safe public release
# Validation Date: Cryptonote Security System @ F:\DEV\Cryptonote
# SHA256: placeholder
# NEVER REMOVE THIS MARKER - Indicates file passed security validation

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.crypto import CryptoManager

class TestCryptoManager(unittest.TestCase):
    def setUp(self):
        self.crypto = CryptoManager()
        self.test_password = "test_password"
        self.test_data = b"Hello, World!"

    def test_encrypt_decrypt(self):
        encrypted = self.crypto.encrypt(self.test_data, self.test_password)
        decrypted = self.crypto.decrypt(encrypted, self.test_password)
        self.assertEqual(decrypted, self.test_data)

    def test_wrong_password(self):
        encrypted = self.crypto.encrypt(self.test_data, self.test_password)
        with self.assertRaises(Exception):
            self.crypto.decrypt(encrypted, "wrong_password")

if __name__ == '__main__':
    unittest.main()