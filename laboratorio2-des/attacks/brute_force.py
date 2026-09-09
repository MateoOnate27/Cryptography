from dataclasses import dataclass
from time import perf_counter

from deslib import des_encrypt_block
from deslib.validation import require_bytes, require_uint
from .keyspace import DEFAULT_FIXED, candidate_to_key, validate_bits


@dataclass
class SearchResult:
    key: bytes | None
    candidate: int | None
    tested: int
    elapsed: float
    workers: int = 1
    worker_tested: tuple[int, ...] = ()

    @property
    def keys_per_second(self) -> float:
        return self.tested / self.elapsed if self.elapsed > 0 else 0.0


def validate_search(plaintext, ciphertext, start, end, unknown_bits, fixed_effective):
    require_bytes(plaintext, "plaintext", 8)
    require_bytes(ciphertext, "ciphertext", 8)
    validate_bits(unknown_bits)
    require_uint(fixed_effective, 56, "fixed_effective")
    if not isinstance(start, int) or not isinstance(end, int):
        raise TypeError("start y end deben ser enteros.")
    if not 0 <= start <= end <= (1 << unknown_bits):
        raise ValueError("El intervalo debe cumplir 0 <= start <= end <= 2**n.")


def search_interval(plaintext, ciphertext, start, end, unknown_bits, fixed_effective, stop=None):
    """Rutina compartida por la búsqueda secuencial y cada proceso hijo."""
    tested = 0
    for candidate in range(start, end):
        if stop is not None and tested % 64 == 0 and stop.is_set():
            break
        key = candidate_to_key(candidate, unknown_bits, fixed_effective)
        encrypted = des_encrypt_block(key, plaintext)
        tested += 1
        if encrypted == ciphertext:
            if stop is not None:
                stop.set()
            return key, candidate, tested
    return None, None, tested


def brute_force_des(
    plaintext: bytes, ciphertext: bytes, start: int, end: int,
    unknown_bits: int = 16, fixed_effective: int = DEFAULT_FIXED,
) -> SearchResult:
    validate_search(plaintext, ciphertext, start, end, unknown_bits, fixed_effective)
    beginning = perf_counter()
    key, candidate, tested = search_interval(
        plaintext, ciphertext, start, end, unknown_bits, fixed_effective
    )
    elapsed = perf_counter() - beginning
    return SearchResult(key, candidate, tested, elapsed, 1, (tested,))
