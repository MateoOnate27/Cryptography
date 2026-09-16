from .tables import S_BOX, INV_S_BOX, MUL2, MUL3, MUL9, MUL11, MUL13, MUL14


def sub_bytes(state):
    for i in range(16):
        state[i] = S_BOX[state[i]]


def inv_sub_bytes(state):
    for i in range(16):
        state[i] = INV_S_BOX[state[i]]


def shift_rows(state):
    state[1], state[5], state[9], state[13] = state[5], state[9], state[13], state[1]
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    state[3], state[7], state[11], state[15] = state[15], state[3], state[7], state[11]


def inv_shift_rows(state):
    state[1], state[5], state[9], state[13] = state[13], state[1], state[5], state[9]
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    state[3], state[7], state[11], state[15] = state[7], state[11], state[15], state[3]


def mix_columns(state):
    for start in range(0, 16, 4):
        a, b, c, d = state[start:start + 4]
        state[start] = MUL2[a] ^ MUL3[b] ^ c ^ d
        state[start + 1] = a ^ MUL2[b] ^ MUL3[c] ^ d
        state[start + 2] = a ^ b ^ MUL2[c] ^ MUL3[d]
        state[start + 3] = MUL3[a] ^ b ^ c ^ MUL2[d]


def inv_mix_columns(state):
    for start in range(0, 16, 4):
        a, b, c, d = state[start:start + 4]
        state[start] = MUL14[a] ^ MUL11[b] ^ MUL13[c] ^ MUL9[d]
        state[start + 1] = MUL9[a] ^ MUL14[b] ^ MUL11[c] ^ MUL13[d]
        state[start + 2] = MUL13[a] ^ MUL9[b] ^ MUL14[c] ^ MUL11[d]
        state[start + 3] = MUL11[a] ^ MUL13[b] ^ MUL9[c] ^ MUL14[d]


def add_round_key(state, round_key):
    for i in range(16):
        state[i] ^= round_key[i]
