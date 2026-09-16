import random
import unittest
from aeslib import AES
from aeslib.gf import xtime, multiply
from aeslib.tables import S_BOX, INV_S_BOX, MUL2, MUL3, MUL9, MUL11, MUL13, MUL14
from aeslib.key_schedule import expand_key, rot_word, sub_word
from aeslib.transformations import (
    sub_bytes, inv_sub_bytes, shift_rows, inv_shift_rows,
    mix_columns, inv_mix_columns, add_round_key,
)
from tests.vectors import PLAIN, FIPS_VECTORS, NIST_PLAIN, NIST_VECTORS, KEY_CHECKPOINTS


def polynomial_product(a, b):
    product = 0
    for bit in range(8):
        if b & (1 << bit):
            product ^= a << bit
    for bit in range(14, 7, -1):
        if product & (1 << bit):
            product ^= 0x11B << (bit - 8)
    return product


class FieldTests(unittest.TestCase):
    def test_published_examples(self):
        self.assertEqual(xtime(0x57), 0xAE)
        self.assertEqual(xtime(0xAE), 0x47)
        self.assertEqual(multiply(0x57, 0x13), 0xFE)
        self.assertEqual(multiply(0x57, 0x83), 0xC1)

    def test_all_byte_products(self):
        for a in range(256):
            for b in range(256):
                self.assertEqual(multiply(a, b), polynomial_product(a, b))

    def test_lookup_products(self):
        for factor, table in ((2,MUL2), (3,MUL3), (9,MUL9), (11,MUL11), (13,MUL13), (14,MUL14)):
            for value in range(256):
                self.assertEqual(table[value], polynomial_product(value, factor))

    def test_sbox_from_mathematical_definition(self):
        for value in range(256):
            inverse = 0
            if value:
                inverse = next(candidate for candidate in range(1,256)
                               if polynomial_product(value, candidate) == 1)
            transformed = inverse
            for shift in (1,2,3,4):
                transformed ^= ((inverse << shift) | (inverse >> (8-shift))) & 255
            self.assertEqual(S_BOX[value], transformed ^ 0x63)
            self.assertEqual(INV_S_BOX[S_BOX[value]], value)


class TransformationTests(unittest.TestCase):
    def test_state_layout_and_shift_rows(self):
        state = list(range(16))
        shift_rows(state)
        self.assertEqual(state, [0,5,10,15,4,9,14,3,8,13,2,7,12,1,6,11])
        inv_shift_rows(state)
        self.assertEqual(state, list(range(16)))

    def test_sub_bytes_known_state(self):
        state = list(bytes.fromhex('00102030405060708090a0b0c0d0e0f0'))
        sub_bytes(state)
        self.assertEqual(bytes(state).hex(), '63cab7040953d051cd60e0e7ba70e18c')
        inv_sub_bytes(state)
        self.assertEqual(bytes(state).hex(), '00102030405060708090a0b0c0d0e0f0')

    def test_mix_columns_known_column(self):
        state = [0xDB,0x13,0x53,0x45] * 4
        mix_columns(state)
        self.assertEqual(state, [0x8E,0x4D,0xA1,0xBC] * 4)
        inv_mix_columns(state)
        self.assertEqual(state, [0xDB,0x13,0x53,0x45] * 4)

    def test_fips_first_round(self):
        state = list(PLAIN)
        keys = expand_key(bytes(range(16)))
        add_round_key(state, keys[0])
        self.assertEqual(bytes(state).hex(), '00102030405060708090a0b0c0d0e0f0')
        sub_bytes(state)
        shift_rows(state)
        self.assertEqual(bytes(state).hex(), '6353e08c0960e104cd70b751bacad0e7')
        mix_columns(state)
        self.assertEqual(bytes(state).hex(), '5f72641557f5bc92f7be3b291db9f91a')
        add_round_key(state, keys[1])
        self.assertEqual(bytes(state).hex(), '89d810e8855ace682d1843d8cb128fe4')

    def test_inverse_pairs_and_input_range(self):
        rng = random.Random(2026)
        for _ in range(100):
            original = list(rng.randbytes(16))
            for forward, inverse in ((sub_bytes,inv_sub_bytes), (shift_rows,inv_shift_rows), (mix_columns,inv_mix_columns)):
                state = original.copy()
                forward(state)
                self.assertTrue(all(0 <= value <= 255 for value in state))
                inverse(state)
                self.assertEqual(state, original)

    def test_add_round_key_is_own_inverse(self):
        state = list(PLAIN)
        key = list(range(16))
        add_round_key(state, key)
        self.assertEqual(bytes(state).hex(), '00102030405060708090a0b0c0d0e0f0')
        add_round_key(state, key)
        self.assertEqual(bytes(state), PLAIN)


