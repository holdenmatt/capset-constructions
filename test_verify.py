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
            # Decode block position and inset local position separately.
            # Independent constants describe the intended 60px blocks, 10px inset.
            def decode_axis(position):
                block_index = int(position // 60)
                within = position - 60 * block_index
                self.assertGreaterEqual(min(within, 60-within)
                                        - float(dot.attrib['r']), 8)
                local_index = round((within-10)/5)
                self.assertAlmostEqual(within, 10+5*local_index, places=5)
                self.assertIn(block_index, range(9))
                self.assertIn(local_index, range(9))
                def pair(index):
                    return ((index//3-1) % 3, (index%3-1) % 3)
                return pair(block_index) + pair(local_index)
            x = decode_axis(float(dot.attrib['cx'])-66)
            y = decode_axis(540-(float(dot.attrib['cy'])-top))
            reconstructed = (t,x[0],x[1],y[0],y[1],x[2],x[3],y[2],y[3])
            self.assertEqual(reconstructed, p)
            decoded.append(reconstructed)
        self.assertEqual(set(decoded), set(points))


if __name__ == '__main__':
    unittest.main()
