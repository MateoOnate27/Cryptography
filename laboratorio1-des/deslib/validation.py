def require_bytes(value: bytes, name: str, length: int | None = None) -> None:
    if not isinstance(value, bytes):
        raise TypeError(f"{name} debe ser bytes.")
    if length is not None and len(value) != length:
        raise ValueError(f"{name} debe contener exactamente {length} bytes.")


def require_uint(value: int, width: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} debe ser un entero.")
    if not 0 <= value < (1 << width):
        raise ValueError(f"{name} debe caber en {width} bits sin signo.")
