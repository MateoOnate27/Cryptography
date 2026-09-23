# Cryptography Laboratories 1, 2, 3, and 4: DES, AES, and RSA Implementation, Cryptanalysis, and Performance

**Mateo Oñate**  
School of Mathematical and Computational Sciences, Yachay Tech  
Email: mateo.onate@yachaytech.edu.ec

This repository contains four cryptography laboratories. In Laboratory 1, we implement the Data Encryption Standard (DES) as a block cipher library. In Laboratory 2, we extend that DES library with message padding, ECB and CBC modes, and sequential and parallel key searches. In Laboratory 3, we implement AES-128, AES-192, and AES-256 from scratch and measure their encryption and decryption performance with 1, 10, and 100 MB inputs. In Laboratory 4, we implement Trial Division, Fermat factorization, and Pollard's Rho to recover small RSA private keys and compare factorization performance.

The cryptographic cores perform their own finite-field operations, permutations, substitutions, round transformations, and key scheduling. The DES code does not call an external DES implementation, and the AES core does not call an external AES implementation. The implementations follow the course material and the corresponding NIST specifications.

## Repository Structure

The repository root contains this README and the four laboratory directories:

| Directory or file | Purpose |
|---|---|
| `laboratorio1-des/deslib/` | DES implementation, tables, key schedule, Feistel rounds, and public API |
| `laboratorio1-des/ejemplo.py` | Known-vector demonstration, sixteen subkeys, parity, and avalanche results |
| `laboratorio1-des/tests/` | Laboratory 1 unit tests |
| `laboratorio1-des/verificar.py` | Runs tests and saves experimental evidence |
| `laboratorio1-des/resultados/` | Laboratory 1 test records and example results |
| `laboratorio2-des/deslib/` | The unchanged DES library from Laboratory 1 |
| `laboratorio2-des/modes/` | PKCS#7 padding and ECB/CBC encryption and decryption |
| `laboratorio2-des/attacks/` | Reduced key-space construction and sequential/parallel search |
| `laboratorio2-des/examples/` | Cipher demonstrations and mode experiments |
| `laboratorio2-des/benchmarks/` | Repeated timing, hardware information, and performance calculations |
| `laboratorio2-des/tests/` | DES, mode, attack, and metric tests |
| `laboratorio2-des/results/` | Recorded measurements and experimental evidence |
| `laboratorio2-des/report/` | Technical Report and performance figures |
| `laboratorio3-aes/aeslib/` | AES finite-field arithmetic, transformations, key expansion, and block cipher implementation |
| `laboratorio3-aes/tests/` | 30 automatic tests, NIST vectors, round-trip checks, and benchmark validation |
| `laboratorio3-aes/benchmarks/` | Performance benchmark, environment records, integrity checks, CSV export, and summaries |
| `laboratorio3-aes/examples/` | Round traces and optional comparison with an external AES implementation |
| `laboratorio3-aes/results/` | Validation evidence and complete benchmark datasets |
| `laboratorio3-aes/report/` | Technical report, figures, and the exact dataset used by the report |
| `laboratorio3-aes/ejercicio1.py` to `ejercicio4.py` | Entry points for the four Laboratory 3 exercises |
| `laboratorio4-rsa/laboratorio4.py` | Single entry point, keyboard input, and sequential execution of all seven exercises |
| `laboratorio4-rsa/factorizacion.py` | GCD, integer square root, primality checks, Trial Division, Fermat, and Pollard Rho |
| `laboratorio4-rsa/rsa.py` | Modular inverse, modular exponentiation, key recovery, encryption, and decryption |
| `laboratorio4-rsa/test_laboratorio.py` | 21 automatic tests for mathematics, factorization, RSA, and generated cases |
| `laboratorio4-rsa/experimentos.py` | Modulus generation, repeated timings, and the Fermat prime-distance experiment |
| `laboratorio4-rsa/resultados.json` | Current execution results, machine metadata, recovery checks, and individual measurements |
| `laboratorio4-rsa/resultados_referencia.json` | Assistant-environment reference measurements supplied with the code package |
| `laboratorio4-rsa/Lab_4_RSA.pdf` | Technical report with factor recovery, timing tables, figures, and security analysis |
| `README.md` | General architecture and execution guide |

Each laboratory has its own working directory. Run its commands from that directory so Python resolves the corresponding modules.

