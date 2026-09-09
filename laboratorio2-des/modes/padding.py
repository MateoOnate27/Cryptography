from deslib.validation import require_bytes


def _validate(data: bytes, block_size: int) -> None:
    require_bytes(data, "data")
    if not isinstance(block_size, int) or not 1 <= block_size <= 255:
        raise ValueError("block_size debe estar entre 1 y 255.")


def pkcs7_pad(data: bytes, block_size: int = 8) -> bytes:
    _validate(data, block_size)
    count = block_size - len(data) % block_size
    return data + bytes([count]) * count


def pkcs7_unpad(data: bytes, block_size: int = 8) -> bytes:
    _validate(data, block_size)
    if not data or len(data) % block_size != 0:
        raise ValueError("El texto con padding debe contener bloques completos.")
    count = data[-1]
    if not 1 <= count <= block_size:
        raise ValueError("Longitud de padding inválida.")
    if data[-count:] != bytes([count]) * count:
        raise ValueError("Los bytes de padding no coinciden.")
    return data[:-count]
