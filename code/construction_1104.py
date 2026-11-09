"""Construct the 1104-cap by lifting the two Hill caps and the axis layer.

Coordinate order: t,z1,z2,z3,z4,v1,v2,v3,v4, modulo 3.
The source is the classical 236-cap: H at t=1, the six-dimensional
signed axes at t=0, and H' at t=-1. Apply the same reflection lift to
each layer, replacing the last two source coordinates by four block
coordinates. The resulting layers have 512, 80, and 512 points.
Throughout the code, 2 represents -1.
"""

import argparse
import csv
import io
from pathlib import Path

from hill import hill_caps, signings

ROOT = Path(__file__).resolve().parent.parent
HEADER = ('t', 'z1', 'z2', 'z3', 'z4', 'v1', 'v2', 'v3', 'v4')
# The center q=0, then one representative of each nonzero pair {q,-q}.
DIRECTIONS = ((0,0), (1,0), (0,1), (1,1), (1,2))


def fibers():
    """Retain v=(x1,...,x4) at each chosen q=(x5,x6), for H and H'."""
    # Negating q preserves both Hill caps, so q and -q have identical fibers.
    layers = []
    for hill_cap in hill_caps():
        layers.append([{x[:4] for x in hill_cap if x[4:] == q}
                       for q in DIRECTIONS])
    return tuple(layers)


def construct():
    """Return the sorted 1104 points in coordinates (t,z,v)."""
    # E consists of eight signed axes. Each F_i consists of eight signed
    # vectors whose only zero coordinate is i. Match E,F1,...,F4 to DIRECTIONS.
    axes = signings(((1,), (2,), (3,), (4,)), 4)
    carriers = [axes]
    for i in range(1, 5):
        support = tuple(j for j in range(1, 5) if j != i)
        carriers.append(signings((support,), 4))

    # Copy each Hill fiber to its block addresses, giving the outer layers.
    plus, minus = fibers()
    points = set()
    for t, local_fibers in ((1, plus), (2, minus)):
        for addresses, local_points in zip(carriers, local_fibers):
            points.update((t,) + z + v for z in addresses for v in local_points)

    # For the source's axis layer, q=0 leaves the eight v-axes. The pairs
    # q=+/- (1,0) and +/- (0,1) each leave only v=0; the other fibers are empty.
    # Its lift is M = E x E union (F1 union F2) x {0}, of size 64+16=80.
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
