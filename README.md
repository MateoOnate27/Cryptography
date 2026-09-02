# Cryptography
# Data Encryption Standard (DES) - Laboratory 1

This repository contains a from-scratch implementation of the **Data Encryption Standard (DES)** symmetric block cipher library, developed following the official FIPS 46 specification and the course lecture materials.

The design strictly avoids external cryptographic libraries or third-party dependencies for the cryptographic core, relying entirely on pure bit-level operations, permutations, and substitution tables.

## Repository Structure

* `des.py`: Source code containing the core DES implementation (permutations, key schedule, Feistel network, S-Boxes, and encryption/decryption routines).
* `test_des.py`: Automated unit test suite verifying mathematical accuracy against standard NIST test vectors.
* `README.md`: Setup, architecture overview, and execution guide.

## Architecture and Implemented Components

The DES library adheres to the standard structural stages of the cipher:

1. *Initial and Final Permutations ($IP$ and $IP^{-1}$):* Bitwise rearrangement applied to the 64-bit block at the input and output stages of the cipher.
2. *Key Schedule Generator:*
   * Strips the 8 parity bits from the original 64-bit key via $PC-1$, leaving a 56-bit effective key.
   * Splits the 56 bits into two 28-bit halves, $C_0$ and $D_0$.
   * Performs circular left shifts ($LS_i$) by 1 or 2 bit positions depending on the round index.
   * Selects and compresses the halves into a 48-bit subkey for each of the 16 rounds using $PC-2$.
3. *Feistel Network (16 Rounds):*
   * Splits the permuted block into 32-bit left ($L$) and right ($R$) halves.
   * Expands the 32-bit $R$ register to 48 bits using the expansion table $E$.
   * Performs a bitwise XOR between $E(R)$ and the 48-bit round subkey.
   * Evaluates the non-linear substitution using the 8 S-Boxes ($S_1$ to $S_8$), mapping 48 bits back down to 32 bits.
   * Applies the internal permutation $P$ to provide diffusion across rounds.
4. *Symmetric Decryption:*
   * Reuses the same Feistel architecture by reversing the round key application order ($K_{16} \to K_1$).

## Environment Requirements

* *Python:* Version 3.8 or higher.
* *Dependencies:* None. Built exclusively with Python standard built-in modules and `unittest`.

## Usage Instructions

### 1. Clone the Repository

git clone [https://github.com/MateoOnate27/Cryptography.git](https://github.com/MateoOnate27/Cryptography.git)
cd Cryptography

### 2. Run the Interactive Trace (Step-by-Step Execution)
To inspect intermediate states across all 16 Feistel rounds, round subkeys, and the final register swap:

**python des.py**

Expected terminal output:

-----------------------------------------------------------------------
INICIANDO CIFRADO

Entrada original (64 bits): 0123456789ABCDEF

Tras Permutación Inicial (IP): L0=CC00CCFF | R0=F0AAF0AA

Ronda 01 | Subclave K01: 1B02EFFC7072 | L01: F0AAF0AA | R01: 4AC04B14

Ronda 16 | Subclave K16: A297DBAB49B3 | L16: 23EF266B | R16: 43297FAD

Pre-salida (R16 + L16 invertidos): 43297FAD23EF266B

Salida final tras IP^-1: 85E813540F0AB405

------------------------------------------------------------------------

### 3. Run the Automated Test Suite
To run the automated unit tests against standard test vectors:

**python -m unittest test_des.py -v**

Expected output:

test_vector_ceros (test_des.TestDES) ... ok

test_vector_nist_estandar (test_des.TestDES) ... ok


----------------------------------------------------------------------
Ran 2 tests in 0.002s

OK
