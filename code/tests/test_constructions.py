"""Check the common source geometry and the paper's coordinate conventions."""

from collections import Counter
from itertools import product
from pathlib import Path
import tempfile
import unittest

from hill import hill_caps, ingredients, signings
from construction_1104 import DIRECTIONS, fibers
from construction_5744 import alpha, beta
from verify import ROOT, check_cap, read_points


class ConstructionTests(unittest.TestCase):
    def test_replacement_hypotheses(self):
        p, plus, minus = ingredients()
        self.assertEqual(tuple(map(len, (p, plus, minus))), (80,32,32))
        self.assertFalse(p & plus or p & minus or plus & minus)
        for a,b in ((p,plus), (p,minus), (plus,minus)):
            check_cap(sorted(a | b), 6)

    def test_hill_sections_and_affine_chart(self):
        h,_ = hill_caps()
        self.assertEqual(Counter(alpha(x) for x in h), {0:45, 1:45, 2:22})
        self.assertEqual(Counter(x[5] for x in h), {0:40, 1:36, 2:36})
        joint = [[sum(alpha(x)==i and beta(x)==j for x in h)
                  for j in range(3)] for i in range(3)]
        self.assertEqual(joint, [[9,18,18], [9,18,18], [4,9,9]])
        for x in product(range(3), repeat=6):
            self.assertEqual((alpha(x)+1-x[3]-x[4]) % 3, x[2])

    def test_reflection_fibers_and_classical_source(self):
        hs = hill_caps()
        for h, ff in zip(hs, fibers()):
            self.assertEqual(list(map(len,ff)), [16,12,12,12,12])
            for q,f in zip(DIRECTIONS,ff):
                self.assertEqual({x[:4] for x in h if x[4:]==tuple(-v%3 for v in q)}, f)
        axes = signings([(i,) for i in range(1,7)],6)
        source = {(1,)+x for x in hs[0]} | {(2,)+x for x in hs[1]} | {(0,)+x for x in axes}
        self.assertEqual(len(source),236)
        self.assertEqual(sum(x[5:]==(0,0) for x in source),40)
        check_cap(sorted(source),7)

    def test_5744_csv_recovers_source_and_multiplicities(self):
        # Decode saved output into source points, using the replacement sets' label.
        # This catches retained-coordinate permutations and incorrect parity assignments.
        parts=ingredients()
        label={a:i for i,part in enumerate(parts) for a in part}
        recovered=Counter()
        for point in read_points(ROOT/'data/cap5744.csv',11):
            x1,x2,x4,x5,x6=point[:5]
            i=label[point[5:]]
            x3=(i+1-x4-x5)%3
            recovered[(x1,x2,x3,x4,x5,x6)]+=1
        h,_=hill_caps()
        self.assertEqual(set(recovered),h)
        for x,n in recovered.items():
            self.assertEqual(n,80 if alpha(x)==0 else 32)

    def test_5744_rejects_wrong_csv_convention(self):
        header='x1,x2,x4,x5,x6,a1,a2,a3,a4,a5,a6\n'
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'bad.csv'
            for text in (header.replace('x4','x3'), header+'0,0,0\n',
                         header+','.join(['3']+['0']*10)+'\n'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    read_points(path,11)


if __name__ == '__main__':
    unittest.main()