## Architecture and Implemented Components

### Laboratory 1: DES Block Cipher

DES processes one 64 bit block with a key represented by 64 bits. Eight key bits provide parity, leaving 56 effective key bits.

1. **Initial and final permutations:** IP rearranges the input bits. The inverse permutation rearranges the final output.
2. **Key schedule:** PC-1 selects and rearranges the 56 effective bits. The algorithm splits them into two 28 bit halves, rotates each half, and applies PC-2 to generate a 48 bit subkey for each of sixteen rounds.
3. **Feistel network:** Each round expands the right half to 48 bits, applies XOR with the subkey, evaluates the eight S-boxes, and permutes the resulting 32 bits before updating both halves.
4. **Decryption:** The same Feistel construction applies the subkeys in reverse order.
5. **Validation:** Tests check intermediate operations, the known ciphertext, message recovery, parity, invalid inputs, and avalanche examples.

### Laboratory 2: Modes and Key Search

1. **PKCS#7 padding:** Completes the final 8 byte block and validates the padding before removal.
2. **ECB:** Encrypts each block independently with the same key.
3. **CBC:** Combines each plaintext block with the preceding ciphertext block through XOR. An 8 byte initialization vector starts the chain.
4. **Mode experiments:** Compare repeated blocks, different IV values, and a single modified ciphertext bit.
5. **Reduced key space:** Fixes 40 effective bits and varies 16, producing 65,536 candidates with odd parity.
6. **Sequential and parallel search:** Tests known plaintext/ciphertext pairs and distributes separate intervals among CPU processes.
7. **Performance analysis:** Calculates throughput, speedup, efficiency, and a mathematical DES-56 projection.


### Laboratory 3: AES Implementation and Performance

AES processes 128 bit blocks. The key size determines the number of rounds and the amount of expanded key material.

| Version | Key bytes | Key words, Nk | Rounds, Nr | Round keys |
|---|---:|---:|---:|---:|
| AES-128 | 16 | 4 | 10 | 11 |
| AES-192 | 24 | 6 | 12 | 13 |
| AES-256 | 32 | 8 | 14 | 15 |

1. **Finite-field arithmetic:** `aeslib/gf.py` implements byte multiplication in GF(2^8) with the AES irreducible polynomial represented by `0x11B`.
2. **Substitution tables:** `aeslib/tables.py` contains the standard S-box and inverse S-box. It also generates the multiplication tables needed by MixColumns and InvMixColumns from the finite-field routine.
3. **State transformations:** `aeslib/transformations.py` implements SubBytes, ShiftRows, MixColumns, AddRoundKey, and their inverse operations. The 16-byte state follows FIPS 197 column order with index `4 * column + row`.
4. **Key expansion:** `aeslib/key_schedule.py` supports 16-, 24-, and 32-byte keys. It produces 44, 52, or 60 expanded words. AES-256 includes the extra SubWord operation required when the word index modulo eight equals four.
5. **Block encryption and decryption:** `aeslib/aes.py` implements all three AES variants. Encryption omits MixColumns in the final round. Decryption applies the inverse transformations in the corresponding order.
6. **Bulk interface:** The benchmark interface processes data in independent 16-byte blocks. It adds no padding because the laboratory measures the AES core rather than a complete file-encryption format.
7. **Validation:** The suite checks all 65,536 byte products in the finite field, the S-box definition, direct and inverse transformations, key expansion checkpoints, NIST vectors, deterministic random round trips, invalid inputs, and benchmark calculations.
8. **Performance evaluation:** The benchmark measures encryption and decryption for AES-128, AES-192, and AES-256 with 1, 10, and 100 MB inputs. Three repetitions for each combination produce 27 encryption/decryption pairs and 54 timed operations.

### Laboratory 4: RSA Factorization Attacks

RSA forms the public modulus as `n = p * q`, where p and q are distinct primes. The attacks receive n and attempt to recover its factors. After factorization, we calculate the totient and private exponent, decrypt the ciphertext, and verify the result through encryption.

