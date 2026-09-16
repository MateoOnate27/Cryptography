import argparse
from aeslib import AES
from aeslib.transformations import sub_bytes, shift_rows, mix_columns, add_round_key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bits',type=int,choices=(128,192,256),default=128)
    args = parser.parse_args()
    aes = AES(bytes(range(args.bits//8)))
    plaintext = bytes.fromhex('00112233445566778899aabbccddeeff')
    state = list(plaintext)
    print('Estado serializado por columnas. Cada dos caracteres representan un byte.')
    print('Entrada:',bytes(state).hex())
    add_round_key(state,aes.round_keys[0])
    print('Ronda 00 AddRoundKey:',bytes(state).hex())
    for number in range(1,aes.rounds+1):
        for operation in (sub_bytes,shift_rows):
            operation(state)
            print(f'Ronda {number:02} {operation.__name__:13}: {bytes(state).hex()}')
        if number != aes.rounds:
            mix_columns(state)
            print(f'Ronda {number:02} mix_columns  : {bytes(state).hex()}')
        add_round_key(state,aes.round_keys[number])
        print(f'Ronda {number:02} add_round_key: {bytes(state).hex()}')
    if bytes(state) != aes.encrypt_block(plaintext):
        raise RuntimeError('La traza y la interfaz pública no coinciden.')
    print('La traza coincide con encrypt_block.')


if __name__ == '__main__':
    main()
