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

ROOT = Path(__file__).resolve().parent.parent
HEADERS = {
    9: ['t', 'z1', 'z2', 'z3', 'z4', 'v1', 'v2', 'v3', 'v4'],
    11: ['x1', 'x2', 'x4', 'x5', 'x6', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6'],
}
SIZES = {1104: 9, 5744: 11}


def read_points(path, dimension=9):
    header = HEADERS[dimension]
    with Path(path).open(encoding='ascii', newline='') as handle:
        reader = csv.reader(handle, strict=True)
        try:
            if next(reader, None) != header:
                raise ValueError('CSV header must be ' + ','.join(header))
            points = []
            for line, row in enumerate(reader, 2):
                if len(row) != dimension or any(x not in ('0', '1', '2') for x in row):
                    raise ValueError(f'Invalid ternary {dimension}-coordinate row at line {line}.')
                points.append(tuple(map(int, row)))
        except csv.Error as error:
            raise ValueError(f'Malformed CSV near line {reader.line_num}: {error}') from error
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


def verify_file(path, size):
    dimension = SIZES[size]
    points = read_points(path, dimension)
    if len(points) != size:
        raise ValueError(f'Expected {size} points, found {len(points)}.')
    if size == 1104:
        layers = Counter(p[0] for p in points)
        expected = {1: 512, 0: 80, 2: 512}
        label = 't'
    else:
        # CSV indices 1,2,3 are the retained source coordinates x2,x4,x5.
        layers = Counter((p[1] + p[2] + p[3]) % 3 for p in points)
        expected = {1: 2304, 0: 1136, 2: 2304}
        label = 'beta=x2+x4+x5'
    if layers != expected:
        raise ValueError(f'Unexpected layer sizes: {dict(layers)}')
    differences = [tuple((x-y) % 3 for x, y in zip(p, points[0]))
                   for p in points[1:]]
    rank = matrix_rank(differences)
    if rank != dimension:
        raise ValueError(f'Expected affine dimension {dimension}, found {rank}.')
    checked = check_cap(points, dimension)
    print(f'PASS: {size} distinct points in F_3^{dimension}; affine dimension {rank}.')
    print(f'PASS: {label} layers (+1,0,-1) = '
          f'({layers[1]},{layers[0]},{layers[2]}).')
    print(f'PASS: all {checked:,} unordered pairs checked; no forbidden line.')
    print(f'{path.name} SHA256:', hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', nargs='?', type=Path, help='Custom CSV; requires --cap.')
    parser.add_argument('--cap', type=int, choices=tuple(SIZES),
                        help='Check one cap; by default check both saved point lists.')
    args = parser.parse_args()
    if args.csv is not None and args.cap is None:
        parser.error('A custom CSV requires --cap 1104 or --cap 5744.')
    try:
        for size in ([args.cap] if args.cap else SIZES):
            path = args.csv if args.csv is not None else ROOT / f'data/cap{size}.csv'
            verify_file(path, size)
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(1, f'FAIL: {error}\n')


if __name__ == '__main__':
    main()
