from aeslib import AES
from aeslib.transformations import sub_bytes, shift_rows, mix_columns, add_round_key
from tests.vectors import FIPS_VECTORS, PLAIN


def show_state(label, state):
    print('\n'+label)
    for row in range(4):
        print(' '.join(f'{state[4*column+row]:02X}' for column in range(4)))


def main():
    print('EJERCICIO 1: AES-128, AES-192 y AES-256')
    print('Bloque de entrada:',PLAIN.hex().upper())
    for key, expected in FIPS_VECTORS:
        aes = AES(key)
        encrypted = aes.encrypt_block(PLAIN)
        recovered = aes.decrypt_block(encrypted)
        print(f'\nAES-{aes.key_bits}: {aes.rounds} rondas')
        print('Clave:      ',key.hex().upper())
        print('Cifrado:    ',encrypted.hex().upper())
        print('Esperado:   ',expected.upper())
        print('Recuperado: ',recovered.hex().upper())
        print('Correcto:   ',encrypted.hex()==expected and recovered==PLAIN)

    aes = AES(bytes(range(16)))
    state = list(PLAIN)
    show_state('AES-128: estado de entrada, ordenado por columnas',state)
    add_round_key(state,aes.round_keys[0])
    show_state('AddRoundKey inicial',state)
    for operation in (sub_bytes,shift_rows,mix_columns):
        operation(state)
        show_state(operation.__name__,state)
    add_round_key(state,aes.round_keys[1])
    show_state('AddRoundKey: fin de la primera ronda',state)
    print('\nPrimera ronda. AES-128 ejecuta diez.')


if __name__ == '__main__':
    main()
