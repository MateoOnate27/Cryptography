import argparse
import csv
import gc
import hashlib
import io
import json
import random
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from aeslib import AES
from .support import ROOT, machine_info, source_hash, summarize, validate_results


def write_results(folder, payload):
    folder.mkdir(parents=True, exist_ok=True)
    payload['summary'] = summarize(payload['runs'])
    temporary = folder/'benchmark.tmp'
    temporary.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    temporary.replace(folder/'benchmark.json')
    for name, rows in (('mediciones.csv',payload['runs']),('resumen.csv',payload['summary'])):
        if rows:
            with (folder/name).open('w',newline='',encoding='utf-8') as stream:
                writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)


def run_tests():
    output = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'),top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
    return {'passed':result.wasSuccessful(),'count':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors)}, output.getvalue()


def make_data(size_mb, seed):
    size_bytes = round(size_mb*1_000_000)
    if size_bytes <= 0 or size_bytes % 16 or abs(size_bytes/1_000_000-size_mb)>1e-12:
        raise ValueError('El tamaño debe ser positivo y representar bloques completos de 16 bytes.')
    return random.Random(seed+size_bytes).randbytes(size_bytes)


def measure_pair(aes, data):
    gc.collect()
    start = perf_counter()
    encrypted = aes.encrypt_blocks(data)
    encryption_s = perf_counter()-start
    start = perf_counter()
    recovered = aes.decrypt_blocks(encrypted)
    decryption_s = perf_counter()-start
    if recovered != data:
        raise RuntimeError('El descifrado no recuperó todos los bytes.')
    return {'encryption_s':encryption_s,'decryption_s':decryption_s,
            'encryption_mb_s':len(data)/1_000_000/encryption_s,
            'decryption_mb_s':len(data)/1_000_000/decryption_s,
            'roundtrip_ok':True,'ciphertext_sha256':hashlib.sha256(encrypted).hexdigest(),
            'recovered_sha256':hashlib.sha256(recovered).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sizes-mb',nargs='+',type=float,default=[1,10,100])
    parser.add_argument('--repetitions',type=int,default=3)
    parser.add_argument('--output',type=Path,default=ROOT/'results'/'mi_equipo')
    parser.add_argument('--origin',required=True,help='equipo-estudiante o entorno-asistente')
    parser.add_argument('--resume',action='store_true')
    args = parser.parse_args()
    if args.repetitions < 1 or len(set(args.sizes_mb)) != len(args.sizes_mb):
        parser.error('Las repeticiones deben ser positivas y los tamaños distintos.')
    if any(not (0<size<=10000) for size in args.sizes_mb):
        parser.error('Cada tamaño debe estar entre 0 y 10000 MB, sin incluir 0.')
    settings = {'sizes_mb':sorted(args.sizes_mb),'repetitions':args.repetitions,
                'key_bits':[128,192,256],'bytes_per_mb':1_000_000,'seed':20260916,
                'warmup_bytes':1_000_000,'timer':'time.perf_counter',
                'key_schedule_timed':False,'data_generation_timed':False,'io_timed':False,
                'buffer_allocation_timed':True,'gc_enabled':gc.isenabled(),
                'operation_order':'encryption then decryption',
                'variant_order':'cyclic rotation by repetition'}
    for size in settings['sizes_mb']:
        n = round(size*1_000_000)
        if n % 16 or abs(n/1_000_000-size)>1e-12:
            parser.error('Cada tamaño debe representar un múltiplo exacto de 16 bytes.')
    fingerprint = source_hash()
    machine = machine_info()
    validation, test_log = run_tests()
    print(test_log,flush=True)
    if not validation['passed']:
        raise SystemExit('Las pruebas fallaron. No se inicia la evaluación.')
    path = args.output/'benchmark.json'
    if path.exists():
        if not args.resume:
            parser.error('La salida ya existe. Seleccione otra carpeta o añada --resume.')
        payload = json.loads(path.read_text(encoding='utf-8'))
        if (payload['source_sha256'] != fingerprint or payload['settings'] != settings
                or payload['machine'] != machine or payload['origin'] != args.origin):
            parser.error('Para reanudar deben coincidir código, equipo, intérprete y configuración.')
        validate_results(payload)
    else:
        if args.resume:
            parser.error('No existe una medición para reanudar en esa carpeta.')
        payload = {'schema':1,'created_utc':datetime.now(timezone.utc).isoformat(),
                   'origin':args.origin,'machine':machine,'settings':settings,
                   'source_sha256':fingerprint,'validation':validation,'runs':[],
                   'sessions':[],'complete':False}
    payload['sessions'].append({'started_utc':datetime.now(timezone.utc).isoformat(),
                                'arguments':sys.argv[1:]})
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'pruebas.txt').write_text(test_log,encoding='utf-8')
    write_results(args.output,payload)
    completed = {(r['key_bits'],r['size_mb'],r['repetition']) for r in payload['runs']}
    ciphers = {bits:AES(bytes(range(bits//8))) for bits in (128,192,256)}
    warmup = make_data(1,settings['seed'])
    for aes in ciphers.values():
        if aes.decrypt_blocks(aes.encrypt_blocks(warmup)) != warmup:
            raise RuntimeError('Falló el calentamiento.')
    del warmup
    try:
        for size in settings['sizes_mb']:
            data = make_data(size,settings['seed'])
            plain_hash = hashlib.sha256(data).hexdigest()
            for repetition in range(1,args.repetitions+1):
                order = [128,192,256]
                offset = (repetition-1)%3
                order = order[offset:]+order[:offset]
                for bits in order:
                    if (bits,size,repetition) in completed:
                        continue
                    print(f'AES-{bits}, {size:g} MB, repetición {repetition}: procesando...',flush=True)
                    row = {'key_bits':bits,'rounds':ciphers[bits].rounds,
                           'size_mb':size,'bytes':len(data),'repetition':repetition,
                           'plaintext_sha256':plain_hash,**measure_pair(ciphers[bits],data)}
                    payload['runs'].append(row)
                    validate_results(payload)
                    write_results(args.output,payload)
                    print(f"  cifrar {row['encryption_s']:.3f} s, descifrar {row['decryption_s']:.3f} s",flush=True)
            del data
    except KeyboardInterrupt:
        print('Se conservaron las repeticiones completas. Continúe con --resume.')
        return
    payload['complete'] = validate_results(payload)
    payload['finished_utc'] = datetime.now(timezone.utc).isoformat()
    write_results(args.output,payload)
    print('Resultados guardados en',args.output.resolve())


if __name__ == '__main__':
    main()
