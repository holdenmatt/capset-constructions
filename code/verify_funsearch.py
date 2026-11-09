"""Check both outer layers against the published FunSearch 512-cap.

The predicate below is a fresh implementation of the mathematical conditions
in Romera-Paredes et al., Nature 625 (2024), Figure 4c and Supplement E.23.
Support indices x0,...,x7 are zero-based, unlike the manuscript's z,v indices.
No search code, downloaded points, or third-party Python packages are needed.
See README.md for the source and an optional check against the authors' data.
"""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from verify import ROOT, check_cap, matrix_rank, read_points

# The 24 allowed weight-four supports and eight allowed zero triples in E.23.
SUPPORTS = {
    (0,1,2,3), (0,1,2,5), (0,1,2,7), (0,1,2,6), (0,1,3,7), (0,1,6,7),
    (0,3,6,7), (0,5,6,7), (0,1,5,7), (1,3,4,6), (1,4,5,6), (0,2,3,6),
    (2,3,4,7), (2,4,5,7), (0,2,6,7), (0,2,5,6), (1,2,4,7), (1,2,4,6),
    (1,3,4,7), (1,4,6,7), (1,4,5,7), (2,3,4,6), (2,4,6,7), (2,4,5,6),
}
ZERO_TRIPLES = {
    (0,4,7), (0,2,4), (0,1,4), (0,4,6),
    (1,2,6), (2,6,7), (1,2,7), (1,6,7),
}


def predicate_part(x):
    """Return the name of the selected part, or None if x is not selected."""
    support = tuple(i for i, a in enumerate(x) if a)
    rho = sum(x[i] == x[8-i] for i in (1, 2, 3))
    if len(support) == 8 and rho >= 2:
        return 'weight 8'
    if support in SUPPORTS and rho <= 1:
        return 'weight 4, rho=0' if rho == 0 else 'weight 4, rho=1'
    zeros = tuple(i for i, a in enumerate(x) if a == 0)
    if (zeros in ZERO_TRIPLES and rho <= 1
            and x[1] * x[7] % 3 != 1 and x[2] * x[6] % 3 != 1):
        return 'weight 5'
    return None


def to_funsearch(p):
    """The linear map B_+ -> FunSearch coordinates, documented in the README."""
    z1, z2, z3, z4, v1, v2, v3, v4 = p
    return tuple(a % 3 for a in
                 (z3, -v2+v4, -v1-v3, z1-z2, z4, z1+z2, v1-v3, v2+v4))


def swap_outer(p):
    """The involutory coordinate permutation interchanging B_+ and B_-."""
    z1, z2, z3, z4, v1, v2, v3, v4 = p
    return z2, z1, z3, z4, v3, v4, v1, v2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', nargs='?', type=Path, default=ROOT / 'data/cap1104.csv')
    parser.add_argument('--official-points', type=Path,
                        help='Optional downloaded FunSearch n8_size512.txt to compare.')
    args = parser.parse_args()
    try:
        points = read_points(args.csv)
        if len(points) != 1104 or len(set(points)) != 1104:
            raise ValueError('Expected 1104 distinct input points.')
        plus = {p[1:] for p in points if p[0] == 1}
        minus = {p[1:] for p in points if p[0] == 2}
        selected = {x: predicate_part(x) for x in product(range(3), repeat=8)
                    if predicate_part(x) is not None}
        counts = Counter(selected.values())
        if len(selected) != 512 or sorted(counts.values()) != [128] * 4:
            raise ValueError(f'Unexpected predicate counts: {dict(counts)}')
        basis_images = [to_funsearch(tuple(int(i == j) for j in range(8)))
                        for i in range(8)]
        if matrix_rank(basis_images) != 8:
            raise ValueError('The linear map is singular.')
        target = set(selected)
        if len(plus) != 512 or {to_funsearch(p) for p in plus} != target:
            raise ValueError('The plus layer does not map exactly to the published cap.')
        if {swap_outer(p) for p in plus} != minus:
            raise ValueError('The coordinate permutation does not exchange the outer layers.')
        if {to_funsearch(swap_outer(p)) for p in minus} != target:
            raise ValueError('The minus layer does not map exactly to the published cap.')
        checked = check_cap(sorted(target), 8)
        if args.official_points:
            official = []
            for line, text in enumerate(args.official_points.read_text().splitlines(), 1):
                if not text.strip():
                    continue
                point = json.loads(text)
                if (not isinstance(point, list) or len(point) != 8
                        or any(type(a) is not int or a not in (0, 1, 2) for a in point)):
                    raise ValueError(f'Invalid ternary 8-coordinate row at line {line}.')
                official.append(tuple(point))
            if len(official) != 512 or set(official) != target:
                raise ValueError('The predicate differs from the supplied official points.')
    except (OSError, ValueError, UnicodeError, TypeError) as error:
        parser.exit(1, f'FAIL: {error}\n')
    print('PASS: published predicate has four disjoint parts of 128 points each.')
    print('PASS: linear map has rank 8 over F_3.')
    print('PASS: both outer layers map exactly to the published FunSearch 512-cap.')
    print(f'PASS: all {checked:,} FunSearch pairs checked; no forbidden line.')
    if args.official_points:
        print('PASS: predicate also equals the supplied official point list.')


if __name__ == '__main__':
    main()
