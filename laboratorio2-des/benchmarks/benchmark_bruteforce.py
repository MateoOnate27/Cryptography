import argparse
import csv
import hashlib
import json
import os
import platform
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from attacks import candidate_to_key, parallel_brute_force_des
from attacks.keyspace import DEFAULT_FIXED
from deslib import des_encrypt_block

ROOT = Path(__file__).resolve().parents[1]
PLAIN = bytes.fromhex("0123456789ABCDEF")


def machine_info() -> dict:
    logical = os.cpu_count() or 1
    affinity = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else logical
    model = platform.processor() or platform.machine()
    physical = None
    quota = None
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        records = cpuinfo.read_text().split("\n\n")
        cores = set()
        for record in records:
            fields = dict(line.split(":", 1) for line in record.splitlines() if ":" in line)
            fields = {key.strip(): value.strip() for key, value in fields.items()}
            model = fields.get("model name", model)
            if "physical id" in fields and "core id" in fields:
                cores.add((fields["physical id"], fields["core id"]))
        physical = len(cores) or None
    elif platform.system() == "Darwin":
        try:
            model = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
            physical = int(subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"], text=True))
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    elif platform.system() == "Windows":
        try:
            output = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command",
                 "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores | ConvertTo-Json -Compress"],
                text=True, timeout=15,
            )
            chips = json.loads(output)
            chips = chips if isinstance(chips, list) else [chips]
            model = "; ".join(chip["Name"] for chip in chips)
            physical = sum(chip["NumberOfCores"] for chip in chips)
        except (OSError, subprocess.SubprocessError, ValueError, KeyError):
            pass
    quota_path = Path("/sys/fs/cgroup/cpu.max")
    if quota_path.exists():
        allowed, period = quota_path.read_text().split()
        if allowed != "max":
            quota = int(allowed) / int(period)
    available = min(logical, affinity, max(1, int(quota)) if quota is not None else logical)
    return {
        "cpu_model": model, "physical_cores": physical, "logical_cores": logical,
        "affinity_cores": affinity, "cpu_quota": quota, "available_workers": available,
        "system": platform.platform(), "python": platform.python_version(),
    }


def worker_counts(maximum: int) -> list[int]:
    counts = []
    value = 1
    while value <= maximum:
        counts.append(value)
        value *= 2
    if maximum not in counts:
        counts.append(maximum)
    return counts


def source_hash() -> str:
    digest = hashlib.sha256()
    for directory in ("deslib", "attacks", "benchmarks"):
        for path in sorted((ROOT / directory).glob("*.py")):
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def summarize(runs: list[dict]) -> list[dict]:
    summaries = []
    for bits, workers in sorted({(row["bits"], row["workers"]) for row in runs}):
        group = [row for row in runs if row["bits"] == bits and row["workers"] == workers]
        times = [row["seconds"] for row in group]
        summaries.append({
            "bits": bits, "workers": workers, "repetitions": len(group),
            "mean_seconds": statistics.mean(times),
            "stdev_seconds": statistics.stdev(times) if len(times) > 1 else 0.0,
            "mean_tested": statistics.mean(row["tested"] for row in group),
            "keys_per_second": sum(row["tested"] for row in group) / sum(times),
        })
    baseline = {row["bits"]: row["mean_seconds"] for row in summaries if row["workers"] == 1}
    for row in summaries:
        row["speedup"] = baseline[row["bits"]] / row["mean_seconds"]
        row["efficiency"] = row["speedup"] / row["workers"]
    return summaries


def extrapolate(rate: float) -> dict:
    result = {"rate_keys_per_second": rate}
    for name, count in (("worst", 1 << 56), ("average", 1 << 55)):
        seconds = count / rate
        result[name] = {"seconds": seconds, "hours": seconds / 3600,
                        "days": seconds / 86400, "years": seconds / (365.25 * 86400)}
    return result


