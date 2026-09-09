import unittest

from deslib import des_encrypt_block
from modes import (des_cbc_decrypt, des_cbc_encrypt, des_ecb_decrypt,
                   des_ecb_encrypt, pkcs7_pad, pkcs7_unpad)
from modes.cbc import xor_blocks

KEY = bytes.fromhex("133457799BBCDFF1")
IV = bytes.fromhex("0123456789ABCDEF")


class PaddingTests(unittest.TestCase):
    def test_example_and_full_block(self):
        self.assertEqual(pkcs7_pad(b"ABCDE"), b"ABCDE\x03\x03\x03")
        self.assertEqual(pkcs7_pad(b"ABCDEFGH"), b"ABCDEFGH" + b"\x08" * 8)
        self.assertEqual(pkcs7_pad(b""), b"\x08" * 8)

    def test_many_lengths(self):
        for length in range(65):
            message = bytes(range(length))
            with self.subTest(length=length):
                self.assertEqual(pkcs7_unpad(pkcs7_pad(message)), message)

    def test_invalid_padding(self):
        cases = [b"", b"ABC", b"ABCDEFG\x00", b"ABCDEFG\x09", b"ABCDEF\x01\x02"]
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                pkcs7_unpad(data)
        for size in (0, 256):
            with self.assertRaises(ValueError):
                pkcs7_pad(b"A", size)


class ModeTests(unittest.TestCase):
    def test_ecb_and_cbc_round_trips(self):
        messages = [b"", b"A", b"ABCDEFGH", b"ABCDEFGH" * 4,
                    "Criptografía en Ecuador".encode("utf-8"), bytes(range(256))]
        for message in messages:
            with self.subTest(length=len(message)):
                self.assertEqual(des_ecb_decrypt(KEY, des_ecb_encrypt(KEY, message)), message)
                self.assertEqual(des_cbc_decrypt(KEY, des_cbc_encrypt(KEY, message, IV), IV), message)

    def test_modes_use_expected_chaining(self):
        message = b"ABCDEFGH" * 2
        cbc = des_cbc_encrypt(KEY, message, IV)
        first = des_encrypt_block(KEY, xor_blocks(message[:8], IV))
        second = des_encrypt_block(KEY, xor_blocks(message[8:], first))
        self.assertEqual(cbc[:16], first + second)
        self.assertEqual(des_ecb_encrypt(KEY, message)[:8], des_encrypt_block(KEY, message[:8]))

    def test_repeated_blocks(self):
        message = b"ABCDEFGH" * 4
        ecb = des_ecb_encrypt(KEY, message)
        cbc = des_cbc_encrypt(KEY, message, IV)
        self.assertEqual(len({ecb[i:i+8] for i in range(0, 32, 8)}), 1)
        self.assertEqual(len({cbc[i:i+8] for i in range(0, 32, 8)}), 4)

    def test_different_ivs(self):
        self.assertNotEqual(des_cbc_encrypt(KEY, b"Hola", IV),
                            des_cbc_encrypt(KEY, b"Hola", bytes(8)))

    def test_error_propagation(self):
        message = b"ABCDEFGH" * 4
        for mode in ("ECB", "CBC"):
            encrypted = des_ecb_encrypt(KEY, message) if mode == "ECB" else des_cbc_encrypt(KEY, message, IV)
            changed = bytearray(encrypted)
            changed[8] ^= 0x80  
            recovered = des_ecb_decrypt(KEY, bytes(changed)) if mode == "ECB" else des_cbc_decrypt(KEY, bytes(changed), IV)
            distances = [(int.from_bytes(message[i:i+8], "big") ^ int.from_bytes(recovered[i:i+8], "big")).bit_count()
                         for i in range(0, 32, 8)]
            self.assertEqual(distances[0], 0)
            self.assertGreater(distances[1], 0)
            self.assertEqual(distances[2], 0 if mode == "ECB" else 1)
            self.assertEqual(distances[3], 0)
            if mode == "CBC":
                self.assertEqual(recovered[16] ^ message[16], 0x80)

    def test_invalid_ciphertext_and_ivs(self):
        for data in (b"", b"A" * 7, b"A" * 9):
            with self.assertRaises(ValueError):
                des_ecb_decrypt(KEY, data)
            with self.assertRaises(ValueError):
                des_cbc_decrypt(KEY, data, IV)
        for length in (0, 7, 9):
            with self.assertRaises(ValueError):
                des_cbc_encrypt(KEY, b"Hola", bytes(length))
            with self.assertRaises(ValueError):
                des_cbc_decrypt(KEY, bytes(8), bytes(length))

    def test_decryption_rejects_malformed_padding(self):
        malformed = b"ABCDEFG\x00"
        with self.assertRaises(ValueError):
            des_ecb_decrypt(KEY, des_encrypt_block(KEY, malformed))
        cbc = des_encrypt_block(KEY, xor_blocks(malformed, IV))
        with self.assertRaises(ValueError):
            des_cbc_decrypt(KEY, cbc, IV)


if __name__ == "__main__":
    unittest.main()
