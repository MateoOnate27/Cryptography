import math
import unittest

from factorizacion import mcd, raiz_entera, es_primo
from rsa import inverso_modular, potencia_modular
from factorizacion import trial_division, fermat, pollard_rho
from rsa import crear_claves, cifrar, descifrar, recuperar_clave
from experimentos import generar_modulo, generar_casos_distancia

ALGORITMOS = (trial_division, fermat, pollard_rho)


class PruebasMatematicas(unittest.TestCase):
    def test_mcd(self):
        for a, b in [(48, 18), (17, 3120), (0, 0), (-12, 8), (7, 0)]:
            self.assertEqual(mcd(a, b), math.gcd(a, b))

    def test_inverso(self):
        for a, modulo in [(17, 3120), (7, 160), (3, 20), (-3, 11)]:
            self.assertEqual((a * inverso_modular(a, modulo)) % modulo, 1)
        self.assertEqual(inverso_modular(17, 3120), 2753)

    def test_sin_inverso(self):
        for a, modulo in [(6, 12), (0, 7), (3, 1)]:
            with self.assertRaises(ValueError):
                inverso_modular(a, modulo)

    def test_raiz(self):
        for n in [0, 1, 2, 4, 3233, 10 ** 40 - 1, 10 ** 40]:
            r = raiz_entera(n)
            self.assertTrue(r * r <= n < (r + 1) ** 2)
        with self.assertRaises(ValueError):
            raiz_entera(-1)

    def test_potencia(self):
        for base, exponente, modulo in [(65, 17, 3233), (2790, 2753, 3233),
                                        (9, 0, 7), (0, 0, 1), (-5, 13, 19)]:
            self.assertEqual(potencia_modular(base, exponente, modulo),
                             pow(base, exponente, modulo))

    def test_potencia_invalida(self):
        for exponente, modulo in [(-1, 5), (1, 0)]:
            with self.assertRaises(ValueError):
                potencia_modular(2, exponente, modulo)

    def test_primos(self):
        for n in [2, 3, 11, 53, 61, 65537]:
            self.assertTrue(es_primo(n))
        for n in [-1, 0, 1, 4, 49, 121, 3233]:
            self.assertFalse(es_primo(n))


class PruebasFactorizacion(unittest.TestCase):
    def test_tres_algoritmos(self):
        for algoritmo in ALGORITMOS:
            for n in [4, 6, 9, 15, 33, 49, 187, 3233, 10403]:
                with self.subTest(algoritmo=algoritmo.__name__, n=n):
                    r = algoritmo(n)
                    self.assertEqual(r["p"] * r["q"], n)
                    self.assertTrue(1 < r["p"] <= r["q"] < n)

    def test_factores_enunciado(self):
        for algoritmo in ALGORITMOS:
            r = algoritmo(3233)
            self.assertEqual((r["p"], r["q"]), (53, 61))

    def test_entradas_pequenas(self):
        for algoritmo in ALGORITMOS:
            for n in [-1, 0, 1, 2, 3]:
                with self.assertRaises(ValueError):
                    algoritmo(n)

    def test_primos_y_limites(self):
        for algoritmo in [trial_division, fermat]:
            with self.assertRaises(ValueError):
                algoritmo(13)
        with self.assertRaises(RuntimeError):
            pollard_rho(13, max_iteraciones=10, max_intentos=2)
        with self.assertRaises(RuntimeError):
            fermat(3 * 101, max_iteraciones=1)

    def test_reinicio_rho(self):
        r = pollard_rho(91, c_inicial=0, x_inicial=0)
        self.assertEqual(r["p"] * r["q"], 91)
        self.assertGreaterEqual(r["reinicios"], 1)

    def test_iteraciones_fermat(self):
        for caso in generar_casos_distancia(20):
            n, p, q = caso["n"], caso["p"], caso["q"]
            inicio = raiz_entera(n)
            if inicio * inicio < n:
                inicio += 1
            esperado = (p + q) // 2 - inicio + 1
            self.assertEqual(fermat(n)["iteraciones"], esperado)


class PruebasRSA(unittest.TestCase):
    def test_recuperacion_enunciado(self):
        for algoritmo in ALGORITMOS:
            r = recuperar_clave(3233, 17, 2790, algoritmo)
            self.assertEqual((r["phi"], r["d"], r["m"]), (3120, 2753, 65))
            self.assertTrue(r["verificado"])

    def test_ejemplos_diapositivas(self):
        self.assertEqual(crear_claves(11, 17, 7)["d"], 23)
        self.assertEqual(cifrar(42, 7, 187), 15)
        self.assertEqual(descifrar(15, 23, 187), 42)
        self.assertEqual(cifrar(4, 3, 33), 31)
        self.assertEqual(descifrar(31, 7, 33), 4)
        self.assertEqual(recuperar_clave(3233, 17, 855, fermat)["m"], 123)

    def test_todos_los_mensajes_de_un_caso(self):
        claves = crear_claves(11, 17, 7)
        for mensaje in range(claves["n"]):
            c = cifrar(mensaje, claves["e"], claves["n"])
            self.assertEqual(descifrar(c, claves["d"], claves["n"]), mensaje)

    def test_claves_invalidas(self):
        for p, q, e in [(11, 11, 7), (9, 11, 7), (11, 17, 2), (3, 11, 20)]:
            with self.assertRaises(ValueError):
                crear_claves(p, q, e)

    def test_rango_mensajes(self):
        for numero in [-1, 3233]:
            with self.assertRaises(ValueError):
                cifrar(numero, 17, 3233)
            with self.assertRaises(ValueError):
                descifrar(numero, 2753, 3233)

    def test_modulo_no_semiprimo(self):
        with self.assertRaises(ValueError):
            recuperar_clave(105, 5, 1, trial_division)


class PruebasGeneracion(unittest.TestCase):
    def test_tamanos_y_reproducibilidad(self):
        for bits in [16, 20, 24, 28]:
            caso = generar_modulo(bits, 2026)
            self.assertEqual(caso, generar_modulo(bits, 2026))
            self.assertEqual(caso["n"].bit_length(), bits)
            self.assertTrue(es_primo(caso["p"]) and es_primo(caso["q"]))
            self.assertNotEqual(caso["p"], caso["q"])
            for algoritmo in ALGORITMOS:
                r = algoritmo(caso["n"])
                self.assertEqual(sorted([r["p"], r["q"]]),
                                 sorted([caso["p"], caso["q"]]))

    def test_distancias(self):
        for bits in range(12, 33):
            cerca, lejos = generar_casos_distancia(bits)
            self.assertEqual(cerca["n"].bit_length(), lejos["n"].bit_length())
            self.assertLess(cerca["distancia"], lejos["distancia"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
