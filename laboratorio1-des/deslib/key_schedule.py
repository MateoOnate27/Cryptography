from .permutation import permute
from .tables import PC1, PC2, ROTATIONS
from .validation import require_bytes, require_uint

MASK28 = (1 << 28) - 1


def rotate_left28(value: int, amount: int) -> int:
    require_uint(value, 28, "value")
    if not isinstance(amount, int) or amount < 0:
        raise ValueError("La rotación debe ser un entero no negativo.")
    amount %= 28
    shifted = value << amount
    wrapped = value >> (28 - amount)
    return (shifted | wrapped) & MASK28


def des_check_parity(key: bytes) -> bool:
    require_bytes(key, "key", 8)
    for byte in key:
        if byte.bit_count() % 2 != 1:
            return False
    return True


def des_key_schedule(key: bytes) -> list[int]:
    require_bytes(key, "key", 8)
    effective_key = permute(int.from_bytes(key, "big"), PC1, 64)
    left = effective_key >> 28
    right = effective_key & MASK28
    subkeys = []
    for amount in ROTATIONS:
        left = rotate_left28(left, amount)
        right = rotate_left28(right, amount)
        joined = (left << 28) | right
        subkey = permute(joined, PC2, 56)
        subkeys.append(subkey)
    return subkeys
