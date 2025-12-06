import unittest
import os
import tempfile
from src.crypto import CryptoManager

class TestCryptoManager(unittest.TestCase):
    def setUp(self):
        self.crypto = CryptoManager()
        self.test_password = "test_password"
        self.test_data = b"Hello, World!"

    def test_encrypt_decrypt(self):
        # Test encryption and decryption
        encrypted = self.crypto.encrypt(self.test_data, self.test_password)
        decrypted = self.crypto.decrypt(encrypted, self.test_password)
        self.assertEqual(decrypted, self.test_data)

    def test_wrong_password(self):
        # Test decryption with wrong password
        encrypted = self.crypto.encrypt(self.test_data, self.test_password)
        with self.assertRaises(Exception):
            self.crypto.decrypt(encrypted, "wrong_password")

    def test_different_passwords_same_data(self):
        # Test that different passwords produce different encrypted data
        encrypted1 = self.crypto.encrypt(self.test_data, self.test_password)
        encrypted2 = self.crypto.encrypt(self.test_data, "different_password")
        self.assertNotEqual(encrypted1, encrypted2)

if __name__ == '__main__':
    unittest.main()