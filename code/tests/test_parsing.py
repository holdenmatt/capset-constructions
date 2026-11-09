"""Regression checks for strict CSV and optional official-point input parsing."""

from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from verify import HEADERS, ROOT, read_points
from verify_funsearch import predicate_part


class ParsingTests(unittest.TestCase):
    def run_cli(self, script, *args):
        return subprocess.run([sys.executable, str(ROOT / 'code' / script), *map(str, args)],
                              capture_output=True, text=True)

    def assert_input_failure(self, result, message):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertTrue(result.stderr.startswith('FAIL: '), result.stderr)
        self.assertIn(message, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_csv_rejects_malformed_quoting(self):
        header = ','.join(HEADERS[9]) + '\n'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'points.csv'
            for text in ('"' + header.rstrip('\n'),
                         header + '0,0,0,0,0,0,0,0,"0',
                         header + '0,0,0,0,0,0,0,0,"0"junk\n'):
                with self.subTest(text=text):
                    path.write_text(text)
                    with self.assertRaisesRegex(ValueError, 'Malformed CSV'):
                        read_points(path)

    def test_csv_accepts_valid_quoted_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'points.csv'
            path.write_text(','.join('"' + name + '"' for name in HEADERS[9]) + '\n'
                            + ','.join(['"0"', '"1"', '"2"'] * 3) + '\n')
            self.assertEqual(read_points(path), [(0, 1, 2) * 3])

    def test_csv_clis_report_malformed_quoting(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'points.csv'
            path.write_text(','.join(HEADERS[9]) + '\n0,0,0,0,0,0,0,0,"0')
            for script, args in (('verify.py', ('--cap', '1104', path)),
                                 ('verify_funsearch.py', (path,)),
                                 ('make_diagrams.py', ('--check', '--csv', path))):
                with self.subTest(script=script):
                    self.assert_input_failure(self.run_cli(script, *args), 'Malformed CSV')

    def test_official_points_require_integer_ternary_rows(self):
        points = [list(p) for p in product(range(3), repeat=8)
                  if predicate_part(p) is not None]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'official.jsonl'

            def write_rows(rows):
                path.write_text('\n\n'.join(json.dumps(p) for p in rows) + '\n\n')

            write_rows(points)
            result = self.run_cli('verify_funsearch.py', '--official-points', path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('predicate also equals the supplied official point list', result.stdout)

            # The bool/float variants represent exactly the original points under
            # Python equality, so a set comparison alone would accept them.
            bad_rows = ([bool(a) if a in (0, 1) else a for a in points[0]],
                        list(map(float, points[0])), points[0][:-1],
                        [3] + points[0][1:], ['0'] + points[0][1:],
                        {str(i): a for i, a in enumerate(points[0])}, None)
            for row in bad_rows:
                with self.subTest(row=row):
                    write_rows([row] + points[1:])
                    result = self.run_cli('verify_funsearch.py', '--official-points', path)
                    self.assert_input_failure(result, 'Invalid ternary 8-coordinate row at line 1')


if __name__ == '__main__':
    unittest.main()
