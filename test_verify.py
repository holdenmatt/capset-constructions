"""Small negative controls for the independent checker and atlas encoding."""

from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from make_atlas import render
from verify import ROOT, check_cap, matrix_rank, read_points


class VerificationTests(unittest.TestCase):
    def test_valid_square(self):
        self.assertEqual(check_cap([(0,0),(0,1),(1,0),(1,1)], 2), 6)

    def test_rejects_line(self):
        with self.assertRaisesRegex(ValueError, 'Forbidden line'):
            check_cap([(0,0),(1,2),(2,1)], 2)

    def test_rejects_cross_layer_line(self):
        with self.assertRaisesRegex(ValueError, 'Forbidden line'):
            check_cap([(0,0,0),(1,1,2),(2,2,1)], 3)

    def test_rejects_duplicate(self):
        with self.assertRaisesRegex(ValueError, 'duplicates'):
            check_cap([(1,2),(1,2)], 2)

    def test_rejects_invalid_coordinates(self):
        for bad in [[(0,3)], [(0,)], [(True,0)], []]:
            with self.assertRaises(ValueError):
                check_cap(bad, 2)

    def test_rejects_malformed_csv(self):
        header = 't,z1,z2,z3,z4,v1,v2,v3,v4\n'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            for text in ('wrong\n', header+'0,0,0\n', header+'3,0,0,0,0,0,0,0,0\n'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    read_points(path)

    def test_modular_rank(self):
        self.assertEqual(matrix_rank([(1,2),(2,1)]), 1)
        self.assertEqual(matrix_rank([(2,1),(0,2)]), 2)

    def test_atlas_round_trip(self):
        points = read_points(ROOT / 'data/cap1104.csv')
        root = ET.fromstring(render(points))
        dots = root.findall('.//{http://www.w3.org/2000/svg}circle[@data-point]')
        self.assertEqual(len(dots), 1104)
        decoded = []
        for dot in dots:
            p = tuple(map(int, dot.attrib['data-point'].split(',')))
            t = p[0]
            top = {1:90, 0:680, 2:1270}[t]
            # Decode plotted coordinates back into four balanced-ternary digits.
            ix = round((float(dot.attrib['cx'])-66)/(540/81)-40.5)
            iy = round(40.5-(float(dot.attrib['cy'])-top)/(540/81))
            def digits(number):
                result = []
                for _ in range(4):
                    digit = (number+1) % 3 - 1
                    result.append(digit % 3)
                    number = (number-digit)//3
                self.assertEqual(number, 0)
                return result[::-1]
            x, y = digits(ix), digits(iy)
            reconstructed = (t,x[0],x[1],y[0],y[1],x[2],x[3],y[2],y[3])
            self.assertEqual(reconstructed, p)
            decoded.append(reconstructed)
        self.assertEqual(set(decoded), set(points))


if __name__ == '__main__':
    unittest.main()
