from deslib.validation import require_bytes, require_uint

DEFAULT_FIXED = 0x12695BC9B7B7F8


def validate_bits(unknown_bits: int) -> None:
    if not isinstance(unknown_bits, int) or not 1 <= unknown_bits <= 24:
        raise ValueError("unknown_bits debe estar entre 1 y 24.")


def effective_to_key(effective: int) -> bytes:
    """Inserta un bit de paridad impar después de cada grupo de 7 bits."""
    require_uint(effective, 56, "effective")
    result = bytearray()
    for group_index in range(8):
        group = (effective >> (49 - 7 * group_index)) & 0x7F
        parity = 1 if group.bit_count() % 2 == 0 else 0
        result.append((group << 1) | parity)
    return bytes(result)


def key_to_effective(key: bytes) -> int:
    """Quita la paridad conservando el orden original; no aplica PC-1."""
    require_bytes(key, "key", 8)
    result = 0
    for byte in key:
        result = (result << 7) | (byte >> 1)
    return result


def candidate_to_key(
    candidate: int, unknown_bits: int = 16, fixed_effective: int = DEFAULT_FIXED
) -> bytes:
    validate_bits(unknown_bits)
    require_uint(candidate, unknown_bits, "candidate")
    require_uint(fixed_effective, 56, "fixed_effective")
    variable_mask = (1 << unknown_bits) - 1
    effective = (fixed_effective & ~variable_mask) | candidate
    return effective_to_key(effective)
