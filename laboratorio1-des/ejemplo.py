from deslib import (
    des_check_parity,
    des_decrypt_block,
    des_encrypt_block,
    des_key_schedule,
)
from deslib.sboxes import sbox_lookup


def distancia_hamming(first: bytes, second: bytes) -> int:
    """Cuenta cuántos bits son distintos entre dos bloques."""
    difference = int.from_bytes(first, "big") ^ int.from_bytes(second, "big")
    return difference.bit_count()


def obtener_resultados() -> dict:
    key = bytes.fromhex("133457799BBCDFF1")
    plaintext = bytes.fromhex("0123456789ABCDEF")
    ciphertext = des_encrypt_block(key, plaintext)
    recovered = des_decrypt_block(key, ciphertext)
    subkeys = des_key_schedule(key)

    changed_plaintext = bytearray(plaintext)
    changed_plaintext[-1] ^= 0x01
    plain_cipher = des_encrypt_block(key, bytes(changed_plaintext))

    changed_key = bytearray(key)
    changed_key[-1] ^= 0x02
    key_cipher = des_encrypt_block(bytes(changed_key), plaintext)

    return {
        "clave": key.hex().upper(),
        "texto": plaintext.hex().upper(),
        "cifrado": ciphertext.hex().upper(),
        "recuperado": recovered.hex().upper(),
        "paridad_correcta": des_check_parity(key),
        "s1_100101": sbox_lookup(0, 0b100101),
        "subclaves": [f"{subkey:012X}" for subkey in subkeys],
        "texto_modificado": bytes(changed_plaintext).hex().upper(),
        "clave_modificada": bytes(changed_key).hex().upper(),
        "cifrado_texto_modificado": plain_cipher.hex().upper(),
        "cifrado_clave_modificada": key_cipher.hex().upper(),
        "avalancha_texto": distancia_hamming(ciphertext, plain_cipher),
        "avalancha_clave": distancia_hamming(ciphertext, key_cipher),
    }


def mostrar_resultados(data: dict) -> None:
    print("LABORATORIO 1 - DES")
    print("Clave:       ", data["clave"])
    print("Texto:       ", data["texto"])
    print("Cifrado:     ", data["cifrado"])
    print("Recuperado:  ", data["recuperado"])
    print("Paridad impar:", data["paridad_correcta"])
    print(f"S1(100101): {data['s1_100101']:04b}")
    print("\nSUBCLAVES")
    for number, subkey in enumerate(data["subclaves"], 1):
        print(f"k{number:02}: {subkey}")
    print("\nEFECTO AVALANCHA")
    print("Al cambiar un bit del texto:", data["avalancha_texto"], "bits cambian.")
    print("Al cambiar un bit efectivo de clave:", data["avalancha_clave"], "bits cambian.")


if __name__ == "__main__":
    mostrar_resultados(obtener_resultados())
