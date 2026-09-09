from secrets import token_bytes

from deslib import des_decrypt_block, des_encrypt_block
from modes import des_cbc_decrypt, des_cbc_encrypt


def main():
    key = bytes.fromhex("133457799BBCDFF1")
    plaintext = bytes.fromhex("0123456789ABCDEF")
    ciphertext = des_encrypt_block(key, plaintext)
    print("Bloque original:", plaintext.hex().upper())
    print("Bloque cifrado: ", ciphertext.hex().upper())
    print("Bloque recuperado:", des_decrypt_block(key, ciphertext).hex().upper())

    message = "Estoy aprendiendo DES paso a paso.".encode("utf-8")
    iv = token_bytes(8)  
    encrypted = des_cbc_encrypt(key, message, iv)
    print("\nIV CBC:", iv.hex().upper())
    print("Mensaje cifrado:", encrypted.hex().upper())
    print("Mensaje recuperado:", des_cbc_decrypt(key, encrypted, iv).decode("utf-8"))


if __name__ == "__main__":
    main()
