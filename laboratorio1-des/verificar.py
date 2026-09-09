import io
import json
import platform
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

from ejemplo import mostrar_resultados, obtener_resultados

ROOT = Path(__file__).resolve().parent


def main() -> int:
    folder = ROOT / "resultados"
    folder.mkdir(exist_ok=True)

    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue(), end="")
    (folder / "pruebas.txt").write_text(stream.getvalue(), encoding="utf-8")
    metadata = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "sistema": platform.platform(),
        "pruebas": result.testsRun,
        "fallos": len(result.failures),
        "errores": len(result.errors),
        "correcto": result.wasSuccessful(),
    }
    (folder / "verificacion.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if not result.wasSuccessful():
        return 1

    data = obtener_resultados()
    (folder / "ejemplo.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    output = io.StringIO()
    with redirect_stdout(output):
        mostrar_resultados(data)
    (folder / "ejemplo.txt").write_text(output.getvalue(), encoding="utf-8")
    print("Evidencias guardadas en la carpeta resultados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