1. **Trial Division:** Checks 2, then odd divisors through the integer square root of n. An exact division identifies a factor.
2. **Fermat factorization:** Starts at the ceiling of the square root and searches for `n = a*a - b*b`. The factors are `a-b` and `a+b`.
3. **Pollard Rho:** Advances two positions through a modular sequence and calculates `gcd(abs(x-y), n)`. It restarts with different parameters when the GCD equals n.
4. **Private-key recovery:** Calculates `phi = (p-1)*(q-1)` and the modular inverse `d = e^(-1) mod phi`. Decryption recovers m, and encryption checks the original ciphertext.
5. **Validation:** Tests cover the mathematical operations, all three attacks, factor products, RSA consistency, invalid inputs, and the Rho restart.
6. **Performance evaluation:** Four generated moduli of 16, 20, 24, and 28 bits, three algorithms, and three repetitions produce 36 timed factorizations.
7. **Prime-distance experiment:** Two additional 28-bit moduli compare close and separated primes. Three repetitions per case record Fermat iterations and execution times.

The algorithms do not call a factoring library or receive the prime factors as inputs. The project keeps factorization, RSA recovery, tests, and experiments in separate files. One main script runs the exercises in order without a menu.

## Environment Requirements

- **Python:** Python 3.11 or later is the recommended common version for the repository. Laboratory 3 also supports Python 3.9 or later, including compatible PyPy versions.
- **Cryptographic cores, examples, benchmarks, and required tests:** Python standard library.
- **Graphs and PDF reports:** Matplotlib and ReportLab, listed in the corresponding laboratory requirements files.
- **Optional AES reference comparison:** The `cryptography` package is required only for `laboratorio3-aes/examples/validacion_externa.py`. It never participates in the AES core or the formal benchmark.
- **Operating system:** The Laboratory 2 parallel implementation follows the `spawn` process model and includes entry-point guards for Windows compatibility. Laboratory 3 runs sequentially in one process for its required benchmark.

Laboratory 4 supports Python 3.8 or later and requires only the standard library for its seven exercises. It runs sequentially in one process. Its separate LaTeX report compiles with pdfLaTeX and the supplied figures.

On Windows, replace `python` with `py` if that is the available command. On systems exposing Python as `python3`, substitute that command instead.

