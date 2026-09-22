#!/usr/bin/env python3
"""
Step A (part 2): run Test_Fluorescence.instr for each formula in formulas.txt
(restartable -- skips directories that already have an emon.dat), then collect
(mass_fractions, spectrum) pairs into a single .npz file.

Usage:
    python 02_run_and_collect.py --instr Test_Fluorescence.instr \
        --formulas formulas.txt --rundir runs --ncount 1e6 --out dataset.npz
"""
import argparse
import os
import subprocess
import numpy as np

from elements import mass_fractions, ELEMENTS


def mxrun_done(run_dir, emon_name="emon.dat"):
    return os.path.isfile(os.path.join(run_dir, emon_name))


def run_one(instr, formula, run_dir, ncount, extra_args=None):
    if mxrun_done(run_dir):
        return True  # restartable: already computed
    cmd = ["mxrun", "-d", run_dir, "-n", str(ncount), instr, f"material={formula}"]
    if extra_args:
        cmd += extra_args
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
        return False
    return mxrun_done(run_dir)


def read_emon(path):
    """McCode 1D monitor file: columns x, I, I_err, N; '#'-prefixed header.
    Returns the I column (the signal, per the tutorial's step 0)."""
    data = np.loadtxt(path, comments="#")
    return data[:, 1]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--instr", default="Test_Fluorescence.instr")
    ap.add_argument("--formulas", default="formulas.txt")
    ap.add_argument("--rundir", default="runs")
    ap.add_argument("--ncount", default="1e6")
    ap.add_argument("--out", default="dataset.npz")
    ap.add_argument("--extra", nargs="*", default=[], help="extra mxrun params, e.g. E0=39 dE=0.06")
    args = ap.parse_args()

    with open(args.formulas) as f:
        formulas = [line.strip() for line in f if line.strip()]

    os.makedirs(args.rundir, exist_ok=True)

    X, Y, kept = [], [], []
    for i, formula in enumerate(formulas):
        run_dir = os.path.join(args.rundir, f"{i:05d}_{formula}")
        print(f"[{i+1}/{len(formulas)}] {formula} -> {run_dir}")
        if not run_one(args.instr, formula, run_dir, args.ncount, args.extra):
            print(f"  !! mxrun failed, skipping {formula}")
            continue
        try:
            I = read_emon(os.path.join(run_dir, "emon.dat"))
        except Exception as e:
            print(f"  !! could not read emon.dat: {e}")
            continue
        X.append(mass_fractions(formula))
        Y.append(I)
        kept.append(formula)

    X, Y = np.array(X), np.array(Y)
    np.savez(args.out, X=X, Y=Y, formulas=np.array(kept), elements=np.array(ELEMENTS))
    print(f"Saved {X.shape[0]} pairs -> {args.out}  (X{X.shape}, Y{Y.shape})")
