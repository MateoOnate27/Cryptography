import copy
import unittest
from benchmarks.support import summarize, validate_results
from benchmarks.benchmark_aes import make_data


def fixture():
    runs = []
    for bits in (128,192,256):
        for size in (1,10,100):
            for repetition in (1,2,3):
                runs.append({'key_bits':bits,'rounds':bits//32+6,'size_mb':size,
                             'bytes':size*1_000_000,'repetition':repetition,
                             'encryption_s':size*2.0,'decryption_s':size*4.0,
                             'encryption_mb_s':0.5,'decryption_mb_s':0.25,
                             'roundtrip_ok':True,'plaintext_sha256':'a',
                             'recovered_sha256':'a','ciphertext_sha256':'b'})
    return {'settings':{'sizes_mb':[1,10,100],'repetitions':3},
            'validation':{'passed':True},'runs':runs}


class BenchmarkTests(unittest.TestCase):
    def test_deterministic_data_and_decimal_mb(self):
        data = make_data(0.001024,7)
        self.assertEqual(len(data),1024)
        self.assertEqual(data,make_data(0.001024,7))
        self.assertNotEqual(data,make_data(0.001024,8))

    def test_invalid_data_sizes(self):
        for size in (0,-1,0.000017):
            with self.assertRaises(ValueError):
                make_data(size,7)

    def test_summary_average_and_sample_deviation(self):
        rows = fixture()['runs'][:3]
        for row, duration in zip(rows,(1,2,3)):
            row['encryption_s'] = duration
        summary = summarize(rows)[0]
        self.assertEqual(summary['encryption_mean_s'],2)
        self.assertEqual(summary['encryption_sd_s'],1)
        self.assertEqual(summary['encryption_mb_s'],0.5)

    def test_complete_grid(self):
        self.assertTrue(validate_results(fixture(),require_complete=True))

    def test_missing_and_duplicate_runs(self):
        payload = fixture()
        payload['runs'].pop()
        with self.assertRaises(ValueError):
            validate_results(payload,require_complete=True)
        payload = fixture()
        payload['runs'].append(copy.deepcopy(payload['runs'][0]))
        with self.assertRaises(ValueError):
            validate_results(payload)

    def test_bad_measurements(self):
        for field, value in (('encryption_s',0),('encryption_s',float('nan')),
                             ('encryption_mb_s',99),('bytes',999999),
                             ('roundtrip_ok',False),('rounds',14),('recovered_sha256','b')):
            payload = fixture()
            payload['runs'][0][field] = value
            with self.assertRaises(ValueError):
                validate_results(payload)

    def test_quick_run_not_final_report(self):
        payload = fixture()
        payload['settings']['sizes_mb'] = [1]
        payload['runs'] = [r for r in payload['runs'] if r['size_mb']==1]
        with self.assertRaises(ValueError):
            validate_results(payload,require_complete=True)


if __name__ == '__main__':
    unittest.main()
