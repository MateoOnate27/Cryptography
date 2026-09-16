import hashlib
import math
import os
import platform
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source_hash():
    digest = hashlib.sha256()
    for folder in ('aeslib', 'benchmarks', 'tests'):
        for path in sorted((ROOT / folder).glob('*.py')):
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()


def machine_info():
    model = platform.processor() or platform.machine()
    cpu_file = Path('/proc/cpuinfo')
    if cpu_file.exists():
        for line in cpu_file.read_text().splitlines():
            if line.startswith('model name'):
                model = line.split(':', 1)[1].strip()
                break
    elif platform.system() == 'Windows':
        try:
            model = subprocess.check_output(['powershell', '-NoProfile', '-Command',
                '(Get-CimInstance Win32_Processor).Name'], text=True, timeout=15).strip()
        except (OSError, subprocess.SubprocessError):
            pass
    elif platform.system() == 'Darwin':
        try:
            model = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True).strip()
        except (OSError, subprocess.SubprocessError):
            pass
    quota_file = Path('/sys/fs/cgroup/cpu.max')
    return {'cpu':model, 'logical_cpus':os.cpu_count(),
            'affinity_cpus':len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
            'cpu_quota':quota_file.read_text().strip() if quota_file.exists() else None,
            'system':platform.platform(), 'python':platform.python_version(),
            'implementation':platform.python_implementation(),
            'interpreter_version':list(platform.python_build()), 'processes':1}


def summarize(runs):
    summaries = []
    for bits, size in sorted({(row['key_bits'],row['size_mb']) for row in runs}):
        group = [row for row in runs if row['key_bits']==bits and row['size_mb']==size]
        item = {'key_bits':bits, 'rounds':bits//32+6, 'size_mb':size, 'repetitions':len(group)}
        for operation in ('encryption','decryption'):
            times = [row[operation+'_s'] for row in group]
            average = statistics.mean(times)
            item[operation+'_mean_s'] = average
            item[operation+'_sd_s'] = statistics.stdev(times) if len(times)>1 else 0.0
            item[operation+'_mb_s'] = size / average
        summaries.append(item)
    return summaries


def validate_results(payload, require_complete=False):
    settings = payload['settings']
    expected = {(bits,size,rep) for bits in (128,192,256) for size in settings['sizes_mb']
                for rep in range(1,settings['repetitions']+1)}
    seen = set()
    input_hashes = {}
    cipher_hashes = {}
    for row in payload['runs']:
        identity = (row['key_bits'],row['size_mb'],row['repetition'])
        if identity in seen or identity not in expected:
            raise ValueError('Medición duplicada o fuera de la configuración.')
        seen.add(identity)
        if row['bytes'] != round(row['size_mb']*1_000_000) or row['bytes'] % 16:
            raise ValueError('La cantidad de bytes no coincide con MB decimales.')
        if row['rounds'] != row['key_bits']//32+6 or not row['roundtrip_ok']:
            raise ValueError('Rondas incorrectas o recuperación fallida.')
        if row['plaintext_sha256'] != row['recovered_sha256']:
            raise ValueError('Los hashes de entrada y recuperación difieren.')
        previous = input_hashes.setdefault(row['size_mb'],row['plaintext_sha256'])
        if previous != row['plaintext_sha256']:
            raise ValueError('Se requieren los mismos datos para comparar las versiones.')
        pair = (row['key_bits'],row['size_mb'])
        previous = cipher_hashes.setdefault(pair,row['ciphertext_sha256'])
        if previous != row['ciphertext_sha256']:
            raise ValueError('El cifrado debe ser reproducible entre repeticiones.')
        for operation in ('encryption','decryption'):
            duration = row[operation+'_s']
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError('Tiempo no válido.')
            if not math.isclose(row[operation+'_mb_s'],row['size_mb']/duration,rel_tol=1e-12):
                raise ValueError('Throughput inconsistente con D/T.')
    if require_complete:
        if seen != expected or not {1.0,10.0,100.0}.issubset(settings['sizes_mb']):
            raise ValueError('Faltan combinaciones o tamaños de 1, 10 y 100 MB.')
        if settings['repetitions'] < 3 or not payload['validation']['passed']:
            raise ValueError('Se requieren tres repeticiones como mínimo y pruebas aprobadas.')
    return seen == expected
