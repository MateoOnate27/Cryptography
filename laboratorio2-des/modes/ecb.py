from deslib import des_decrypt_block, des_encrypt_block
from deslib.validation import require_bytes
from .padding import pkcs7_pad, pkcs7_unpad


def validate_ciphertext(ciphertext: bytes) -> None:
    require_bytes(ciphertext, "ciphertext")
    if not ciphertext or len(ciphertext) % 8 != 0:
        raise ValueError("El ciphertext debe ser no vacío y múltiplo de 8 bytes.")


def des_ecb_encrypt(key: bytes, plaintext: bytes) -> bytes:
    require_bytes(key, "key", 8)
    padded = pkcs7_pad(plaintext)
    blocks = []
    for offset in range(0, len(padded), 8):
        blocks.append(des_encrypt_block(key, padded[offset:offset + 8]))
    return b"".join(blocks)


def des_ecb_decrypt(key: bytes, ciphertext: bytes) -> bytes:
    require_bytes(key, "key", 8)
    validate_ciphertext(ciphertext)
    blocks = []
    for offset in range(0, len(ciphertext), 8):
        blocks.append(des_decrypt_block(key, ciphertext[offset:offset + 8]))
    return pkcs7_unpad(b"".join(blocks))
