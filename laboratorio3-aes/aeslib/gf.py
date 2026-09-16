def xtime(value):
    shifted = value << 1
    if value & 0x80:
        shifted ^= 0x11B
    return shifted & 0xFF


def multiply(a, b):
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        a = xtime(a)
        b >>= 1
    return result
