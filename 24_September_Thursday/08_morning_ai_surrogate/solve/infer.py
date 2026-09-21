#!/usr/bin/env python3
"""Use the trained surrogate.

  python use_surrogate.py predict Ti2FeAg --model surrogate.pt [--emon runs/00007/emon.dat]
  python use_surrogate.py speed   --model surrogate.pt
  python use_surrogate.py invert  --model surrogate.pt --data dataset.npz     # spectrum -> composition
"""
import argparse, time
import numpy as np
import torch
import fluo
from train_surrogate import load_surrogate


def cmd_predict(a):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    s = load_surrogate(a.model)
    y = s.predict(a.formula)
    print('mass fractions:', {k: round(float(v), 3) for k, v in zip(fluo.ELEMENTS, fluo.mass_fractions(a.formula))})
    print('K-alpha areas :', {k: float('%.3g' % v) for k, v in zip(fluo.ELEMENTS, fluo.line_areas(s.E, y))})
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.semilogy(s.E, y + 1e-18, label='surrogate')
    if a.emon:                                    # compare with a real McXtrace run
        r = fluo.read_mccode_1d(a.emon)
        G = fluo.response_matrix(r['E'], s.ck['fwhm0']) if s.ck['fwhm0'] >= 0 else None
        ref, _ = fluo.apply_response(G, r['I'])
        ax.semilogy(r['E'], ref + 1e-18, lw=.8, label='simulation (+ detector response)')
        print('relative L2 error: %.4f' % (np.linalg.norm(y - ref) / np.linalg.norm(ref)))
    ax.set_ylim(y.max() * 1e-5, y.max() * 3); ax.set_xlabel('E [keV]'); ax.set_title(a.formula); ax.legend()
    fig.tight_layout(); fig.savefig('predict.png', dpi=110); print('figure -> predict.png')


def cmd_speed(a):
    s = load_surrogate(a.model)
    w = np.random.dirichlet(np.ones(5), 10000)
    t = time.time(); s.predict(w); dt = time.time() - t
    print(f'{dt / len(w) * 1e6:.1f} us per spectrum (batch of {len(w)}, CPU)')
    print('a McXtrace run of 1e6 rays takes seconds to minutes: check with `time mxrun ...`')


def cmd_invert(a):
    """Inverse problem: find the composition whose predicted spectrum best matches a
    measured one. Possible because the surrogate is differentiable: w = softmax(theta),
    Adam on the squared difference in sqrt space, several random starts in parallel."""
    s = load_surrogate(a.model); m = s.model
    d = np.load(a.data); ck = s.ck
    G = fluo.response_matrix(d['E'], ck['fwhm0']) if ck['fwhm0'] >= 0 else None
    idx = ck['splits']['test'][:a.n]
    Yd, _ = fluo.apply_response(G, d['Y'][idx])
    target = torch.tensor(np.sqrt(Yd / ck['S']), dtype=torch.float32)          # (n, nE)
    n, K = len(idx), a.starts
    torch.manual_seed(0)
    theta = torch.randn(n, K, 5, requires_grad=True)
    opt = torch.optim.Adam([theta], lr=0.05)
    t0 = time.time()
    for it in range(a.iters):
        w = torch.softmax(theta, -1)
        pred = m(w.reshape(-1, 5)).reshape(n, K, -1)
        loss = ((pred - target[:, None]) ** 2).mean(-1)                          # (n, K)
        opt.zero_grad(); loss.sum().backward(); opt.step()
    best = loss.argmin(1)
    w_fit = torch.softmax(theta, -1)[torch.arange(n), best].detach().numpy()
    w_true = d['w'][idx]
    err = np.abs(w_fit - w_true)
    print(f'{n} spectra inverted in {time.time() - t0:.1f} s ({a.starts} starts each)')
    print('mean abs error of mass fractions per element:', {k: round(float(v), 3) for k, v in zip(fluo.ELEMENTS, err.mean(0))})
    for j in range(min(5, n)):
        print(f'  {d["formulas"][idx[j]]:16s} true {w_true[j].round(2)}  fit {w_fit[j].round(2)}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    p = sp.add_parser('predict'); p.add_argument('formula'); p.add_argument('--model', default='surrogate.pt')
    p.add_argument('--emon', default=None)
    p = sp.add_parser('speed'); p.add_argument('--model', default='surrogate.pt')
    p = sp.add_parser('invert'); p.add_argument('--model', default='surrogate.pt'); p.add_argument('--data', default='dataset.npz')
    p.add_argument('--n', type=int, default=30); p.add_argument('--starts', type=int, default=8); p.add_argument('--iters', type=int, default=400)
    a = ap.parse_args(); dict(predict=cmd_predict, speed=cmd_speed, invert=cmd_invert)[a.cmd](a)
