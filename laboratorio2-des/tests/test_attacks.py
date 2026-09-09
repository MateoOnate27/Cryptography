import unittest
from threading import Event

from attacks import brute_force_des, candidate_to_key, parallel_brute_force_des
from attacks.keyspace import DEFAULT_FIXED, effective_to_key, key_to_effective
from attacks.parallel_attack import partition_range
from attacks.brute_force import search_interval
from deslib import des_check_parity, des_encrypt_block

PLAIN = bytes.fromhex("0123456789ABCDEF")


class KeyspaceTests(unittest.TestCase):
    def test_mapping_parity_uniqueness_and_fixed_bits(self):
        seen = set()
        for candidate in range(256):
            key = candidate_to_key(candidate, 8)
            effective = key_to_effective(key)
            self.assertTrue(des_check_parity(key))
            self.assertEqual(effective & 255, candidate)
            self.assertEqual(effective >> 8, DEFAULT_FIXED >> 8)
            seen.add(key)
        self.assertEqual(len(seen), 256)

    def test_conversion_of_known_key(self):
        key = bytes.fromhex("133457799BBCDFF1")
        self.assertEqual(effective_to_key(key_to_effective(key)), key)

    def test_invalid_spaces(self):
        for args in [(-1, 8), (256, 8), (0, 0), (0, 56)]:
            with self.assertRaises(ValueError):
                candidate_to_key(*args)

    def test_partition_no_gaps_or_overlaps(self):
        intervals = partition_range(5, 28, 4)
        covered = [key for a, b in intervals for key in range(a, b)]
        self.assertEqual(covered, list(range(5, 28)))
        sizes = [b-a for a,b in intervals]
        self.assertLessEqual(max(sizes) - min(sizes), 1)


class SearchTests(unittest.TestCase):
    def test_stop_signal_prevents_more_candidates(self):
        stop = Event()
        stop.set()
        key, candidate, tested = search_interval(PLAIN, bytes(8), 0, 32, 5, DEFAULT_FIXED, stop)
        self.assertIsNone(key)
        self.assertIsNone(candidate)
        self.assertEqual(tested, 0)

    def test_sequential_recovery_and_exact_count(self):
        key = candidate_to_key(37, 6)
        ciphertext = des_encrypt_block(key, PLAIN)
        result = brute_force_des(PLAIN, ciphertext, 5, 64, 6)
        self.assertEqual(result.key, key)
        self.assertEqual(result.candidate, 37)
        self.assertEqual(result.tested, 33)

    def test_first_and_last_candidates(self):
        for candidate in (0, 31):
            key = candidate_to_key(candidate, 5)
            result = brute_force_des(PLAIN, des_encrypt_block(key, PLAIN), 0, 32, 5)
            self.assertEqual(result.tested, candidate + 1)

    def test_no_match_and_exclusive_end(self):
        key = candidate_to_key(31, 5)
        result = brute_force_des(PLAIN, des_encrypt_block(key, PLAIN), 0, 31, 5)
        self.assertIsNone(result.key)
        self.assertEqual(result.tested, 31)

    def test_empty_and_invalid_intervals(self):
        self.assertEqual(brute_force_des(PLAIN, bytes(8), 0, 0, 5).tested, 0)
        for start,end in [(-1, 1), (5, 4), (0, 33)]:
            with self.assertRaises(ValueError):
                brute_force_des(PLAIN, bytes(8), start, end, 5)

    def test_parallel_recovery(self):
        key = candidate_to_key(200, 8)
        result = parallel_brute_force_des(PLAIN, des_encrypt_block(key, PLAIN), 0, 256, 2, 8)
        self.assertEqual(result.key, key)
        self.assertEqual(result.candidate, 200)
        self.assertGreater(result.tested, 0)
        self.assertLessEqual(result.tested, 256)
        self.assertEqual(result.tested, sum(result.worker_tested))

    def test_parallel_absent_key_searches_entire_range(self):
        key = candidate_to_key(63, 6)
        result = parallel_brute_force_des(PLAIN, des_encrypt_block(key, PLAIN), 0, 63, 3, 6)
        self.assertIsNone(result.key)
        self.assertEqual(result.tested, 63)

    def test_parallel_one_worker_and_invalid_worker_count(self):
        key = candidate_to_key(1, 4)
        ciphertext = des_encrypt_block(key, PLAIN)
        self.assertEqual(parallel_brute_force_des(PLAIN, ciphertext, 0, 16, 1, 4).tested, 2)
        with self.assertRaises(ValueError):
            parallel_brute_force_des(PLAIN, ciphertext, 0, 16, 0, 4)


if __name__ == "__main__":
    unittest.main()
