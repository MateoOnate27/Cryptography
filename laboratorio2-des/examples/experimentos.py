import argparse
import json
from pathlib import Path

from deslib import des_check_parity, des_decrypt_block, des_encrypt_block, des_key_schedule
from deslib.feistel import des_round, feistel_f
from deslib.permutation import permute
from deslib.tables import IP
from modes import des_cbc_decrypt, des_cbc_encrypt, des_ecb_decrypt, des_ecb_encrypt, pkcs7_pad

ROOT = Path(__file__).resolve().parents[1]
KEY = bytes.fromhex("133457799BBCDFF1")
PLAIN = bytes.fromhex("0123456789ABCDEF")


def blocks(data: bytes) -> list[str]:
    return [data[i:i+8].hex().upper() for i in range(0, len(data), 8)]


def hamming(first: bytes, second: bytes) -> int:
    if len(first) != len(second):
        raise ValueError("Las entradas deben tener la misma longitud.")
    return (int.from_bytes(first, "big") ^ int.from_bytes(second, "big")).bit_count()


def collect_evidence() -> dict:
    encrypted = des_encrypt_block(KEY, PLAIN)
    altered_plain = (int.from_bytes(PLAIN, "big") ^ 1).to_bytes(8, "big")
    altered_key = (int.from_bytes(KEY, "big") ^ 2).to_bytes(8, "big")
    subkeys = des_key_schedule(KEY)
    initial = permute(int.from_bytes(PLAIN, "big"), IP, 64)
    left, right = initial >> 32, initial & 0xFFFFFFFF
    trace = [{"round": 0, "left": f"{left:08X}", "right": f"{right:08X}", "subkey": "-"}]
    for number, key in enumerate(subkeys, 1):
        left, right = des_round(left, right, key)
        trace.append({"round": number, "left": f"{left:08X}", "right": f"{right:08X}", "subkey": f"{key:012X}"})

    message = b"ABCDEFGH" * 4
    iv1 = bytes.fromhex("0123456789ABCDEF")
    iv2 = bytes.fromhex("FEDCBA9876543210")
    ecb = des_ecb_encrypt(KEY, message)
    cbc1 = des_cbc_encrypt(KEY, message, iv1)
    cbc2 = des_cbc_encrypt(KEY, message, iv2)
    errors = {}
    for mode, ciphertext in (("ECB", ecb), ("CBC", cbc1)):
        changed = bytearray(ciphertext)
        changed[8] ^= 0x80  
        recovered = (des_ecb_decrypt(KEY, bytes(changed)) if mode == "ECB"
                     else des_cbc_decrypt(KEY, bytes(changed), iv1))
        distances = [hamming(message[i:i+8], recovered[i:i+8]) for i in range(0, len(message), 8)]
        errors[mode] = {"ciphertext_bit_changes": hamming(ciphertext, bytes(changed)),
                        "modified_ciphertext_blocks": blocks(bytes(changed)),
                        "recovered_blocks": blocks(recovered), "changed_bits_per_block": distances,
                        "changed_plaintext_blocks": [i+1 for i,d in enumerate(distances) if d]}
    return {
        "lab1": {"key": KEY.hex().upper(), "plaintext": PLAIN.hex().upper(),
                 "ciphertext": encrypted.hex().upper(),
                 "decrypted": des_decrypt_block(KEY, encrypted).hex().upper(),
                 "parity_valid": des_check_parity(KEY),
                 "subkeys": [f"{key:012X}" for key in subkeys], "trace": trace,
                 "first_f": f"{feistel_f(0xF0AAF0AA, subkeys[0]):08X}",
                 "avalanche_plain_bit": 64, "avalanche_key_bit": 63,
                 "avalanche_plain_cipher": des_encrypt_block(KEY, altered_plain).hex().upper(),
                 "avalanche_key_cipher": des_encrypt_block(altered_key, PLAIN).hex().upper(),
                 "avalanche_plain_distance": hamming(encrypted, des_encrypt_block(KEY, altered_plain)),
                 "avalanche_key_distance": hamming(encrypted, des_encrypt_block(altered_key, PLAIN))},
        "lab2": {"message_ascii": message.decode(), "key": KEY.hex().upper(),
                 "plaintext_blocks_with_padding": blocks(pkcs7_pad(message)),
                 "iv1": iv1.hex().upper(), "iv2": iv2.hex().upper(),
                 "ecb_blocks": blocks(ecb), "cbc_iv1_blocks": blocks(cbc1),
                 "cbc_iv2_blocks": blocks(cbc2), "different_ivs_differ": cbc1 != cbc2,
                 "error_bit": "primer bit de C2: byte 8, máscara 0x80", "errors": errors},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--salida", type=Path, default=ROOT / "results" / "experimentos.json")
    args = parser.parse_args()
    evidence = collect_evidence()
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Vector DES:", evidence["lab1"]["ciphertext"])
    print("Avalancha (texto/clave):", evidence["lab1"]["avalanche_plain_distance"], evidence["lab1"]["avalanche_key_distance"])
    print("\nBloque | Texto con padding | ECB              | CBC")
    data = evidence["lab2"]
    for i, (p,e,c) in enumerate(zip(data["plaintext_blocks_with_padding"], data["ecb_blocks"], data["cbc_iv1_blocks"]), 1):
        print(f"{i:6} | {p} | {e} | {c}")
    for mode in ("ECB", "CBC"):
        print(mode, "bits modificados en P1..P4:", data["errors"][mode]["changed_bits_per_block"])
    print("Evidencias guardadas en", args.salida.resolve())


if __name__ == "__main__":
    main()
