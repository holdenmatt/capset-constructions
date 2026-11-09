# Cap-set constructions

Coordinates and exact verification for *Large caps in F₃⁹ and F₃¹¹*, by Matt Holden.

[Read the paper (PDF)](holden-large-caps.pdf) · [LaTeX source](tex/main.tex)

| Cap | Dimension | Construction | Point list |
| --- | --- | --- | --- |
| 1104 points | 9 | Reflection lift of the classical Calderbank–Fishburn 236-cap | [CSV](data/cap1104.csv) |
| 5744 points | 11 | Coordinate substitution in Hill's 112-cap through a noncentral 45-section | [CSV](data/cap5744.csv) |

To the best of our knowledge, these improve the previously reported lower
bounds of 1082 and 5504, respectively. The paper gives the constructions and proofs.

## Verify the constructions

Use Python 3.9 or later. All scripts use only the standard library and run offline.
From the repository root:

```sh
python3 code/check_all.py
```

This verifies that the saved point lists match the constructors, checks every
pair of distinct points for a forbidden line, and checks the FunSearch
maps, coordinate diagrams, and construction ingredients. It also runs the tests.
The pair checker reads the CSVs independently of the constructors.

To check one cap or regenerate its point list:

```sh
python3 code/verify.py --cap 5744
python3 code/construction_5744.py
```

Use `1104` instead for the other cap. Constructors accept `--check` to compare
with the saved CSV without writing. For a custom point list, run
`python3 code/verify.py --cap 5744 path/to/points.csv`.

## Files

| File | Purpose |
| --- | --- |
| [holden-large-caps.pdf](holden-large-caps.pdf) | Paper. |
| [tex/](tex/) | LaTeX source and figure; compile `main.tex` from this directory. |
| [data/](data/) | Complete point lists, with coordinate headers matching the paper. |
| [construction_1104.py](code/construction_1104.py), [construction_5744.py](code/construction_5744.py) | Coordinate constructors. |
| [hill.py](code/hill.py) | Shared Hill-cap ingredients. |
| [verify.py](code/verify.py) | Independent cap-property, dimension, and layer-count checks. |
| [verify_funsearch.py](code/verify_funsearch.py) | Explicit maps and exact FunSearch comparison. |
| [make_diagrams.py](code/make_diagrams.py) | Generates the 1104 coordinate diagram from its CSV. |
| [code/tests/](code/tests/) | Tests of the constructions, diagrams, and input validation. |

Each CSV row is one point. Arithmetic is modulo three: **2 represents −1**.
See the paper for the meaning of the coordinates.

## FunSearch comparison

The two 512-point outer layers of the 1104-cap are linearly equivalent to
the cap found using FunSearch. To verify this:

```sh
python3 code/verify_funsearch.py
```

The script contains both coordinate maps, checks their invertibility, and
compares the mapped point sets with the published membership rule evaluated
on all `3^8` vectors (Romera-Paredes et al., Figure 4c and Supplement Figure E.23).

For an optional comparison with the authors' data, download the
[official point list](https://github.com/google-deepmind/funsearch/blob/cc53f274237d7ab05c19df939edbc1f9616a7c19/cap_set/n8_size512.txt) and run:

```sh
python3 code/verify_funsearch.py --official-points /path/to/n8_size512.txt
```

## Coordinate diagram

Each dot is one point of the 1104-cap. The panels show its three layers,
with 512, 80, and 512 points. Each small square fixes four coordinates;
dot positions encode the remaining four. See Figure 1 in the paper for
coordinate ordering and colors. Alignments on the page need not be lines over F₃.

![Coordinate diagrams of the 1104-cap](figures/cap1104.svg)

## Attribution

- Calderbank and Fishburn, *Maximal three-independent subsets of {0,1,2}ⁿ*,
  Designs, Codes and Cryptography **4** (1994), 203–211: the classical 236-cap.
- Edel and Bierbrauer, [*Large caps in small spaces*](https://www.yvesedel.de/Papers/smallCaps.pdf),
  **23** (2001), 197–212, Section 2 and Theorem 5/Table 2: Hill coordinates and
  the classical 236-cap model; the linked author version contains corrections.
- Bierbrauer and Edel, [*Large caps in projective Galois spaces*](https://www.yvesedel.de/Papers/CapSurvey.pdf),
  in *Current Research Topics in Galois Geometry* (2012), 87–104, Theorem 1
  and Table 1: doubling the listed 541-cap in PG(8,3) gives the affine
  dimension-nine bound 1082.
- Romera-Paredes et al., [*Mathematical discoveries from program search with large language models*](https://doi.org/10.1038/s41586-023-06924-6),
  Nature **625** (2024), 468–475: FunSearch's explicit 512-cap, its discussion
  of Hill, and a later report of the dimension-nine bound 1082.
- Karapetyan and Karapetyan, [*Complete Caps in AG(n,3)*](https://doi.org/10.51408/csit2023_30),
  CSIT 2023, 135–136, Corollary 2: the 5504-point construction in dimension eleven.
- Fiber and generalized-product constructions are classical; see
  [Edel–Bierbrauer (1999)](https://www.yvesedel.de/Papers/RCap.pdf) and
  [Edel (2004), including Section 3's Hill ingredients](https://www.yvesedel.de/Papers/ExtProd.pdf).

The paper (including its LaTeX source and PDF), code, documentation,
coordinate data, and diagrams are available under the [MIT license](LICENSE).
This license does not cover the external works cited or linked above.
Please cite the paper and relevant original sources.
