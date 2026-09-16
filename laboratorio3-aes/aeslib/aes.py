from .key_schedule import expand_key
from .transformations import (
    sub_bytes, inv_sub_bytes, shift_rows, inv_shift_rows,
    mix_columns, inv_mix_columns, add_round_key,
)


class AES:
    def __init__(self, key):
        self.round_keys = expand_key(key)
        self.rounds = len(self.round_keys) - 1
        self.key_bits = len(key) * 8

    @staticmethod
    def _check_block(block):
        if not isinstance(block, bytes):
            raise TypeError('El bloque debe ser bytes.')
        if len(block) != 16:
            raise ValueError('El bloque AES debe tener exactamente 16 bytes.')

    def encrypt_block(self, plaintext):
        self._check_block(plaintext)
        state = list(plaintext)
        add_round_key(state, self.round_keys[0])
        for number in range(1, self.rounds):
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, self.round_keys[number])
        sub_bytes(state)
        shift_rows(state)
        add_round_key(state, self.round_keys[-1])
        return bytes(state)

    def decrypt_block(self, ciphertext):
        self._check_block(ciphertext)
        state = list(ciphertext)
        add_round_key(state, self.round_keys[-1])
        for number in range(self.rounds - 1, 0, -1):
            inv_shift_rows(state)
            inv_sub_bytes(state)
            add_round_key(state, self.round_keys[number])
            inv_mix_columns(state)
        inv_shift_rows(state)
        inv_sub_bytes(state)
        add_round_key(state, self.round_keys[0])
        return bytes(state)

    @staticmethod
    def _check_data(data):
        if not isinstance(data, bytes):
            raise TypeError('Los datos deben ser bytes.')
        if len(data) % 16:
            raise ValueError('La longitud debe ser múltiplo de 16. No se añade padding.')

    def encrypt_blocks(self, data):
        self._check_data(data)
        output = bytearray(len(data))
        for start in range(0, len(data), 16):
            output[start:start + 16] = self.encrypt_block(data[start:start + 16])
        return bytes(output)

    def decrypt_blocks(self, data):
        self._check_data(data)
        output = bytearray(len(data))
        for start in range(0, len(data), 16):
            output[start:start + 16] = self.decrypt_block(data[start:start + 16])
        return bytes(output)
