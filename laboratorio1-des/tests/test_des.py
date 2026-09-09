import random
import unittest

from deslib import des_check_parity, des_decrypt_block, des_encrypt_block, des_key_schedule
from deslib.des_core import des_block
from deslib.feistel import des_round, feistel_f
from deslib.key_schedule import rotate_left28
from deslib.permutation import permute
from deslib.sboxes import sbox_lookup, substitute
from deslib.tables import E, IP, IP_INVERSE, PC1, PC2, ROTATIONS, SBOXES

KEY = bytes.fromhex("133457799BBCDFF1")
PLAIN = bytes.fromhex("0123456789ABCDEF")
CIPHER = bytes.fromhex("85E813540F0AB405")


class PruebasComponentesDES(unittest.TestCase):
    def test_bit_uno_es_el_mas_significativo(self):
        self.assertEqual(permute(0b10000000, (1,), 8), 1)
        self.assertEqual(permute(0b00000001, (1,), 8), 0)
        self.assertEqual(permute(1 << (64 - 58), IP, 64), 1 << 63)

    def test_ip_y_su_inversa(self):
        self.assertEqual(permute(int.from_bytes(PLAIN, "big"), IP, 64), 0xCC00CCFFF0AAF0AA)
        for bit in range(64):
            value = 1 << bit
            self.assertEqual(permute(permute(value, IP, 64), IP_INVERSE, 64), value)

    def test_errores_de_permutacion(self):
        for args in [(256, (1,), 8), (-1, (1,), 8), (0, (0,), 8), (0, (9,), 8), (0, (), 0)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                permute(*args)

    def test_tablas_y_posiciones_de_paridad(self):
        self.assertEqual(set(range(1, 65)) - set(PC1), set(range(8, 65, 8)))
        self.assertEqual(len(PC1), 56)
        self.assertEqual(len(set(PC2)), 48)
        self.assertEqual(sum(ROTATIONS), 28)
        for box in SBOXES:
            self.assertEqual(len(box), 4)
            for row in box:
                self.assertEqual(sorted(row), list(range(16)))

    def test_ejemplo_s1(self):
        self.assertEqual(sbox_lookup(0, 0b100101), 0b1000)

    def test_salidas_sboxes_de_cuatro_bits(self):
        for box in range(8):
            for group in range(64):
                self.assertIn(sbox_lookup(box, group), range(16))

    def test_expansion_sustitucion_y_funcion_f(self):
        self.assertEqual(permute(0xF0AAF0AA, E, 32), 0x7A15557A1555)
        self.assertEqual(substitute(0x6117BA866527), 0x5C82B597)
        self.assertEqual(feistel_f(0xF0AAF0AA, 0x1B02EFFC7072), 0x234AA9BB)

    def test_una_ronda(self):
        self.assertEqual(des_round(0xCC00CCFF, 0xF0AAF0AA, 0x1B02EFFC7072),
                         (0xF0AAF0AA, 0xEF4A6544))

    def test_rotacion_circular(self):
        self.assertEqual(rotate_left28(1 << 27, 1), 1)
        self.assertEqual(rotate_left28(0x1234567, 28), 0x1234567)

    def test_generacion_subclaves(self):
        keys = des_key_schedule(KEY)
        self.assertEqual(len(keys), 16)
        self.assertEqual(keys[0], 0x1B02EFFC7072)
        self.assertEqual(keys[-1], 0xCB3D8B0E17F5)
        self.assertTrue(all(0 <= key < (1 << 48) for key in keys))


class PruebasBloqueDES(unittest.TestCase):
    def test_cifrado_vector_conocido(self):
        self.assertEqual(des_encrypt_block(KEY, PLAIN), CIPHER)

    def test_descifrado_vector_conocido(self):
        self.assertEqual(des_decrypt_block(KEY, CIPHER), PLAIN)

    def test_nucleo_e_intercambio_final(self):
        keys = des_key_schedule(KEY)
        self.assertEqual(des_block(int.from_bytes(PLAIN, "big"), keys), int.from_bytes(CIPHER, "big"))
        with self.assertRaises(ValueError):
            des_block(0, keys[:-1])

    def test_32_bloques_recuperados(self):
        rng = random.Random(2026)  
        for i in range(32):
            key, block = rng.randbytes(8), rng.randbytes(8)
            with self.subTest(block=i):
                self.assertEqual(des_decrypt_block(key, des_encrypt_block(key, block)), block)

    def test_avalancha_texto(self):
        changed = (int.from_bytes(PLAIN, "big") ^ 1).to_bytes(8, "big")
        changed_cipher = des_encrypt_block(KEY, changed)
        difference = int.from_bytes(CIPHER, "big") ^ int.from_bytes(changed_cipher, "big")
        distance = difference.bit_count()
        self.assertTrue(20 <= distance <= 44, distance)

    def test_avalancha_bit_efectivo_clave(self):
        changed = (int.from_bytes(KEY, "big") ^ 2).to_bytes(8, "big")
        changed_cipher = des_encrypt_block(changed, PLAIN)
        difference = int.from_bytes(CIPHER, "big") ^ int.from_bytes(changed_cipher, "big")
        distance = difference.bit_count()
        self.assertTrue(20 <= distance <= 44, distance)

    def test_paridad_no_cambia_cifrado(self):
        self.assertTrue(des_check_parity(KEY))
        changed = bytes(byte ^ 1 for byte in KEY)
        self.assertFalse(des_check_parity(changed))
        self.assertEqual(des_key_schedule(KEY), des_key_schedule(changed))
        self.assertEqual(des_encrypt_block(changed, PLAIN), CIPHER)

    def test_longitudes_invalidas(self):
        for length in (0, 7, 9):
            for function in (des_encrypt_block, des_decrypt_block):
                with self.subTest(length=length, function=function.__name__):
                    with self.assertRaises(ValueError):
                        function(bytes(length), PLAIN)
                    with self.assertRaises(ValueError):
                        function(KEY, bytes(length))
            for function in (des_key_schedule, des_check_parity):
                with self.assertRaises(ValueError):
                    function(bytes(length))

    def test_tipo_bytes_requerido(self):
        with self.assertRaises(TypeError):
            des_encrypt_block(KEY, "ABCDEFGH")
        with self.assertRaises(TypeError):
            des_encrypt_block("12345678", PLAIN)


if __name__ == "__main__":
    unittest.main()
