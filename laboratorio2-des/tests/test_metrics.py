import unittest

from benchmarks.benchmark_bruteforce import extrapolate, summarize, worker_counts


class MetricTests(unittest.TestCase):
    def test_averages_speedup_and_real_work(self):
        runs = [
            {"bits": 8, "workers": 1, "seconds": 10, "tested": 100},
            {"bits": 8, "workers": 1, "seconds": 14, "tested": 100},
            {"bits": 8, "workers": 2, "seconds": 4, "tested": 80},
            {"bits": 8, "workers": 2, "seconds": 8, "tested": 100},
        ]
        sequential, parallel = summarize(runs)
        self.assertEqual(sequential["mean_seconds"], 12)
        self.assertEqual(parallel["mean_seconds"], 6)
        self.assertEqual(parallel["mean_tested"], 90)
        self.assertEqual(parallel["keys_per_second"], 15)
        self.assertEqual(parallel["speedup"], 2)
        self.assertEqual(parallel["efficiency"], 1)

    def test_full_space_units_and_average(self):
        result = extrapolate(1_000_000)
        self.assertAlmostEqual(result["worst"]["seconds"], 72_057_594_037.927936)
        self.assertEqual(result["average"]["seconds"], result["worst"]["seconds"] / 2)
        self.assertAlmostEqual(result["worst"]["years"], result["worst"]["seconds"] / 31_557_600)

    def test_selected_workers(self):
        self.assertEqual(worker_counts(1), [1])
        self.assertEqual(worker_counts(4), [1, 2, 4])
        self.assertEqual(worker_counts(6), [1, 2, 4, 6])


if __name__ == "__main__":
    unittest.main()
