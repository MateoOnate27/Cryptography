import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from time import perf_counter

from .brute_force import SearchResult, brute_force_des, search_interval, validate_search
from .keyspace import DEFAULT_FIXED

_STOP = None


def _initialize_worker(stop):
    global _STOP
    _STOP = stop


def _worker(plaintext, ciphertext, start, end, unknown_bits, fixed_effective):
    return search_interval(
        plaintext, ciphertext, start, end, unknown_bits, fixed_effective, _STOP
    )


def partition_range(start: int, end: int, workers: int) -> list[tuple[int, int]]:
    if not isinstance(workers, int) or workers < 1:
        raise ValueError("workers debe ser un entero positivo.")
    if not 0 <= start <= end:
        raise ValueError("Intervalo inválido.")
    size = end - start
    return [
        (start + size * i // workers, start + size * (i + 1) // workers)
        for i in range(workers)
    ]


def parallel_brute_force_des(
    plaintext: bytes, ciphertext: bytes, start: int, end: int,
    workers: int = 2, unknown_bits: int = 16,
    fixed_effective: int = DEFAULT_FIXED,
) -> SearchResult:
    validate_search(plaintext, ciphertext, start, end, unknown_bits, fixed_effective)
    intervals = partition_range(start, end, workers)
    if workers == 1:
        return brute_force_des(plaintext, ciphertext, start, end, unknown_bits, fixed_effective)

    context = mp.get_context("spawn")
    stop = context.Event()
    beginning = perf_counter()
    pool = ProcessPoolExecutor(
        max_workers=workers, mp_context=context,
        initializer=_initialize_worker, initargs=(stop,),
    )
    found_key, found_candidate = None, None
    counts = [0] * workers
    try:
        futures = {
            pool.submit(_worker, plaintext, ciphertext, a, b, unknown_bits, fixed_effective): i
            for i, (a, b) in enumerate(intervals)
        }
        for future in as_completed(futures):
            key, candidate, tested = future.result()
            counts[futures[future]] = tested
            if key is not None:
                found_key, found_candidate = key, candidate
                stop.set()
    finally:
        stop.set()
        pool.shutdown(wait=True, cancel_futures=True)
    elapsed = perf_counter() - beginning
    return SearchResult(found_key, found_candidate, sum(counts), elapsed, workers, tuple(counts))
