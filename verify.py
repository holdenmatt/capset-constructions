"""Independently check a CSV point list, without importing the construction.

For distinct x,y in F_3^d, their unique third collinear point is -x-y.
It is distinct from x and y. Thus checking every unordered pair proves
that the listed points form a cap, including triples across different layers.
"""

import argparse
from collections import Counter
import csv
import hashlib
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HEADER = ['t', 'z1', 'z2', 'z3', 'z4', 'v1', 'v2', 'v3', 'v4']


def read_points(path):
    with Path(path).open(encoding='ascii', newline='') as handle:
        reader = csv.reader(handle)
        if next(reader, None) != HEADER:
            raise ValueError('CSV header must be ' + ','.join(HEADER))
        points = []
        for line, row in enumerate(reader, 2):
            if len(row) != 9 or any(x not in ('0', '1', '2') for x in row):
                raise ValueError(f'Invalid ternary nine-coordinate row at line {line}.')
            points.append(tuple(map(int, row)))
    return points


def check_cap(points, dimension):
    """Return the number of pairs checked; raise ValueError for invalid input."""
    if not points:
        raise ValueError('Point list is empty.')
    if any(len(p) != dimension or
           any(type(a) is not int or a not in (0, 1, 2) for a in p) for p in points):
        raise ValueError('Invalid coordinates.')
    point_set = set(points)
    if len(point_set) != len(points):
        raise ValueError('Point list contains duplicates.')
    checked = 0
    for x, y in combinations(points, 2):
        third = tuple((-a - b) % 3 for a, b in zip(x, y))
        if third in point_set:
            raise ValueError(f'Forbidden line: {x}, {y}, {third}')
        checked += 1
    return checked


def matrix_rank(rows):
    """Exact row rank over F_3 (also used to check the FunSearch linear map)."""
    a = [list(row) for row in rows]
    if not a:
        return 0
    rank = 0
    for col in range(len(a[0])):
        pivot = next((r for r in range(rank, len(a)) if a[r][col] % 3), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = a[rank][col] % 3  # 1 and 2 are their own inverses.
        a[rank] = [(x * inverse) % 3 for x in a[rank]]
        for r in range(rank + 1, len(a)):
            factor = a[r][col] % 3
            a[r] = [(x - factor * y) % 3 for x, y in zip(a[r], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', nargs='?', type=Path, default=ROOT / 'data/cap1104.csv')
    args = parser.parse_args()
    try:
        points = read_points(args.csv)
        checked = check_cap(points, 9)
        if len(points) != 1104:
            raise ValueError(f'Expected 1104 points, found {len(points)}.')
        layers = Counter(p[0] for p in points)
        if layers != {1: 512, 0: 80, 2: 512}:
            raise ValueError(f'Unexpected layer sizes: {dict(layers)}')
        differences = [tuple((x-y) % 3 for x, y in zip(p, points[0]))
                       for p in points[1:]]
        rank = matrix_rank(differences)
        if rank != 9:
            raise ValueError(f'Expected affine dimension 9, found {rank}.')
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(1, f'FAIL: {error}\n')
    print('PASS: 1104 distinct points in F_3^9; affine dimension 9.')
    print('PASS: layer sizes (t=+1, 0, -1) = (512, 80, 512).')
    print(f'PASS: all {checked:,} unordered pairs checked; no forbidden line.')
    print('CSV SHA256:', hashlib.sha256(args.csv.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
