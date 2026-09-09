from examples.experimentos import main as guardar_experimentos
from tests.run_tests import main as ejecutar_pruebas


def main():
    status = ejecutar_pruebas()
    if status != 0:
        return status
    guardar_experimentos()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
