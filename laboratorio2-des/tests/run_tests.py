import hashlib
import io
import json
import platform
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_hash() -> str:
    digest = hashlib.sha256()
    for directory in ("deslib", "modes", "attacks", "tests"):
        for path in sorted((ROOT / directory).glob("*.py")):
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    text = stream.getvalue()
    print(text, end="")
    folder = ROOT / "results"
    folder.mkdir(exist_ok=True)
    (folder / "pruebas.txt").write_text(text, encoding="utf-8")
    evidence = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "system": platform.platform(), "python": platform.python_version(),
                "tests_run": result.testsRun, "failures": len(result.failures),
                "errors": len(result.errors), "skipped": len(result.skipped),
                "passed": result.wasSuccessful(), "source_sha256": test_source_hash()}
    (folder / "pruebas.json").write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
