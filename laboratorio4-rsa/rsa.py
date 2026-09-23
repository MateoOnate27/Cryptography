from factorizacion import es_primo, mcd


def inverso_modular(a, modulo):
    if modulo <= 1:
        raise ValueError("El módulo debe ser mayor que 1.")
    resto_anterior, resto = modulo, a % modulo
    coef_anterior, coef = 0, 1
    while resto != 0:
        cociente = resto_anterior // resto
        resto_anterior, resto = resto, resto_anterior - cociente * resto
        coef_anterior, coef = coef, coef_anterior - cociente * coef
    if resto_anterior != 1:
        raise ValueError("No existe inverso: los números no son coprimos.")
    return coef_anterior % modulo


def potencia_modular(base, exponente, modulo):
    if exponente < 0 or modulo < 1:
        raise ValueError("Exponente no negativo y módulo positivo requeridos.")
    resultado = 1 % modulo
    base = base % modulo
    for bit in bin(exponente)[2:]:
        resultado = (resultado * resultado) % modulo
        if bit == "1":
            resultado = (resultado * base) % modulo
    return resultado





def crear_claves(p, q, e):
    if not es_primo(p) or not es_primo(q) or p == q:
        raise ValueError("p y q deben ser primos distintos.")
    n = p * q
    phi = (p - 1) * (q - 1)
    if not 1 < e < phi or mcd(e, phi) != 1:
        raise ValueError("e debe cumplir 1 < e < phi y MCD(e, phi) = 1.")
    d = inverso_modular(e, phi)
    return {"n": n, "e": e, "phi": phi, "d": d}


def cifrar(mensaje, e, n):
    if not 0 <= mensaje < n:
        raise ValueError("El mensaje debe cumplir 0 <= m < n.")
    return potencia_modular(mensaje, e, n)


def descifrar(cifrado, d, n):
    if not 0 <= cifrado < n:
        raise ValueError("El cifrado debe cumplir 0 <= c < n.")
    return potencia_modular(cifrado, d, n)


def recuperar_clave(n, e, cifrado, algoritmo):
    factores = algoritmo(n)
    p, q = factores["p"], factores["q"]
    if p * q != n:
        raise ValueError("Los factores no reconstruyen n.")
    claves = crear_claves(p, q, e)
    mensaje = descifrar(cifrado, claves["d"], n)
    verificado = cifrar(mensaje, e, n) == cifrado
    return {**factores, **claves, "c": cifrado, "m": mensaje,
            "verificado": verificado}
