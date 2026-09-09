from .tables import SBOXES
from .validation import require_uint


def sbox_lookup(box: int, six_bits: int) -> int:
    """box se numera de 0 a 7; por ejemplo, box=0 selecciona S1."""
    require_uint(box, 3, "box")
    require_uint(six_bits, 6, "six_bits")
    first_bit = six_bits >> 5
    last_bit = six_bits & 1
    row = (first_bit << 1) | last_bit
    column = (six_bits >> 1) & 0b1111
    return SBOXES[box][row][column]


def substitute(value48: int) -> int:
    require_uint(value48, 48, "value48")
    result = 0
    for box in range(8):
        group = (value48 >> (42 - 6 * box)) & 0b111111
        result = (result << 4) | sbox_lookup(box, group)
    return result
