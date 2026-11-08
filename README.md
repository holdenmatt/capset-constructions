# Cap-set constructions

Coordinates and exact verification for **Large caps in F₃⁹ and F₃¹¹**, by Matt Holden.
[LaTeX source](tex/main.tex). The reviewed PDF will be added as
`holden-large-caps.pdf` before publication. An arXiv link will follow when available.

| Cap | Dimension | Construction | Parallel layers |
| --- | --- | --- | --- |
| 1104 points | 9 | Reflection lift of the classical Calderbank–Fishburn 236-cap | 512, 80, 512 |
| 5744 points | 11 | Coordinate substitution in Hill's 112-cap through a noncentral 45-section | 2304, 1136, 2304 |

Both use the same signed-support model of Hill's cap. Both outer layers of
1104 are linearly equivalent to the 512-cap discovered using FunSearch.
The 5744 layer counts do not assert an equivalence between its outer layers.

To the best of our knowledge, these improve the previously reported lower
bounds of 1082 and 5504, respectively. No global optimality claim is made.

## Run all checks

Use **Python 3.9 or later**. All scripts use only the standard library and run offline.
From the repository root:

```sh
python3 code/check_all.py
```

This checks:

- Both saved CSVs exactly match their coordinate recipes.
- All **608,856 pairs** in the 1104-cap and **16,493,896 pairs** in the 5744-cap:
  for distinct points `x,y`, the third collinear point `-x-y` is absent.
- The affine dimensions and the layer counts in the table above.
- Both invertible maps from the 512-point outer layers to the published FunSearch cap.
- The saved 1104 diagram, including decoding dot positions back to cap points.
- The substitution hypotheses, Hill section counts, coordinate recovery, and
  rejection of lines, duplicates, and malformed data.

`verify.py` reads the point lists without importing either constructor or `hill.py`.
These finite checks accompany the proofs; they do not certify historical priority.
The pair check for 5744 is the slowest step.

To run individual checks or regenerate artifacts:

```sh
python3 code/verify.py --cap 5744
python3 code/verify_funsearch.py
python3 -m unittest discover -s code -p 'test_*.py' -v

python3 code/construction_1104.py
python3 code/construction_5744.py
python3 code/make_diagrams.py
```

Both constructors and `make_diagrams.py` accept `--check` to compare saved
artifacts without writing. `verify.py` checks both CSVs by default; use
`python3 code/verify.py --cap 5744 path/to/points.csv` for a custom point list.

## Files and coordinates

| File | Purpose |
| --- | --- |
| [tex/](tex/) | Manuscript source and its included figure; compile `main.tex` from this directory. |
| [code/check_all.py](code/check_all.py) | Runs the complete offline verification suite. |
| [hill.py](code/hill.py) | Shared six-coordinate support design and Hill ingredients. |
| [construction_1104.py](code/construction_1104.py) | Derives the Hill fibers and assembles the reflection lift. |
| [construction_5744.py](code/construction_5744.py) | Implements the affine coordinate substitution. |
| [data/cap1104.csv](data/cap1104.csv), [data/cap5744.csv](data/cap5744.csv) | Complete point lists, sorted lexicographically, with headers. |
| [verify.py](code/verify.py) | Independent pair checks, affine ranks, and layer counts. |
| [verify_funsearch.py](code/verify_funsearch.py) | Exact comparison with the published FunSearch membership rule. |
| [make_diagrams.py](code/make_diagrams.py) | Renders the 1104 CSV as a standalone SVG. |
| [code/tests/](code/tests/) | Geometry, coordinate conventions, diagram decoding, and negative controls. |

Arithmetic is modulo three: **2 represents −1**. Coordinate indices in the
CSV headers are one-based, matching the paper.

### 1104-cap

```text
t,z1,z2,z3,z4,v1,v2,v3,v4
```

`t` selects the layer; `z` specifies a block and `v` a point in its fiber.
The diagram displays layers `t=1,0,2` (that is, +1,0,−1).

### 5744-cap

```text
x1,x2,x4,x5,x6,a1,a2,a3,a4,a5,a6
```

The source is `H = P ∪ Q+` in six coordinates. `P` contains all signings on
these ten supports:

```text
123, 124, 135, 146, 156, 236, 245, 256, 345, 346
```

`Q+` and `Q−` are the full-support vectors of coordinate product +1 and −1.
The substituted scalar is `alpha = x3+x4+x5−1`. Retain `x1,x2,x4,x5,x6` and
append every vector `a` in `P`, `Q+`, or `Q−` according as `alpha` is 0,1,2.
These replacement sets have sizes 80,32,32; the source sections have sizes
45,45,22. Thus the output has `80·45 + 32·45 + 32·22 = 5744` points.

The source coordinate can be recovered as `x3 = alpha+1−x4−x5` modulo 3.
The output's layers use `beta = x2+x4+x5`, with sizes 2304,1136,2304 at
`beta=1,0,2`. The six-dimensional set `P` is distinct from the 1104-cap's
80-point middle layer in eight dimensions.

## The FunSearch comparison

FunSearch is a program-search method guided by a large language model.
The 512-cap's membership rule is specified by Romera-Paredes et al.,
**Figure 4c and Supplement Figure E.23**. `verify_funsearch.py` evaluates it
on all `3^8` vectors, using zero-based indices `x0,…,x7`.
The map from the 1104-cap's plus layer is:

```text
x = (z3, -v2+v4, -v1-v3, z1-z2, z4, z1+z2, v1-v3, v2+v4) mod 3.
```

For the minus layer, first apply `(z2,z1,z3,z4,v3,v4,v1,v2)`, which exchanges
the two outer layers. The checker verifies invertibility and equality of
the complete point sets, then checks all 130,816 FunSearch pairs for lines.

The predicate was also checked against the authors'
[official point list at a fixed revision](https://github.com/google-deepmind/funsearch/blob/cc53f274237d7ab05c19df939edbc1f9616a7c19/cap_set/n8_size512.txt).
To repeat that optional check, download the file and run:

```sh
python3 code/verify_funsearch.py --official-points /path/to/n8_size512.txt
```

## Reading the 1104 diagram

Each dot is one point. In every panel, the 9-by-9 block grid encodes
`(z1,z2)` horizontally and `(z3,z4)` vertically. Within each block, the
9-by-9 possible dot positions encode `(v1,v2)` and `(v3,v4)`. Pairs are
ordered lexicographically, −1 < 0 < 1, increasing rightwards and upwards.
All panels share the same arrangement and scale, with dots inset from block edges.

Blue blocks have addresses on the signed axes `E`; the other four colors
label `Fi`, the addresses whose only zero coordinate is `i`. Straight
alignments in this encoding need not be lines over F₃.

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
  CSIT 2023, 135–136, Corollary 2: the 5504 construction. The ordinary Hill
  slicing 40/36/36 gives 5504 under the substitution; choosing a noncentral
  45-section gains `(80−32)(45−40) = 240` points.
- Fiber and generalized-product constructions are classical; see
  [Edel–Bierbrauer (1999)](https://www.yvesedel.de/Papers/RCap.pdf) and
  [Edel (2004), including Section 3's Hill ingredients](https://www.yvesedel.de/Papers/ExtProd.pdf).

The paper (including its LaTeX source and PDF), original code, documentation,
coordinate data, and diagrams are available under the [MIT license](LICENSE).
This license does not cover the external works cited or linked above.
Please cite the paper and relevant original sources.
