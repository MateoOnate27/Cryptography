import json
import random
from pathlib import Path
from datetime import datetime, timezone
from aeslib import AES
from benchmarks.support import ROOT, source_hash


def main():
    import cryptography
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    rng = random.Random(20260916)
    comparisons = 0
    for length in (16,24,32):
        for _ in range(16):
            key = rng.randbytes(length)
            plaintext = rng.randbytes(256)
            reference = Cipher(algorithms.AES(key),modes.ECB()).encryptor()
            expected = reference.update(plaintext)+reference.finalize()
            aes = AES(key)
            if aes.encrypt_blocks(plaintext) != expected or aes.decrypt_blocks(expected) != plaintext:
                raise RuntimeError('Diferencia frente a la implementación externa.')
            comparisons += 16
    result = {'passed':True,'blocks_per_direction':comparisons,
              'key_sizes':[128,192,256],'different_keys':48,
              'reference':'cryptography '+cryptography.__version__,
              'source_sha256':source_hash(),'created_utc':datetime.now(timezone.utc).isoformat()}
    folder = ROOT/'results'/'validacion'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'referencia_externa.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f'Coinciden {comparisons} bloques de cifrado y {comparisons} de descifrado.')


if __name__ == '__main__':
    main()
