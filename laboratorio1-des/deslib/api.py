from .des_core import des_block
from .key_schedule import des_check_parity, des_key_schedule
from .validation import require_bytes


def des_encrypt_block(key: bytes, plaintext: bytes) -> bytes:
    require_bytes(plaintext, "plaintext", 8)
    subkeys = des_key_schedule(key)
    encrypted = des_block(int.from_bytes(plaintext, "big"), subkeys)
    return encrypted.to_bytes(8, "big")


def des_decrypt_block(key: bytes, ciphertext: bytes) -> bytes:
    require_bytes(ciphertext, "ciphertext", 8)
    subkeys = des_key_schedule(key)
    decrypted = des_block(int.from_bytes(ciphertext, "big"), subkeys[::-1])
    return decrypted.to_bytes(8, "big")
