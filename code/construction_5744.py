"""Construct the 5744-cap by coordinate substitution in Hill's 112-cap.

Coordinates are (x1,x2,x4,x5,x6,a1,a2,a3,a4,a5,a6), modulo 3.
The first five entries retain the source coordinates; the last six replace
alpha=x3+x4+x5-1. Its labels 0,1,2 select P,Q_1,Q_{-1}, respectively.
The source sections have sizes 45,45,22 and the replacement sets have
sizes 80,32,32, giving 45*80 + 45*32 + 22*32 = 5744 points.
Throughout the code, 2 represents -1.
"""

import argparse
import csv
import io
from pathlib import Path

from hill import ingredients

ROOT = Path(__file__).resolve().parent.parent
HEADER = ('x1', 'x2', 'x4', 'x5', 'x6', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6')


def alpha(x):
    """Shift the noncentral section x3+x4+x5=1 to label zero."""
    return (x[2] + x[3] + x[4] - 1) % 3


def beta(x):
    """Additional layer coordinate used in tests; not needed to construct the cap."""
    return (x[1] + x[3] + x[4]) % 3


def construct():
    """Return the sorted 5744 points in the coordinate order given by HEADER."""
    p, q_plus, q_minus = ingredients()
    hill_cap = p | q_plus
    replacements = (p, q_plus, q_minus)
    points = []
    for x in hill_cap:
        # Retain five coordinates. Together with alpha they determine x,
        # since x3 = alpha + 1 - x4 - x5 (modulo 3).
        retained = (x[0], x[1], x[3], x[4], x[5])
        replacement_set = replacements[alpha(x)]
        # Replace the scalar label by every six-coordinate point in its set.
        points.extend(retained + a for a in replacement_set)
    return sorted(points)


def csv_text(points):
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(HEADER)
    writer.writerows(points)
    return buffer.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/cap5744.csv')
    parser.add_argument('--check', action='store_true', help='Compare saved CSV; write nothing.')
    args = parser.parse_args()
    points = construct()
    payload = csv_text(points).encode('ascii')
    if args.check:
        if args.output.read_bytes() != payload:
            parser.exit(1, 'FAIL: saved CSV differs from the 5744 coordinate recipe.\n')
        print('PASS: saved 5744 CSV exactly matches the shared Hill construction.')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(f'Wrote {len(points)} points to {args.output}.')


if __name__ == '__main__':
    main()