## Usage Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/MateoOnate27/Cryptography.git
cd Cryptography
python --version
```

The commands below follow the directory names listed in Repository Structure.

### 2. Run Laboratory 1

From the repository root:

```bash
cd laboratorio1-des
python ejemplo.py
```

The example prints the key, original block, ciphertext, recovered block, parity result, sixteen subkeys, and two avalanche measurements.

Expected main values:

```text
Clave:        133457799BBCDFF1
Texto:        0123456789ABCDEF
Cifrado:      85E813540F0AB405
Recuperado:   0123456789ABCDEF
Paridad impar: True
S1(100101): 1000
```

Additional checkpoints:

| Check | Expected result |
|---|---|
| First subkey K1 | `1B02EFFC7072` |
| Last subkey K16 | `CB3D8B0E17F5` |
| Changed ciphertext bits after the selected plaintext-bit flip | 37 |
| Changed ciphertext bits after the selected effective-key-bit flip | 32 |

These avalanche counts describe the particular bit changes in `ejemplo.py`. They are not fixed values for every input.

#### Run the Laboratory 1 Tests

From `laboratorio1-des`:

```bash
python -m unittest discover -s tests -v
```

The suite contains 19 tests, including recovery of 32 different blocks. Successful tests report `ok`, and the suite ends with `OK`. Execution time depends on the computer.

| Laboratory 1 component | Implementation | Verification |
|---|---|---|
| Permutations and indexing | `deslib/permutation.py`, `deslib/tables.py` | IP, inverse IP, and bit-position tests |
| S-boxes | `deslib/sboxes.py` | Known S1 example and output-width tests |
| Subkey generation | `deslib/key_schedule.py` | Rotation and subkey tests |
| Feistel function and round | `deslib/feistel.py` | Expansion, substitution, function, and round tests |
| Complete cipher | `deslib/des_core.py`, `deslib/api.py` | Known-vector encryption/decryption and final-swap tests |
| Parity and avalanche | `ejemplo.py`, `tests/test_des.py` | Effective-bit, parity-bit, and avalanche checks |

To run the tests and save evidence:

```bash
python verificar.py
```

This updates `resultados/pruebas.txt`, `resultados/verificacion.json`, `resultados/ejemplo.txt`, and `resultados/ejemplo.json`.

### 3. Run Laboratory 2

From `laboratorio1-des`, switch to the second laboratory:

```bash
cd ../laboratorio2-des
python -m examples.demo_cifrado
```

This example first checks single-block DES and then encrypts and decrypts a complete CBC message. It generates a new IV for the CBC operation, so the CBC ciphertext normally differs between executions.

The recovered message is:

```text
Estoy aprendiendo DES paso a paso.
```

#### Run the Mode Experiments

```bash
python -m examples.experimentos
```

The command performs the repeated-block, IV, and error-propagation experiments. It prints the block comparison and error counts, then writes the complete evidence to `results/experimentos.json`, including both IV results.

Expected observations:

| Experiment | Expected observation |
|---|---|
| Repeated plaintext blocks | The first four ECB blocks equal `0EE11BD2808EF0A1` |
| CBC on the same repeated message | The first four CBC blocks differ in this experiment |
| Different IV values | CBC produces different ciphertext for the same key and message |
| One modified bit in C2, ECB | Plaintext differences: `[0, 39, 0, 0]` |
| One modified bit in C2, CBC | Plaintext differences: `[0, 32, 1, 0]` |

The message contains four blocks of `ABCDEFGH`. PKCS#7 adds a fifth block. The values 39 and 32 are trial-specific, while the single corresponding change in the next CBC plaintext block follows from XOR.

#### Run the Key-Search Demonstrations

Sequential search:

```bash
python -m examples.demo_ataque --bits 16 --workers 1
```

Parallel search:

```bash
python -m examples.demo_ataque --bits 16 --workers 2
python -m examples.demo_ataque --bits 16 --workers 4
```

Select a process count supported by the computer. All three demonstrations target candidate **49,152**, three quarters of the way through the 16 bit space. The sequential search tests **49,153** candidates, including candidate zero.

Each command prints the recovered key, candidate position, attempt count, elapsed time, and throughput. Parallel attempt counts vary because workers stop after another worker finds a match.

These demonstrations perform actual searches. Their target position differs from the formal benchmark, which places the target at candidate **65,535**.

### 4. Check the Laboratory 2 Exercises

Run the following commands from `laboratorio2-des`. Some exercises share an experiment or test because they examine different properties of the same implementation.

| Exercise | Topic | Execution or evidence |
|---|---|---|
| 1 | PKCS#7 padding | `python -m unittest tests.test_modes.PaddingTests -v` |
| 2 | ECB encryption and decryption | `python -m unittest tests.test_modes.ModeTests.test_ecb_and_cbc_round_trips -v` |
| 3 | CBC chaining | `python -m unittest tests.test_modes.ModeTests.test_modes_use_expected_chaining -v` |
| 4 | Repeated blocks | `python -m examples.experimentos` |
| 5 | Initialization vector | `python -m unittest tests.test_modes.ModeTests.test_different_ivs -v` |
| 6 | Error propagation | `python -m unittest tests.test_modes.ModeTests.test_error_propagation -v` |
| 7 | Known-plaintext attack and candidate construction | `python -m unittest tests.test_attacks -v` |
| 8 | Sequential search | `python -m examples.demo_ataque --bits 16 --workers 1` |
| 9 | Parallel search | `python -m examples.demo_ataque --bits 16 --workers 4` |
| 10 | Throughput, speedup, and efficiency | Recorded CSV tables and report graphs, described below |
| 11 | DES-56 extrapolation | The `des56` section of `results/mi_equipo/benchmark.json` and the report |
| 12 | Security analysis | `docs/PREGUNTAS_RESUELTAS.md` and the report security discussion |

Exercises 10 and 11 calculate from measured rates. Exercise 12 interprets the evidence and answers the seven security questions. It is not a separate encryption operation or a general security certification.

#### Run the Full Laboratory 2 Test Suite

```bash
python -m unittest discover -s tests -v
```

The suite contains 44 tests covering DES, padding, ECB/CBC, candidate mapping, sequential and parallel recovery, interval boundaries, and metric calculations.

To run the tests and update their records and the mode experiments:

```bash
python verificar.py
```

This updates `results/pruebas.txt`, `results/pruebas.json`, and `results/experimentos.json`. It does not run the full timing benchmark.

### 5. Inspect or Repeat the 16 Bit Benchmark

The recorded student measurements are available in:

| File | Contents |
|---|---|
| `results/mi_equipo/benchmark.json` | Hardware, settings, individual runs, summary, and DES-56 estimates |
| `results/mi_equipo/mediciones.csv` | One row per recorded execution |
| `results/mi_equipo/resumen.csv` | Aggregate performance for each process count |
| `results/originales_estudiante/` | The complete original files submitted by the student |

The report analyzes only the nine 16 bit runs, following the instructor's scope. The separate `results/verificacion_entorno/` directory contains earlier assistant-environment checks, not student hardware measurements.

To collect a new set without overwriting the recorded student results:

```bash
python -m benchmarks.benchmark_bruteforce --bits 16 --repeticiones 3 --max-workers 4 --origen equipo-estudiante --salida results/nueva_medicion_16
```

This runs three repetitions for each supported selected process count, up to four processes. It records actual timings on the current computer.

To resume an interrupted run:

```bash
python -m benchmarks.benchmark_bruteforce --bits 16 --repeticiones 3 --max-workers 4 --origen equipo-estudiante --salida results/nueva_medicion_16 --reanudar
```

Completed repetitions remain saved. An interrupted repetition starts again. Always include `--bits 16` for this laboratory, since the general benchmark module also supports larger spaces.


### 6. Run Laboratory 3

From `laboratorio2-des`, switch to the AES laboratory:

```bash
cd ../laboratorio3-aes
python --version
```

Laboratory 3 supports AES-128, AES-192, and AES-256. All three versions process 16-byte blocks, while the key length changes the key schedule and round count.

Optional plotting and report dependencies can be installed with:

```bash
python -m pip install -r requirements.txt
```

The core implementation and the required 30-test suite do not require third-party cryptographic libraries.

#### Exercise 1: Run the AES Core

```bash
python ejercicio1.py
```

The program encrypts and decrypts the standard FIPS test input with all three key sizes. It also prints the first AES-128 round step by step so the state changes can be followed without reading the full cipher loop first.

For plaintext `00112233445566778899AABBCCDDEEFF` and incrementing key bytes beginning at `00`, the expected ciphertexts are:

| Version | Expected ciphertext | Rounds |
|---|---|---:|
| AES-128 | `69C4E0D86A7B0430D8CDB78070B4C55A` | 10 |
| AES-192 | `DDA97CA4864CDFE06EAF70A0EC0D7191` | 12 |
| AES-256 | `8EA2B7CA516745BFEAFC49904B496089` | 14 |

To inspect every encryption round for a selected version:

```bash
python -m examples.traza --bits 128
python -m examples.traza --bits 192
python -m examples.traza --bits 256
```

#### Exercise 2: Run the Laboratory 3 Validation

```bash
python ejercicio2.py
```

This command runs the full 30-test suite and writes the validation evidence to `results/validacion/pruebas.txt` and `results/validacion/pruebas.json`. A successful execution ends with `OK`.

The equivalent direct command is:

```bash
python -m unittest discover -s tests -v
```

The required suite checks:

| Area | Verification |
|---|---|
| GF(2^8) arithmetic | All 65,536 byte products, known examples, and generated lookup values |
| S-box | Every value against its mathematical construction |
| AES transformations | SubBytes, ShiftRows, MixColumns, AddRoundKey, inverse pairs, and FIPS intermediate states |
| Key schedule | AES-128, AES-192, and AES-256 checkpoints and expansion lengths |
| Complete cipher | Published NIST vectors and deterministic random encryption/decryption round trips |
| Input validation | Unsupported key sizes and invalid block/data lengths |
| Benchmark support | Data sizes, summaries, sample standard deviation, required grid, and invalid measurement detection |

The package also contains an optional comparison with an independent library. It is separate from the AES implementation and is not required for the standalone core:

```bash
python -m pip install cryptography
python -m examples.validacion_externa
```

The optional comparison checks 768 blocks in each direction across 48 keys and writes `results/validacion/referencia_externa.json`.

#### Exercise 3: Measure AES Performance

To collect the complete required dataset on the current computer:

```bash
python ejercicio3.py --origin equipo-estudiante --output results/mi_equipo
```

The default experiment follows the laboratory grid:

- AES-128, AES-192, and AES-256.
- 1, 10, and 100 MB inputs.
- Three repetitions for each key-size and input-size combination.
- 27 encryption/decryption pairs.
- 54 timed operations in total.

The benchmark records encryption time, decryption time, throughput in decimal MB/s, means, sample standard deviations, CPU information, operating system, Python interpreter, source fingerprint, recovery checks, and SHA-256 checksums.

The timed interval includes output allocation, block handling, Python calls, and AES rounds. Data generation, key expansion, warm-up, correctness comparisons, hashing, console output, and disk writes stay outside the timed interval. Each AES object expands its key once before timing. A 1 MB encryption/decryption warm-up runs for every variant, and the AES order rotates across repetitions.

Every completed measurement is saved to:

| File | Contents |
|---|---|
| `results/mi_equipo/benchmark.json` | Complete metadata, settings, individual runs, validation state, and summaries |
| `results/mi_equipo/mediciones.csv` | One row per completed benchmark pair |
| `results/mi_equipo/resumen.csv` | Aggregate time and throughput for every AES and size combination |

To continue an interrupted complete measurement:

```bash
python ejercicio3.py --origin equipo-estudiante --output results/mi_equipo --resume
```

Resume requires the same source files, machine metadata, interpreter, and benchmark settings. A partially completed encryption/decryption pair starts again, while completed pairs remain stored.

For a short timing demonstration:

```bash
python ejercicio3.py --sizes-mb 0.016 --repetitions 1 --origin demostracion --output results/demo
```

The short demonstration checks the workflow but does not replace the required 1, 10, and 100 MB experiment.

If PyPy is installed, a separate complete dataset can be collected with:

```bash
pypy3 ejercicio3.py --origin equipo-estudiante --output results/mi_equipo_pypy
```

Keep measurements from different Python interpreters in separate result folders.

#### Exercise 4: Regenerate Tables, Figures, and the Report

To regenerate the report from the included reference measurements:

```bash
python ejercicio4.py --results results/entorno_asistente/benchmark.json
```

After collecting measurements on the personal computer:

```bash
python ejercicio4.py --results results/mi_equipo/benchmark.json
```

The generator recalculates the tables and analysis from the selected benchmark file. It rejects incomplete result grids, inconsistent rates, failed recovery checks, or results that do not match the expected source version.

#### Laboratory 3 Public API

```python
from aeslib import AES

