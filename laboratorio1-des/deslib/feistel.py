from .permutation import permute
from .sboxes import substitute
from .tables import E, P
from .validation import require_uint


def feistel_f(right: int, subkey: int) -> int:
    require_uint(right, 32, "right")
    require_uint(subkey, 48, "subkey")
    expanded = permute(right, E, 32)
    mixed = expanded ^ subkey
    return permute(substitute(mixed), P, 32)


def des_round(left: int, right: int, subkey: int) -> tuple[int, int]:
    require_uint(left, 32, "left")
    return right, left ^ feistel_f(right, subkey)
