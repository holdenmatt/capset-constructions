"""Construct the 1104-cap by lifting the two Hill caps and the axis layer.

Coordinate order: t,z1,z2,z3,z4,v1,v2,v3,v4, modulo 3.
The fibers derived here are the five rows of the manuscript's table.
"""

import argparse
import csv
import io
from pathlib import Path

from hill import hill_caps, signings

ROOT = Path(__file__).resolve().parent
HEADER = ('t', 'z1', 'z2', 'z3', 'z4', 'v1', 'v2', 'v3', 'v4')
DIRECTIONS = ((0,0), (1,0), (0,1), (1,1), (1,2))


def fibers():
    """The center fiber and four paired fibers of each Hill cap."""
    return tuple([{x[:4] for x in h if x[4:] == q} for q in DIRECTIONS]
                 for h in hill_caps())


def construct():
    axes = signings(((1,), (2,), (3,), (4,)), 4)
    carriers = [axes] + [signings((tuple(j for j in range(1, 5) if j != i),), 4)
                         for i in range(1, 5)]
    plus, minus = fibers()
    points = set()
    for t, local_fibers in ((1, plus), (2, minus)):
        for addresses, local in zip(carriers, local_fibers):
            points.update((t,) + z + v for z in addresses for v in local)
    # M = E x E union (F1 union F2) x {0}.
    points.update((0,) + z + v for z in axes for v in axes)
    points.update((0,) + z + (0, 0, 0, 0) for z in carriers[1] | carriers[2])
    return sorted(points)


def csv_text(points):
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(HEADER)
    writer.writerows(points)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/cap1104.csv')
    parser.add_argument('--check', action='store_true', help='Compare saved CSV; write nothing.')
    args = parser.parse_args()
    points = construct()
    payload = csv_text(points).encode('ascii')
    if args.check:
        if args.output.read_bytes() != payload:
            parser.exit(1, 'FAIL: saved CSV differs from the 1104 coordinate recipe.\n')
        print('PASS: saved 1104 CSV exactly matches the shared Hill construction.')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(f'Wrote {len(points)} points to {args.output}.')


if __name__ == '__main__':
    main()
