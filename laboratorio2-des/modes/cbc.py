from deslib import des_decrypt_block, des_encrypt_block
from deslib.validation import require_bytes
from .ecb import validate_ciphertext
from .padding import pkcs7_pad, pkcs7_unpad


def xor_blocks(first: bytes, second: bytes) -> bytes:
    require_bytes(first, "first", 8)
    require_bytes(second, "second", 8)
    return bytes(a ^ b for a, b in zip(first, second))


def des_cbc_encrypt(key: bytes, plaintext: bytes, iv: bytes) -> bytes:
    require_bytes(key, "key", 8)
    require_bytes(iv, "iv", 8)
    padded = pkcs7_pad(plaintext)
    previous = iv
    blocks = []
    for offset in range(0, len(padded), 8):
        block = padded[offset:offset + 8]
        encrypted = des_encrypt_block(key, xor_blocks(block, previous))
        blocks.append(encrypted)
        previous = encrypted
    return b"".join(blocks)


def des_cbc_decrypt(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    require_bytes(key, "key", 8)
    require_bytes(iv, "iv", 8)
    validate_ciphertext(ciphertext)
    previous = iv
    blocks = []
    for offset in range(0, len(ciphertext), 8):
        block = ciphertext[offset:offset + 8]
        blocks.append(xor_blocks(des_decrypt_block(key, block), previous))
        previous = block
    return pkcs7_unpad(b"".join(blocks))
