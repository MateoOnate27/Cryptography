import unittest
from Lab1 import des_procesar_bloque, hex_a_bin, bin_a_hex

class TestDES(unittest.TestCase):

    def test_vector_nist_estandar(self):
        texto_plano_hex = "0123456789ABCDEF"
        clave_hex = "133457799BBCDFF1"
        criptograma_esperado_hex = "85E813540F0AB405"

        texto_bin = hex_a_bin(texto_plano_hex)
        clave_bin = hex_a_bin(clave_hex)

        # Prueba de Cifrado
        cifrado_bin = des_procesar_bloque(texto_bin, clave_bin, descifrar=False)
        self.assertEqual(bin_a_hex(cifrado_bin), criptograma_esperado_hex)

        # Prueba de Descifrado
        descifrado_bin = des_procesar_bloque(cifrado_bin, clave_bin, descifrar=True)
        self.assertEqual(bin_a_hex(descifrado_bin), texto_plano_hex)

    def test_vector_ceros(self):
        texto_plano_hex = "0000000000000000"
        clave_hex = "0000000000000000"
        criptograma_esperado_hex = "8CA64DE9C1B123A7"

        texto_bin = hex_a_bin(texto_plano_hex)
        clave_bin = hex_a_bin(clave_hex)

        cifrado_bin = des_procesar_bloque(texto_bin, clave_bin, descifrar=False)
        self.assertEqual(bin_a_hex(cifrado_bin), criptograma_esperado_hex)

        descifrado_bin = des_procesar_bloque(cifrado_bin, clave_bin, descifrar=True)
        self.assertEqual(bin_a_hex(descifrado_bin), texto_plano_hex)

if __name__ == "__main__":
    unittest.main()
