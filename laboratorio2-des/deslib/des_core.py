from .feistel import des_round
from .permutation import permute
from .tables import IP, IP_INVERSE
from .validation import require_uint


def des_block(block: int, subkeys: list[int]) -> int:
    require_uint(block, 64, "block")
    if len(subkeys) != 16:
        raise ValueError("DES necesita exactamente 16 subclaves.")
    state = permute(block, IP, 64)
    left, right = state >> 32, state & 0xFFFFFFFF
    for subkey in subkeys:
        left, right = des_round(left, right, subkey)
    return permute((right << 32) | left, IP_INVERSE, 64)
