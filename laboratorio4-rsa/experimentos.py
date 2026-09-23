import random
from statistics import mean, stdev
from time import perf_counter
from factorizacion import es_primo, raiz_entera, trial_division, fermat, pollard_rho

ALGORITMOS = [("Trial Division", trial_division), ("Fermat", fermat),
              ("Pollard Rho", pollard_rho)]

def primo_aleatorio(bits, generador):
    while True:
        candidato = generador.randrange(2 ** (bits - 1), 2 ** bits)
        if es_primo(candidato):
            return candidato


def generar_modulo(bits, semilla):
    if not 12 <= bits <= 32:
        raise ValueError("Para esta práctica elegimos entre 12 y 32 bits.")
    generador = random.Random(semilla)
    while True:
        p = primo_aleatorio(bits // 2, generador)
        q = primo_aleatorio(bits - bits // 2, generador)
        n = p * q
        if p != q and n.bit_length() == bits:
            return {"bits": bits, "n": n, "p": p, "q": q}


def siguiente_primo(numero):
    while not es_primo(numero):
        numero += 1
    return numero


def generar_casos_distancia(bits):
    if not 12 <= bits <= 32:
        raise ValueError("Seleccionar entre 12 y 32 bits.")
    objetivo = 3 * 2 ** (bits - 2)
    p_cerca = siguiente_primo(raiz_entera(objetivo))
    q_cerca = siguiente_primo(p_cerca + 1)
    p_lejos = siguiente_primo(2 ** (bits // 2 - 2))
    q_lejos = siguiente_primo((objetivo + p_lejos - 1) // p_lejos)
    casos = []
    for nombre, p, q in [("cercanos", p_cerca, q_cerca),
                         ("separados", p_lejos, q_lejos)]:
        n = p * q
        if n.bit_length() != bits:
            raise ValueError("La generación no conservó el tamaño solicitado.")
        casos.append({"caso": nombre, "bits": bits, "n": n,
                      "p": p, "q": q, "distancia": abs(p - q)})
    return casos


def medir(algoritmo, n):
    inicio = perf_counter()
    resultado = algoritmo(n)
    segundos = perf_counter() - inicio
    return resultado, segundos


def benchmark():
    casos, mediciones, resumen = [], [], []
    for bits in [16, 20, 24, 28]:
        caso = generar_modulo(bits, semilla=2026 + bits)
        casos.append(caso)
        fila = {"bits": bits, "n": caso["n"]}
        for nombre, algoritmo in ALGORITMOS:
            algoritmo(caso["n"])  
            tiempos = []
            for repeticion in range(1, 4):
                r, segundos = medir(algoritmo, caso["n"])
                if sorted([r["p"], r["q"]]) != sorted([caso["p"], caso["q"]]):
                    raise AssertionError("Factores incorrectos.")
                tiempos.append(segundos)
                mediciones.append({"bits": bits, "n": caso["n"], "algoritmo": nombre,
                                   "repeticion": repeticion, "segundos": segundos, **r})
            fila[nombre + " media_s"] = mean(tiempos)
            fila[nombre + " desviacion_s"] = stdev(tiempos)
        resumen.append(fila)
    print("\nBits | n          | Trial (ms) | Fermat (ms) | Rho (ms)")
    for r in resumen:
        print(f"{r['bits']:4} | {r['n']:10} | {r['Trial Division media_s']*1000:.6f} | "
              f"{r['Fermat media_s']*1000:.6f} | {r['Pollard Rho media_s']*1000:.6f}")
    return {"casos": casos, "mediciones": mediciones, "resumen": resumen}


def comparar_distancias():
    """Dos módulos de 28 bits, con primos cercanos y separados."""
    mediciones, resumen = [], []
    for caso in generar_casos_distancia(28):
        fermat(caso["n"])  
        tiempos = []
        for repeticion in range(1, 4):
            r, segundos = medir(fermat, caso["n"])
            if (r["p"], r["q"]) != (caso["p"], caso["q"]):
                raise AssertionError("Factores incorrectos.")
            tiempos.append(segundos)
            mediciones.append({**caso, "repeticion": repeticion,
                               "segundos": segundos, "iteraciones": r["iteraciones"]})
        resumen.append({**caso, "iteraciones": r["iteraciones"],
                        "media_s": mean(tiempos), "desviacion_s": stdev(tiempos)})
    print("\nCaso | p | q | n | distancia | iteraciones | tiempo medio (ms)")
    for r in resumen:
        print(f"{r['caso']} | {r['p']} | {r['q']} | {r['n']} | {r['distancia']} | "
              f"{r['iteraciones']} | {r['media_s']*1000:.6f}")
    return {"mediciones": mediciones, "resumen": resumen}