def save_results(folder: Path, data: dict) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    data["summary"] = summarize(data["runs"])
    best = max(row["keys_per_second"] for row in data["summary"])
    data["des56"] = extrapolate(best)
    temporary = folder / "benchmark.tmp"
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(folder / "benchmark.json")
    for filename, rows in (("mediciones.csv", data["runs"]), ("resumen.csv", data["summary"])):
        with (folder / filename).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, nargs="+", default=[16, 18, 20])
    parser.add_argument("--repeticiones", type=int, default=3)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--origen", required=True, choices=["equipo-estudiante", "entorno-asistente"])
    parser.add_argument("--salida", type=Path, default=ROOT / "results" / "mi_equipo")
    parser.add_argument("--reanudar", action="store_true")
    args = parser.parse_args()
    if any(not 1 <= bits <= 24 for bits in args.bits):
        parser.error("Cada n debe estar entre 1 y 24; no se permite buscar DES-56.")
    if args.repeticiones < 3 or args.max_workers < 1:
        parser.error("Usa al menos tres repeticiones y un proceso.")
    machine = machine_info()
    workers = worker_counts(min(args.max_workers, machine["available_workers"]))
    settings = {"bits": sorted(set(args.bits)), "repetitions": args.repeticiones,
                "workers": workers, "origin": args.origen, "fixed_effective": f"{DEFAULT_FIXED:014X}",
                "target_position": "ultima clave: 2**n - 1", "plaintext": PLAIN.hex().upper(),
                "source_sha256": source_hash()}
    target = args.salida / "benchmark.json"
    if target.exists():
        if not args.reanudar:
            parser.error("La salida ya tiene resultados; usa otra carpeta o --reanudar.")
        data = json.loads(target.read_text(encoding="utf-8"))
        if data["settings"] != settings or data["machine"] != machine:
            parser.error("No se pueden mezclar equipos, configuraciones o versiones de código.")
    else:
        data = {"created_utc": datetime.now(timezone.utc).isoformat(),
                "machine": machine, "settings": settings, "runs": []}
    print(f"CPU: {machine['cpu_model']} | procesos: {workers}", flush=True)
    print("Se busca hasta la última clave; los espacios grandes pueden tardar horas.", flush=True)
    completed = {(row["bits"], row["workers"], row["repetition"]) for row in data["runs"]}
    for bits in settings["bits"]:
        size = 1 << bits
        target_key = candidate_to_key(size - 1, bits)
        ciphertext = des_encrypt_block(target_key, PLAIN)
        for repetition in range(1, args.repeticiones + 1):
            for count in workers:
                if (bits, count, repetition) in completed:
                    continue
                print(f"Inicia n={bits}, p={count}, repetición={repetition}", flush=True)
                result = parallel_brute_force_des(PLAIN, ciphertext, 0, size, count, bits)
                if result.key != target_key or result.candidate != size - 1:
                    raise RuntimeError("La búsqueda no recuperó la clave generada.")
                second_plain = b"DES LAB2"
                if des_encrypt_block(result.key, second_plain) != des_encrypt_block(target_key, second_plain):
                    raise RuntimeError("Falló la confirmación de la segunda pareja.")
                data["runs"].append({
                    "bits": bits, "workers": count, "repetition": repetition,
                    "space_size": size, "candidate": result.candidate,
                    "key_hex": result.key.hex().upper(), "ciphertext_hex": ciphertext.hex().upper(),
                    "tested": result.tested, "seconds": result.elapsed,
                    "keys_per_second": result.keys_per_second,
                    "worker_tested": json.dumps(result.worker_tested),
                })
                save_results(args.salida, data)
                print(f"  {result.tested:,} claves | {result.elapsed:.3f} s | {result.keys_per_second:.1f} claves/s", flush=True)
    print(f"Resultados: {args.salida.resolve()}", flush=True)


if __name__ == "__main__":
    main()
