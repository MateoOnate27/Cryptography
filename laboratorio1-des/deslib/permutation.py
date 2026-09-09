from .validation import require_uint


def permute(value: int, table: tuple[int, ...], input_width: int) -> int:
    """Copia los bits que indica la tabla, en el orden de la tabla."""
    if not isinstance(input_width, int) or input_width < 1:
        raise ValueError("El ancho de entrada debe ser un entero positivo.")
    require_uint(value, input_width, "value")
    result = 0
    for position in table:
        if not 1 <= position <= input_width:
            raise ValueError("La tabla contiene una posición fuera de la entrada.")
        bit = (value >> (input_width - position)) & 1
        result = (result << 1) | bit
    return result
