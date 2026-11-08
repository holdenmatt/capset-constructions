"""The paper's common six-coordinate Hill model, with arithmetic modulo 3."""

from itertools import product
from math import prod

# One-based supports, in exactly the manuscript's coordinate convention.
DESIGN = ((1,2,3), (1,2,4), (1,3,5), (1,4,6), (1,5,6),
          (2,3,6), (2,4,5), (2,5,6), (3,4,5), (3,4,6))


def signings(supports, dimension):
    """All nonzero signings of the given one-based supports."""
    points = set()
    for support in supports:
        for signs in product((1, 2), repeat=len(support)):
            x = [0] * dimension
            for i, a in zip(support, signs):
                x[i - 1] = a
            points.add(tuple(x))
    return points


def ingredients():
    """Return the disjoint sets P, Q_1, Q_{-1}, of sizes 80, 32, 32."""
    cube = set(product((1, 2), repeat=6))
    return (signings(DESIGN, 6),
            {x for x in cube if prod(x) % 3 == 1},
            {x for x in cube if prod(x) % 3 == 2})


def hill_caps():
    """Return H and H': complementary support designs, both with parity +1."""
    p, q_plus, _ = ingredients()
    complements = [tuple(i for i in range(1, 7) if i not in b) for b in DESIGN]
    return p | q_plus, signings(complements, 6) | q_plus
