# Permutación Inicial (IP)
IP_TABLE = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]

# Permutación Inversa (IP-1)
IP_INV_TABLE = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25
]

# Matriz de Expansión (E)
E_TABLE = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]

# Permutación Interna (P)
P_TABLE = [
    16, 7, 20, 21, 29, 12, 28, 17,
    1, 15, 23, 26, 5, 18, 31, 10,
    2, 8, 24, 14, 32, 27, 3, 9,
    19, 13, 30, 6, 22, 11, 4, 25
]

# Permuted Choice 1 (PC-1) - Reduce de 64 a 56 bits
PC1_TABLE = [
    57, 49, 41, 33, 25, 17, 9, 1,
    58, 50, 42, 34, 26, 18, 10, 2,
    59, 51, 43, 35, 27, 19, 11, 3,
    60, 52, 44, 36, 63, 55, 47, 39,
    31, 23, 15, 7, 62, 54, 46, 38,
    30, 22, 14, 6, 61, 53, 45, 37,
    29, 21, 13, 5, 28, 20, 12, 4
]

# Permuted Choice 2 (PC-2) - Selecciona 48 bits de los 56
PC2_TABLE = [
    14, 17, 11, 24, 1, 5, 3, 28,
    15, 6, 21, 10, 23, 19, 12, 4,
    26, 8, 16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55, 30, 40,
    51, 45, 33, 48, 44, 49, 39, 56,
    34, 53, 46, 42, 50, 36, 29, 32
]

# Rotaciones circulares por ronda
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

# Cajas de Sustitución (S-Boxes)
S_BOXES = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
    ],
    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 5, 9, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
    ]
]


def permutar(bloque_bits, tabla):
    return ''.join([bloque_bits[i - 1] for i in tabla])

def xor(bits1, bits2):
    return ''.join(['1' if b1 != b2 else '0' for b1, b2 in zip(bits1, bits2)])

def rotar_izquierda(bits, posiciones):
    return bits[posiciones:] + bits[:posiciones]


def generar_subclaves(clave_64bits):
    subclaves = []
    
    clave_56bits = permutar(clave_64bits, PC1_TABLE)
    
    C, D = clave_56bits[:28], clave_56bits[28:]
    
    for shift in SHIFTS:
        C = rotar_izquierda(C, shift)
        D = rotar_izquierda(D, shift)
        
        subclave = permutar(C + D, PC2_TABLE)
        subclaves.append(subclave)
        
    return subclaves

def procesar_sboxes(bits_48):
    salida_32bits = ""
    
    for i in range(8):
        bloque_6bits = bits_48[i*6 : (i+1)*6]
        
        fila = int(bloque_6bits[0] + bloque_6bits[5], 2)
        
        columna = int(bloque_6bits[1:5], 2)
        
        valor_sbox = S_BOXES[i][fila][columna]
        
        salida_32bits += format(valor_sbox, '04b')
        
    return salida_32bits

def funcion_feistel(R, subclave):
    R_expandido = permutar(R, E_TABLE)
    
    xored = xor(R_expandido, subclave)
    
    resultado_sboxes = procesar_sboxes(xored)
    
    return permutar(resultado_sboxes, P_TABLE)

def des_procesar_bloque(texto_64bits, clave_64bits, descifrar=False):
    subclaves = generar_subclaves(clave_64bits)
    
    if descifrar:
        subclaves.reverse()
        
    bloque = permutar(texto_64bits, IP_TABLE)
    L, R = bloque[:32], bloque[32:]
    
    for i in range(16):
        L_siguiente = R
        R_siguiente = xor(L, funcion_feistel(R, subclaves[i]))
        L, R = L_siguiente, R_siguiente
        
    bloque_final = R + L
    return permutar(bloque_final, IP_INV_TABLE)

def hex_a_bin(hex_str):
    return bin(int(hex_str, 16))[2:].zfill(64)

def bin_a_hex(bin_str):
    return hex(int(bin_str, 2))[2:].upper().zfill(16)

def des_procesar_bloque(texto_64bits, clave_64bits, descifrar=False):
    modo = "DESCIFRADO" if descifrar else "CIFRADO"
    print(f"\nINICIANDO {modo}")
    
    subclaves = generar_subclaves(clave_64bits)
    if descifrar:
        subclaves.reverse()
        
    print(f"[*] Entrada original (64 bits): {bin_a_hex(texto_64bits)}")
    
    bloque = permutar(texto_64bits, IP_TABLE)
    L, R = bloque[:32], bloque[32:]
    print(f"[*] Tras Permutación Inicial (IP): L0={bin_a_hex(L.ljust(64, '0'))[:8]} | R0={bin_a_hex(R.ljust(64, '0'))[:8]}")
    print("-" * 65)
    
    for i in range(16):
        num_ronda = i + 1
        L_siguiente = R
        f_out = funcion_feistel(R, subclaves[i])
        R_siguiente = xor(L, f_out)
        
        L, R = L_siguiente, R_siguiente
        
        l_hex = f"{int(L, 2):08X}"
        r_hex = f"{int(R, 2):08X}"
        k_hex = f"{int(subclaves[i], 2):012X}"
        
        print(f"Ronda {num_ronda:02d} | Subclave K{num_ronda:02d}: {k_hex} | L{num_ronda:02d}: {l_hex} | R{num_ronda:02d}: {r_hex}")
        
    print("-" * 65)
    
    bloque_final = R + L
    resultado = permutar(bloque_final, IP_INV_TABLE)
    
    print(f"Pre-salida (R16 + L16 invertidos): {bin_a_hex(bloque_final)}")
    print(f"Salida final tras IP^-1: {bin_a_hex(resultado)}")
    return resultado

if __name__ == "__main__":
    texto_plano_hex = "0123456789ABCDEF"
    clave_hex       = "133457799BBCDFF1"
    
    texto_bin = hex_a_bin(texto_plano_hex)
    clave_bin = hex_a_bin(clave_hex)
    
    criptograma_bin = des_procesar_bloque(texto_bin, clave_bin, descifrar=False)
    
    recuperado_bin = des_procesar_bloque(criptograma_bin, clave_bin, descifrar=True)
