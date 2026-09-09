# Cryptography Laboratories 1 and 2: DES Implementation and Cryptanalysis

**Mateo Oñate**  
School of Mathematical and Computational Sciences, Yachay Tech  
Email: mateo.onate@yachaytech.edu.ec

This repository contains two connected cryptography laboratories. In Laboratory 1, we implement the Data Encryption Standard (DES) as a block cipher library. In Laboratory 2, we extend that library with message padding, ECB and CBC modes, and sequential and parallel key searches.

The cryptographic core performs its own bit operations, permutations, substitutions, and key scheduling. It does not call an external DES implementation. The tables follow the course lecture materials.

## Repository Structure

The repository root contains this README and the two laboratory directories:

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
| `laboratorio2-des/report/` | Report generator and performance figures |
| `laboratorio2-des/docs/` | Study guide, security answers, sources, and rubric mapping |
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

## Environment Requirements

- **Python:** 3.11 or later. The recorded student measurements ran on Python 3.12.7.
- **Cryptographic core, examples, and tests:** Python standard library.
- **Graphs and PDF reports:** Matplotlib and ReportLab, listed in the laboratory requirements files.
- **Operating system:** The parallel implementation follows the `spawn` process model and includes entry-point guards for Windows compatibility.

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

### 6. Generate the Report and Performance Graphs

From `laboratorio2-des`:

```bash
python -m pip install -r requirements.txt
python verificar.py
python -m report.generar_informe --resultados results/mi_equipo/benchmark.json
```

The generator produces:

- `report/Lab_2_DES.pdf`
- `report/Guia_Lab2_DES.pdf`
- `report/figuras/throughput.png`
- `report/figuras/speedup.png`

The PDF generator in this Python package produces the original Spanish report and study guide. The separately prepared English LaTeX report has its own source and compilation workflow.

To plot a new benchmark, replace the JSON path with `results/nueva_medicion_16/benchmark.json`. This updates the generated report and figures to that dataset.

## Recorded Experimental Results

The submitted 16 bit benchmark ran on an **Intel Core i3-1005G1**, with **2 physical cores**, **4 logical processors**, **Windows 10**, and **Python 3.12.7**. Each process configuration includes three repetitions with target candidate 65,535.

| Processes | Mean time, s | Standard deviation, s | Mean tested keys | Keys/s | Speedup | Efficiency |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 36.063 | 2.107 | 65,536.0 | 1,817.3 | 1.000 | 100.0% |
| 2 | 24.725 | 0.695 | 65,536.0 | 2,650.6 | 1.459 | 72.9% |
| 4 | 22.006 | 0.036 | 65,386.7 | 2,971.4 | 1.639 | 41.0% |

Throughput divides total attempts by total time. Speedup divides the sequential mean time by the parallel mean time. Efficiency divides speedup by the number of processes.

Four processes reduced mean search time by approximately 39%. Parallel attempt counts vary with early stopping, so speedup describes time until recovery rather than a fixed amount of completed work in every run.

At the best recorded rate, complete DES-56 traversal projects to approximately **768,455 years**. The expected search time is approximately **384,227 years**, assuming a uniform target position and a constant rate. These calculations describe the measured Python implementation and hardware. The project does not execute a complete DES-56 search or benchmark specialized hardware.
