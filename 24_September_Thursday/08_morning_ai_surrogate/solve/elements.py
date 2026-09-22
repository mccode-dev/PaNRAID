"""Shared helpers for the 5-element fluorescence surrogate (Ti, Fe, Ge, Ru, Ag)."""
import re
import numpy as np

ELEMENTS = ["Ti", "Fe", "Ge", "Ru", "Ag"]

ATOMIC_WEIGHTS = {
    "Ti": 47.867,
    "Fe": 55.845,
    "Ge": 72.630,
    "Ru": 101.07,
    "Ag": 107.8682,
}


def parse_formula(formula):
    """'Ti2FeAg3' -> {'Ti': 2, 'Fe': 1, 'Ag': 3}"""
    counts = {}
    for el, num in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
        if not el:
            continue
        if el not in ATOMIC_WEIGHTS:
            raise ValueError(f"Unsupported element '{el}' in formula '{formula}' "
                              f"(allowed: {ELEMENTS})")
        counts[el] = counts.get(el, 0) + (int(num) if num else 1)
    return counts


def mass_fractions(formula):
    """Return a length-5 vector of mass fractions, in ELEMENTS order."""
    counts = parse_formula(formula)
    masses = {el: counts.get(el, 0) * ATOMIC_WEIGHTS[el] for el in ELEMENTS}
    total = sum(masses.values())
    if total == 0:
        raise ValueError(f"Empty/unparseable formula: '{formula}'")
    return np.array([masses[el] / total for el in ELEMENTS])
