from .gf import xtime
from .tables import S_BOX


def rot_word(word):
    return word[1:] + word[:1]


def sub_word(word):
    return [S_BOX[value] for value in word]


def expand_key(key):
    if not isinstance(key, bytes):
        raise TypeError('La clave debe ser bytes.')
    if len(key) not in (16, 24, 32):
        raise ValueError('La clave AES debe tener 16, 24 o 32 bytes.')

    nk = len(key) // 4
    rounds = nk + 6
    words = [list(key[i:i + 4]) for i in range(0, len(key), 4)]
    rcon = 1

    for i in range(nk, 4 * (rounds + 1)):
        temp = words[i - 1].copy()
        if i % nk == 0:
            temp = sub_word(rot_word(temp))
            temp[0] ^= rcon
            rcon = xtime(rcon)
        elif nk == 8 and i % nk == 4:
            temp = sub_word(temp)
        new_word = [words[i - nk][j] ^ temp[j] for j in range(4)]
        words.append(new_word)

    round_keys = []
    for start in range(0, len(words), 4):
        joined = []
        for word in words[start:start + 4]:
            joined.extend(word)
        round_keys.append(tuple(joined))
    return tuple(round_keys)
