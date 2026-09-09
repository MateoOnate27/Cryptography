import argparse

from attacks import candidate_to_key, parallel_brute_force_des
from deslib import des_encrypt_block


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bits", type=int, default=10)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if not 1 <= args.bits <= 24 or args.workers < 1:
        parser.error("Usa entre 1 y 24 bits y al menos un proceso.")
    position = (1 << args.bits) * 3 // 4
    original_key = candidate_to_key(position, args.bits)
    plaintext = b"DES LAB2"
    ciphertext = des_encrypt_block(original_key, plaintext)
    result = parallel_brute_force_des(plaintext, ciphertext, 0, 1 << args.bits, args.workers, args.bits)
    print("Clave recuperada:", result.key.hex().upper() if result.key else "no encontrada")
    print("Candidato:", result.candidate)
    print("Claves probadas:", result.tested)
    print(f"Tiempo: {result.elapsed:.4f} s | Throughput: {result.keys_per_second:.1f} claves/s")


if __name__ == "__main__":
    main()
