"""Render coordinate diagrams from the CSV, using only the standard library.

The same address pairing, local pairing and scale are used in all panels.
SVG circles retain their full CSV coordinates in data-point attributes.
"""

import argparse
from collections import Counter
from pathlib import Path

from verify import ROOT, read_points

COLORS = ('#0072B2', '#D88000', '#00875A', '#C65B91', '#7651A8')
BLOCK_INSET = 1 / 6  # Fraction of a block between its edge and the outer dot centers.


def signed(a):
    return -1 if a == 2 else a


def carrier(z):
    weight = sum(a != 0 for a in z)
    if weight == 1:
        return 0
    if weight == 3:
        return z.index(0) + 1
    raise ValueError(f'Unoccupied carrier address: {z}')


def render(points):
    if len(points) != 1104 or len(set(points)) != 1104:
        raise ValueError('Expected 1104 distinct points.')
    if Counter(p[0] for p in points) != {1:512, 0:80, 2:512}:
        raise ValueError('Unexpected layer counts.')
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1920" '
           'viewBox="0 0 800 1920" role="img" aria-labelledby="title desc">',
           '<title id="title">A 1104-cap in nine dimensions: coordinate diagrams</title>',
           '<desc id="desc">Three vertically stacked panels with 512, 80, 512 dots. '
           'Block columns encode z1,z2; block rows encode z3,z4. Within a block, '
           'dot columns encode v1,v2 and dot rows v3,v4. All pairs use lexicographic '
           'order -1,0,1 increasing rightwards and upwards. Dot patterns are '
           'inset from block borders for readability.</desc>',
           '<rect width="800" height="1920" fill="white"/>',
           '<g font-family="Arial, sans-serif" fill="#222">',
           '<text x="66" y="36" font-size="24">A 1104-cap in F₃⁹</text>',
           '<text x="66" y="60" font-size="14">One dot = one point · common coordinates in every panel</text>']
    left, side = 66, 540
    block = side / 9
    inset = block * BLOCK_INSET
    step = (block - 2 * inset) / 8
    pair_labels = [(a,b) for a in (-1,0,1) for b in (-1,0,1)]
    for index, (t, name) in enumerate(((1,'+1'),(0,'0'),(2,'−1'))):
        top = 90 + 590 * index
        layer = sorted(p for p in points if p[0] == t)
        svg.append(f'<g id="layer-{t}">')
        svg.append(f'<rect x="{left}" y="{top}" width="{side}" height="{side}" '
                   'fill="none" stroke="#aaa" stroke-width="0.8"/>')
        for k in range(1,9):
            delta = k * side / 9
            color = '#bbb' if k % 3 == 0 else '#ddd'
            svg.append(f'<path d="M {left+delta:g},{top} v {side} '
                       f'M {left},{top+delta:g} h {side}" fill="none" '
                       f'stroke="{color}" stroke-width="0.7"/>')
        for k,(a,b) in enumerate(pair_labels):
            x = left + (k + 0.5) * side / 9
            y = top + side - (k + 0.5) * side / 9 + 4
            svg.append(f'<text x="{x:g}" y="{top+side+17}" text-anchor="middle" '
                       f'font-size="10">({a},{b})</text>')
            svg.append(f'<text x="{left-8}" y="{y:g}" text-anchor="end" '
                       f'font-size="10">({a},{b})</text>')
        addresses = set()
        for p in layer:
            z = tuple(signed(a) for a in p[1:5])
            v = tuple(signed(a) for a in p[5:])
            # Keep the nine block positions fixed; inset each nine-position local grid.
            bx, by = 3*z[0]+z[1]+4, 3*z[2]+z[3]+4
            vx, vy = 3*v[0]+v[1]+4, 3*v[2]+v[3]+4
            ix, iy = 9*bx+vx, 9*by+vy
            if (ix,iy) in addresses:
                raise ValueError('Diagram coordinates overlap.')
            addresses.add((ix,iy))
            cx = left + bx*block + inset + vx*step
            cy = top + (8-by)*block + inset + (8-vy)*step
            color = COLORS[carrier(z)]
            label = ','.join(map(str,p))
            svg.append(f'<circle cx="{cx:.6f}" cy="{cy:.6f}" r="1.85" '
                       f'fill="{color}" data-point="{label}"><title>{label}</title></circle>')
        svg.append(f'<text x="630" y="{top+72}" font-size="22">t = {name}</text>')
        svg.append(f'<text x="630" y="{top+101}" font-size="17">{len(layer)} points</text>')
        formula = '8 × 8 + 16' if t == 0 else '8 × 16 + 32 × 12'
        svg.append(f'<text x="630" y="{top+126}" font-size="14">{formula}</text>')
        if index == 0:
            for g, label in enumerate(('E','F₁','F₂','F₃','F₄')):
                y = top+193+28*g
                svg.append(f'<circle cx="637" cy="{y-4}" r="4" fill="{COLORS[g]}"/>')
                svg.append(f'<text x="652" y="{y}" font-size="17">{label}</text>')
        svg.append('</g>')
    svg.extend([
        '<text x="66" y="1856" font-size="14">Blocks: columns (z₁,z₂), rows (z₃,z₄). Dots within each block: columns (v₁,v₂), rows (v₃,v₄).</text>',
        '<text x="66" y="1880" font-size="14">Pairs run in lexicographic order −1, 0, 1, increasing rightwards and upwards.</text>',
        '<text x="66" y="1904" font-size="14">Straight alignments in this encoding need not be lines over F₃.</text>',
        '</g>', '</svg>', ''])
    return '\n'.join(svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=ROOT / 'data/cap1104.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'figures/atlas1104.svg')
    parser.add_argument('--check', action='store_true', help='Check saved SVG without writing.')
    args = parser.parse_args()
    try:
        payload = render(read_points(args.csv)).encode('utf-8')
        if args.check:
            if args.output.read_bytes() != payload:
                raise ValueError('Saved diagrams differ from the point list.')
            print('PASS: saved coordinate diagrams exactly match the CSV (512, 80, 512 dots).')
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(payload)
            print(f'Wrote {args.output}.')
    except (OSError, ValueError, UnicodeError) as error:
        parser.exit(1, f'FAIL: {error}\n')


if __name__ == '__main__':
    main()
