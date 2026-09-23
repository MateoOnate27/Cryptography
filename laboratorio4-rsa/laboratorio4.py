import json
import platform
import unittest
from datetime import datetime, timezone
from pathlib import Path

from factorizacion import trial_division, fermat, pollard_rho
from rsa import recuperar_clave
from experimentos import benchmark, comparar_distancias


def leer_entero(nombre, predeterminado, minimo, maximo):
    while True:
        texto = input(f"{nombre} [{predeterminado}]: ").strip()
        try:
            numero = predeterminado if texto == "" else int(texto)
            if minimo <= numero <= maximo:
                return numero
        except ValueError:
            pass
        print(f"Escribir un entero entre {minimo} y {maximo}.")


def ejecutar_laboratorio():
    print("LABORATORIO 4: RSA FACTORIZATION ATTACKS")
    print("Enter conserva los datos del enunciado. También se pueden escribir otros datos de la práctica.")
    n = leer_entero("Módulo n", 3233, 4, 2 ** 32 - 1)
    algoritmos = [("Trial Division", trial_division), ("Fermat", fermat),
                  ("Pollard Rho", pollard_rho)]

    for numero, (nombre, algoritmo) in enumerate(algoritmos, start=1):
        print(f"\nEJERCICIO {numero}: {nombre}")
        r = algoritmo(n)
        print(f"p={r['p']}, q={r['q']}, p*q={r['p']*r['q']}")
        print(f"Iteraciones={r['iteraciones']}, reinicios={r['reinicios']}")

    print("\nEJERCICIO 4: RECUPERACIÓN DE LA CLAVE RSA")
    e = leer_entero("Exponente público e", min(17, n-1), 2, n-1)
    c = leer_entero("Texto cifrado c", min(2790, n-1), 0, n-1)
    recuperaciones = []
    for nombre, algoritmo in algoritmos:
        r = recuperar_clave(n, e, c, algoritmo)
        recuperaciones.append({"algoritmo": nombre, **r})
        print(f"\n{nombre}: phi={r['phi']}, d={r['d']}, clave privada=({n},{r['d']})")
        print(f"Mensaje recuperado={r['m']}, verificación del cifrado={r['verificado']}")

    print("\nEJERCICIO 5: PRUEBAS AUTOMÁTICAS", flush=True)
    carpeta = Path(__file__).resolve().parent
    pruebas = unittest.defaultTestLoader.discover(str(carpeta), "test_laboratorio.py")
    validacion = unittest.TextTestRunner(verbosity=2).run(pruebas)
    if not validacion.wasSuccessful():
        raise RuntimeError("Las pruebas deben pasar antes de medir.")

    print("\nEJERCICIO 6: COMPARACIÓN DE LOS TRES ALGORITMOS")
    rendimiento = benchmark()
    print("\nEJERCICIO 7: DISTANCIA ENTRE LOS PRIMOS")
    distancia = comparar_distancias()

    datos = {"fecha_utc": datetime.now(timezone.utc).isoformat(),
             "python": platform.python_version(), "sistema": platform.platform(),
             "procesador": platform.processor(), "pruebas_aprobadas": validacion.testsRun,
             "recuperacion": recuperaciones, "benchmark": rendimiento, "distancia": distancia}
    ruta = carpeta / "resultados.json"
    ruta.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nLaboratorio terminado. Resultados guardados en {ruta.name}.")


if __name__ == "__main__":
    try:
        ejecutar_laboratorio()
    except (ValueError, RuntimeError) as error:
        print(f"No se pudo completar: {error}")
    except (EOFError, KeyboardInterrupt):
        print("\nEjecución interrumpida.")
