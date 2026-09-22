#!/usr/bin/env python3
"""
Step A (part 1): generate a set of random chemical formulae from
{Ti, Fe, Ge, Ru, Ag}, deduplicated by reduced composition, always
including the 5 pure elements.

Usage:
    python 01_generate_formulas.py --n 300 --out formulas.txt
"""
import argparse
import random
from math import gcd
from functools import reduce

ELEMENTS = ["Ti", "Fe", "Ge", "Ru", "Ag"]


def reduce_coeffs(coeffs):
    g = reduce(gcd, coeffs)
    return [c // g for c in coeffs]


def formula_from_counts(counts):
    """{'Ti': 2, 'Fe': 1, 'Ag': 3} -> 'Ti2FeAg3' (fixed element order = canonical)."""
    parts = []
    for el in ELEMENTS:
        c = counts.get(el, 0)
        if c == 0:
            continue
        parts.append(el if c == 1 else f"{el}{c}")
    return "".join(parts)


def random_formula(max_coeff=4):
    k = random.randint(1, len(ELEMENTS))
    chosen = random.sample(ELEMENTS, k)
    coeffs = reduce_coeffs([random.randint(1, max_coeff) for _ in chosen])  # Ti2Fe2 -> TiFe
    return formula_from_counts(dict(zip(chosen, coeffs)))


def generate(n, seed=0, max_coeff=4):
    random.seed(seed)
    formulas = set(ELEMENTS)  # always include the 5 pure elements
    while len(formulas) < n:
        formulas.add(random_formula(max_coeff))
    return sorted(formulas)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300, help="total unique formulae (incl. 5 pure elements)")
    ap.add_argument("--max-coeff", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="formulas.txt")
    args = ap.parse_args()

    formulas = generate(args.n, seed=args.seed, max_coeff=args.max_coeff)
    with open(args.out, "w") as f:
        f.write("\n".join(formulas) + "\n")
    print(f"Wrote {len(formulas)} unique formulae to {args.out}")
