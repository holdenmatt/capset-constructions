"""Replace alpha=x3+x4+x5-1 of Hill's cap by P80, Q+32, Q-32.

Coordinates are (x1,x2,x4,x5,x6,a1,a2,a3,a4,a5,a6), modulo 3.
The first five entries retain the source coordinates; the last six replace
alpha. Its labels 0,1,2 select P,Q_1,Q_{-1}, respectively.
"""

import argparse
import csv
import io
from pathlib import Path

from hill import ingredients

ROOT = Path(__file__).resolve().parent
HEADER = ('x1', 'x2', 'x4', 'x5', 'x6', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6')


def alpha(x):
    return (x[2] + x[3] + x[4] - 1) % 3


def beta(x):
    return (x[1] + x[3] + x[4]) % 3


def construct():
    parts = ingredients()
    h = parts[0] | parts[1]
    return sorted((x[0], x[1], x[3], x[4], x[5]) + a
                  for x in h for a in parts[alpha(x)])


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
