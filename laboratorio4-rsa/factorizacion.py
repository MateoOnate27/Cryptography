from math import isqrt


def mcd(a, b):
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a


def raiz_entera(n):
    return isqrt(n)


def es_primo(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    for divisor in range(3, raiz_entera(n) + 1, 2):
        if n % divisor == 0:
            return False
    return True



def resultado(n, factor, iteraciones, reinicios=0):
    otro = n // factor
    return {"p": min(factor, otro), "q": max(factor, otro),
            "iteraciones": iteraciones, "reinicios": reinicios}


def trial_division(n):
    if n < 4:
        raise ValueError("n debe ser un número compuesto mayor o igual que 4.")
    if n % 2 == 0:
        return resultado(n, 2, 1)
    iteraciones = 1  
    for divisor in range(3, raiz_entera(n) + 1, 2):
        iteraciones += 1
        if n % divisor == 0:
            return resultado(n, divisor, iteraciones)
    raise ValueError("n es primo: no tiene dos factores no triviales.")


def fermat(n, max_iteraciones=1000000):
    if n < 4:
        raise ValueError("n debe ser un número compuesto mayor o igual que 4.")
    if n % 2 == 0:
        return resultado(n, 2, 1)
    a = raiz_entera(n)
    if a * a < n:
        a += 1 
    for iteracion in range(1, max_iteraciones + 1):
        b_cuadrado = a * a - n
        b = raiz_entera(b_cuadrado)
        if b * b == b_cuadrado:
            if a - b == 1:
                raise ValueError("n es primo: Fermat encontró 1 y n.")
            return resultado(n, a - b, iteracion)
        a += 1
    raise RuntimeError("Fermat alcanzó el límite de iteraciones de la demostración.")


def pollard_rho(n, c_inicial=1, x_inicial=2,
               max_iteraciones=100000, max_intentos=20):
    if n < 4:
        raise ValueError("n debe ser un número compuesto mayor o igual que 4.")
    if n % 2 == 0:
        return resultado(n, 2, 1)
    total = 0
    for reinicios in range(max_intentos):
        constante = (c_inicial + reinicios) % n
        x = (x_inicial + reinicios) % n
        y = x
        for _ in range(max_iteraciones):
            x = (x * x + constante) % n
            y = (y * y + constante) % n
            y = (y * y + constante) % n
            divisor = mcd(abs(x - y), n)
            total += 1
            if 1 < divisor < n:
                return resultado(n, divisor, total, reinicios)
            if divisor == n:
                break  
    raise RuntimeError("Pollard Rho agotó los intentos. Cambiar c o x inicial.")
