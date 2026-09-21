#!/usr/bin/env python3
"""Run Test_Fluorescence.instr for many random formulae and collect emon.dat spectra.

  python make_dataset.py --n 500 --jobs 8                 # McXtrace (mxrun must be in PATH)
  python make_dataset.py --n 500 --synthetic              # toy generator, seconds
Output: dataset.npz  (formulas, w, E, Y, Yerr, N, Yrep, rep_idx, E0)
The runs are restartable: an existing runs/<id>/emon.dat is not recomputed.
"""
import argparse, os, subprocess
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import fluo


def run_one(job):
    run_dir, formula, ncount, seed, instr, E0, synthetic = job
    if os.path.exists(f'{run_dir}/emon.dat'):
        return run_dir
    if synthetic:
        fluo.toy_run(run_dir, formula, ncount, seed, E0)
    else:
        # -d must not pre-exist; one process per run, parallelism comes from --jobs
        cmd = ['mxrun', '-d', run_dir, '-n', str(int(ncount)), '--seed', str(seed),
               instr, f'material={formula}', f'E0={E0}']
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            print('FAILED', formula, r.stderr[-300:])
    return run_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=500); ap.add_argument('--ncount', type=float, default=1e6)
    ap.add_argument('--E0', type=float, default=39.0); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--instr', default='Test_Fluorescence.instr'); ap.add_argument('--out', default='dataset.npz')
    ap.add_argument('--repeat', type=int, default=20, help='re-run the first K formulae with another seed: noise floor')
    ap.add_argument('--synthetic', action='store_true'); ap.add_argument('--seed', type=int, default=42)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    formulas = fluo.random_formulas(a.n, rng)
    rep_idx = np.arange(min(a.repeat, a.n))
    jobs = [(f'runs/{i:05d}', f, a.ncount, 1000 + i, a.instr, a.E0, a.synthetic) for i, f in enumerate(formulas)]
    jobs += [(f'runs/{i:05d}_rep', formulas[i], a.ncount, 900000 + i, a.instr, a.E0, a.synthetic) for i in rep_idx]
    with ThreadPoolExecutor(a.jobs) as ex:
        dirs = list(ex.map(run_one, jobs))

    def collect(d):
        r = fluo.read_mccode_1d(f'{d}/emon.dat')
        return r['E'], r['I'], r['I_err'], r['N']
    res = [collect(d) for d in dirs]
    E = res[0][0]
    n = len(formulas)
    Y, Yerr, N = (np.stack([r[k] for r in res[:n]]) for k in (1, 2, 3))
    Yrep = np.stack([r[1] for r in res[n:]]) if len(rep_idx) else np.zeros((0, len(E)))
    np.savez_compressed(a.out, formulas=np.array(formulas), w=np.stack([fluo.mass_fractions(f) for f in formulas]),
                        E=E, Y=Y, Yerr=Yerr, N=N, Yrep=Yrep, rep_idx=rep_idx, E0=a.E0)
    print(f'{n} spectra x {len(E)} bins -> {a.out}')


if __name__ == '__main__':
    main()