key = bytes.fromhex('000102030405060708090A0B0C0D0E0F')
plaintext = bytes.fromhex('00112233445566778899AABBCCDDEEFF')

aes = AES(key)
ciphertext = aes.encrypt_block(plaintext)
recovered = aes.decrypt_block(ciphertext)

assert recovered == plaintext
```

The block interface requires exactly 16 bytes. The bulk interface requires a length that is a multiple of 16, accepts empty input, and adds no padding.

### 7. Run Laboratory 4

From `laboratorio3-aes`, switch to the RSA laboratory:

```bash
cd ../laboratorio4-rsa
python laboratorio4.py
```

If starting from the repository root, run `cd laboratorio4-rsa` first. No additional packages or menu selections are required.

The program first asks for n and runs the three factorization algorithms. It then asks for e and the ciphertext c before recovering the private key. Press Enter at each prompt to retain the laboratory example, or type different values from the course or generated for this practice.

```text
Módulo n [3233]:
Exponente público e [17]:
Texto cifrado c [2790]:
```

Expected recovery values for all three methods:

```text
p = 53
q = 61
phi = 3120
d = 2753
Private key = (3233, 2753)
Recovered message = 65
Ciphertext verification = True
```

The program prints Spanish labels. The factors appear in ascending order. The expected counters for this example are 27 divisor checks for Trial Division, 1 candidate check for Fermat, and 6 iterations for Pollard Rho, with no restarts. These counters describe different operations and do not represent equal computational costs.

#### Check the Seven Laboratory 4 Exercises

One execution of `python laboratorio4.py` performs the complete sequence:

| Exercise | Topic | Result |
|---|---|---|
| 1 | Trial Division | Factors of the entered n and divisor-check count |
| 2 | Fermat factorization | Factors of the same n and candidate-check count |
| 3 | Pollard Rho | Factors, iterations, and restart count |
| 4 | Private-key recovery | Totient, private exponent, message, and encryption check for all three methods |
| 5 | Automatic tests | 21 tests, with failure stopping the timing experiments |
| 6 | Factorization benchmark | Four generated bit sizes, three repetitions per method, and mean execution times |
| 7 | Distance between primes | Two 28-bit moduli, prime distances, Fermat iterations, and timing summaries |

Keyboard values affect Exercises 1–4. Exercises 6 and 7 generate their own inputs to satisfy the required comparisons. The 16-bit unknown-key restriction from Laboratory 2 does not apply to RSA modulus sizes.

#### Demonstrate Different Keyboard Inputs

Run the same script again and enter one of these course examples:

| n | e | Ciphertext c | Recovered factors | Private exponent d | Message m |
|---:|---:|---:|---|---:|---:|
| 3233 | 17 | 2790 | 53 and 61 | 2753 | 65 |
| 187 | 7 | 15 | 11 and 17 | 23 | 42 |
| 3233 | 17 | 855 | 53 and 61 | 2753 | 123 |

The ciphertext 855 belongs to a separate lecture example. It should not be confused with the required laboratory ciphertext 2790.

#### Run Only the Laboratory 4 Tests

From `laboratorio4-rsa`:

```bash
python -m unittest -v
```

The full laboratory execution also runs this suite before measurement. The restart test deliberately produces a GCD equal to n and checks whether Pollard Rho recovers after changing parameters.

#### Save and Interpret Laboratory 4 Results

A completed execution writes `resultados.json` beside the Python files. It includes the environment, approved-test count, RSA recovery results, 36 benchmark measurements, six prime-distance measurements, means, and sample standard deviations.

Times in JSON are in seconds. Console and report tables express them in milliseconds. Each new full execution replaces `resultados.json`, so preserve a copy before collecting another dataset if the previous measurements are needed.

The supplied `resultados_referencia.json` belongs to the assistant environment. The Laboratory 4 results summarized below come from the student's submitted `resultados.json`. The updated LaTeX report also analyzes that student dataset. Running the program creates new measurements but does not automatically update the PDF.

## Laboratory 2 Recorded Experimental Results

The submitted 16 bit benchmark ran on an **Intel Core i3-1005G1**, with **2 physical cores**, **4 logical processors**, **Windows 10**, and **Python 3.12.7**. Each process configuration includes three repetitions with target candidate 65,535.

| Processes | Mean time, s | Standard deviation, s | Mean tested keys | Keys/s | Speedup | Efficiency |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 36.063 | 2.107 | 65,536.0 | 1,817.3 | 1.000 | 100.0% |
| 2 | 24.725 | 0.695 | 65,536.0 | 2,650.6 | 1.459 | 72.9% |
| 4 | 22.006 | 0.036 | 65,386.7 | 2,971.4 | 1.639 | 41.0% |

Throughput divides total attempts by total time. Speedup divides the sequential mean time by the parallel mean time. Efficiency divides speedup by the number of processes.

Four processes reduced mean search time by approximately 39%. Parallel attempt counts vary with early stopping, so speedup describes time until recovery rather than a fixed amount of completed work in every run.

At the best recorded rate, complete DES-56 traversal projects to approximately **768,455 years**. The expected search time is approximately **384,227 years**, assuming a uniform target position and a constant rate. These calculations describe the measured Python implementation and hardware. The project does not execute a complete DES-56 search or benchmark specialized hardware.

## Laboratory 3 Recorded Experimental Results

The included Laboratory 3 reference dataset contains all 27 required encryption/decryption pairs and passed all 30 automatic tests before measurement. These measurements were collected in the assistant execution environment with PyPy 7.3.23, Python 3.11.15, on Linux. The recorded CPU is an Intel Xeon Platinum 8573C. The benchmark ran sequentially in one process. These values are reference measurements and are not measurements from Mateo's personal computer.

Each row below summarizes three repetitions. Throughput is calculated from the data size divided by the mean elapsed time.

| AES | Rounds | Size, MB | Encryption mean, s | Encryption SD, s | Encryption MB/s | Decryption mean, s | Decryption SD, s | Decryption MB/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 128 | 10 | 1 | 0.136 | 0.006 | 7.379 | 0.151 | 0.009 | 6.640 |
| 128 | 10 | 10 | 1.369 | 0.034 | 7.303 | 1.446 | 0.024 | 6.915 |
| 128 | 10 | 100 | 14.655 | 1.223 | 6.824 | 16.136 | 0.185 | 6.197 |
| 192 | 12 | 1 | 0.164 | 0.008 | 6.098 | 0.172 | 0.003 | 5.821 |
| 192 | 12 | 10 | 1.617 | 0.016 | 6.184 | 1.715 | 0.016 | 5.831 |
| 192 | 12 | 100 | 16.667 | 0.198 | 6.000 | 18.594 | 0.305 | 5.378 |
| 256 | 14 | 1 | 0.182 | 0.004 | 5.495 | 0.198 | 0.007 | 5.046 |
| 256 | 14 | 10 | 1.822 | 0.037 | 5.489 | 1.949 | 0.017 | 5.131 |
| 256 | 14 | 100 | 19.532 | 0.920 | 5.120 | 21.858 | 0.981 | 4.575 |

For the 100 MB input, mean encryption times were 14.655 seconds for AES-128, 16.667 seconds for AES-192, and 19.532 seconds for AES-256. The corresponding AES-192/AES-128 and AES-256/AES-128 time ratios were approximately 1.137 and 1.333. The round-count ratios are 1.2 and 1.4, so the measured runtime does not scale as an exact multiple of the round count. Python overhead, state handling, allocation, interpreter behavior, and scheduling also contribute to total time.

At 100 MB, the decryption/encryption time ratios were approximately 1.101 for AES-128, 1.116 for AES-192, and 1.119 for AES-256. In this implementation, InvMixColumns performs more table lookups per output byte than MixColumns, which contributes to the measured difference. The benchmark does not isolate that operation as a separate timing experiment.

The reference dataset stores the source fingerprint, complete recovery checks, and SHA-256 records for every completed run. To replace these reference numbers with personal hardware results, run Exercise 3 with `--origin equipo-estudiante`, then regenerate the report with Exercise 4.

## Laboratory 4 Recorded Experimental Results

The submitted execution passed **21 automatic tests** and completed on **September 23, 2026**, with **Python 3.12.7** and **Windows 10, build 19045**. The processor field records `Intel64 Family 6 Model 126 Stepping 5, GenuineIntel`. The export does not specify the commercial processor model.

Each benchmark row summarizes three repetitions. Both means and sample standard deviations below are in milliseconds.

| Bits of n | n | Trial mean, ms | Trial SD, ms | Fermat mean, ms | Fermat SD, ms | Rho mean, ms | Rho SD, ms |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 47083 | 0.008933 | 0.000321 | 0.001433 | 0.000252 | 0.005733 | 0.000681 |
| 20 | 732349 | 0.024167 | 0.003553 | 0.002733 | 0.000153 | 0.013467 | 0.000115 |
| 24 | 12277201 | 0.133300 | 0.033100 | 0.013167 | 0.004100 | 0.017267 | 0.000252 |
| 28 | 256796269 | 0.928667 | 0.358433 | 0.001500 | <0.000001 | 0.133867 | 0.000666 |

For the largest tested modulus, Fermat recorded the lowest mean time, **0.001500 ms**. Its factors are **15959** and **16091**, separated by **132**, and the algorithm finds them in one candidate check. Trial Division required 7980 divisor checks, while Pollard Rho required 114 iterations. This ranking applies to the measured case, not every RSA modulus.

Trial Division increased from 0.008933 ms at 16 bits to 0.928667 ms at 28 bits. Its 28-bit measurements ranged from 0.541700 to 1.249300 ms. The sample standard deviation records this variation instead of selecting only the fastest observation.

#### Fermat Prime-Distance Experiment

Both generated moduli have 28 bits and similar magnitudes:

| Case | n | p | q | Distance | Fermat checks | Mean time, ms | SD, ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Close primes | 201696779 | 14197 | 14207 | 10 | 1 | 0.002067 | 0.000351 |
| Separated primes | 201330583 | 4099 | 49117 | 45018 | 12419 | 3.054167 | 1.570763 |

Fermat begins at `ceil(sqrt(n))` and finishes at `(p+q)/2` for odd prime factors. Including the initial candidate, its exact check count is `(p+q)/2 - ceil(sqrt(n)) + 1`. The close pair requires one check. The separated pair requires 12419, even though both moduli have the same bit length.

These experiments demonstrate factor recovery and private-key reconstruction for small educational RSA values. The repeatable generator and integer RSA routines do not implement production key generation or randomized encryption padding.