class KeyScheduleTests(unittest.TestCase):
    def test_word_operations(self):
        self.assertEqual(rot_word([0x09,0xcf,0x4f,0x3c]), [0xcf,0x4f,0x3c,0x09])
        self.assertEqual(sub_word([0xcf,0x4f,0x3c,0x09]), [0x8a,0x84,0xeb,0x01])

    def test_lengths_and_original_key(self):
        for size, count in ((16,11), (24,13), (32,15)):
            key = bytes(range(size))
            keys = expand_key(key)
            self.assertEqual(len(keys), count)
            self.assertTrue(all(len(item)==16 for item in keys))
            self.assertEqual(bytes(v for item in keys for v in item)[:size], key)

    def test_fips_128_expansion(self):
        self.check_schedule(0)

    def test_fips_192_expansion(self):
        self.check_schedule(1)

    def test_fips_256_expansion_and_extra_subword(self):
        self.check_schedule(2)

    def check_schedule(self, index):
        key, checkpoints = KEY_CHECKPOINTS[index]
        flat = bytes(value for item in expand_key(bytes.fromhex(key)) for value in item)
        for i, expected in checkpoints.items():
            self.assertEqual(flat[4*i:4*i+4].hex(), expected)


class CipherTests(unittest.TestCase):
    def test_fips_128(self):
        self.check_vector(0)

    def test_fips_192(self):
        self.check_vector(1)

    def test_fips_256(self):
        self.check_vector(2)

    def check_vector(self, index):
        key, expected = FIPS_VECTORS[index]
        aes = AES(key)
        self.assertEqual(aes.encrypt_block(PLAIN).hex(), expected)
        self.assertEqual(aes.decrypt_block(bytes.fromhex(expected)), PLAIN)
        self.assertEqual(aes.rounds, (10,12,14)[index])

    def test_nist_four_block_vectors(self):
        for key, expected in NIST_VECTORS:
            aes = AES(bytes.fromhex(key))
            self.assertEqual(aes.encrypt_blocks(NIST_PLAIN).hex(), expected)
            self.assertEqual(aes.decrypt_blocks(bytes.fromhex(expected)), NIST_PLAIN)

    def test_random_round_trips_all_versions(self):
        rng = random.Random(314159)
        for length in (16,24,32):
            for _ in range(40):
                aes = AES(rng.randbytes(length))
                block = rng.randbytes(16)
                self.assertEqual(aes.decrypt_block(aes.encrypt_block(block)), block)

    def test_empty_and_multiple_blocks(self):
        aes = AES(bytes(16))
        self.assertEqual(aes.encrypt_blocks(b''), b'')
        self.assertEqual(aes.decrypt_blocks(b''), b'')
        data = bytes(range(256))
        self.assertEqual(aes.decrypt_blocks(aes.encrypt_blocks(data)), data)

    def test_invalid_key(self):
        for length in (0,15,17,23,25,31,33):
            with self.assertRaises(ValueError):
                AES(bytes(length))
        for value in ('0'*16, [0]*16, None, bytearray(16)):
            with self.assertRaises(TypeError):
                AES(value)

    def test_invalid_blocks(self):
        aes = AES(bytes(16))
        for method in (aes.encrypt_block, aes.decrypt_block):
            for length in (0,15,17,32):
                with self.assertRaises(ValueError):
                    method(bytes(length))
            with self.assertRaises(TypeError):
                method('0'*16)
        for method in (aes.encrypt_blocks,aes.decrypt_blocks):
            with self.assertRaises(ValueError):
                method(bytes(17))
            with self.assertRaises(TypeError):
                method([0]*16)


if __name__ == '__main__':
    unittest.main()
