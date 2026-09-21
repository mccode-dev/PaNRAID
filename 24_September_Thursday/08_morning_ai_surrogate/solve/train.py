#!/usr/bin/env python3
"""Surrogate: composition (mass fractions of Ti, Fe, Ge, Ru, Ag) -> emon.dat spectrum.

  python train_surrogate.py --data dataset.npz --out surrogate.pt
  python train_surrogate.py --data dataset.npz --train-max-elements 3   # extrapolation test

Model = linear mixing baseline (fitted by least squares)  +  MLP correction, both in
sqrt(intensity) space (variance-stabilising for counting noise).
"""
import argparse, time
import numpy as np
import torch, torch.nn as nn
import fluo


class Surrogate(nn.Module):
    def __init__(self, B, S, hidden=256, layers=3):
        super().__init__()
        self.register_buffer('B', torch.as_tensor(B, dtype=torch.float32))     # (n_el, nE) linear-mixing spectra
        self.register_buffer('S', torch.as_tensor(float(S)))                   # global intensity scale
        d, mods = B.shape[0], []
        for _ in range(layers):
            mods += [nn.Linear(d, hidden), nn.GELU()]; d = hidden
        last = nn.Linear(d, B.shape[1]); nn.init.zeros_(last.weight); nn.init.zeros_(last.bias)
        self.net = nn.Sequential(*mods, last)       # zero init: training starts AT the linear baseline

    def baseline(self, w):                          # linear physics-inspired guess, sqrt space
        return torch.sqrt((w @ self.B).clamp(min=0) / self.S + 1e-8)

    def forward(self, w):                           # sqrt(I / S)
        return self.baseline(w) + self.net(w)

    def spectrum(self, w):                          # back to intensity units
        return self.forward(w).clamp(min=0) ** 2 * self.S


def split(formulas, seed, max_el):
    rng = np.random.default_rng(seed)
    n_el = np.array([fluo.n_elements(f) for f in formulas])
    idx = rng.permutation(len(formulas))
    extrap = idx[n_el[idx] > max_el] if max_el < len(fluo.ELEMENTS) else np.array([], int)
    rest = idx[n_el[idx] <= max_el]
    n_te, n_va = int(.15 * len(rest)), int(.10 * len(rest))
    return dict(test=rest[:n_te], val=rest[n_te:n_te + n_va], train=rest[n_te + n_va:], extrap=extrap)


def metrics(E, Yp, Y, Yerr, w):
    """relative L2, reduced chi2 (bins with >=10 effective counts), median line-area error."""
    rel = np.linalg.norm(Yp - Y, axis=1) / np.linalg.norm(Y, axis=1)
    neff = (Y / np.maximum(Yerr, 1e-30)) ** 2
    m = (neff >= 10) & (Y >= 1e-3 * Y.max(1, keepdims=True))     # skip empty bins / convolution tails
    chi2 = ((Yp - Y) ** 2 / np.maximum(Yerr, 1e-30) ** 2 * m).sum() / max(m.sum(), 1)
    la_p, la_t = fluo.line_areas(E, Yp), fluo.line_areas(E, Y)
    sel = w > 0.05
    la = np.abs(la_p - la_t)[sel] / la_t[sel]
    return rel.mean(), chi2, np.median(la)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='dataset.npz'); ap.add_argument('--out', default='surrogate.pt')
    ap.add_argument('--epochs', type=int, default=600); ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--lr', type=float, default=1e-3); ap.add_argument('--hidden', type=int, default=256)
    ap.add_argument('--layers', type=int, default=3)
    ap.add_argument('--fwhm0', type=float, default=0.10, help='detector electronic FWHM [keV]; <0: no response')
    ap.add_argument('--train-max-elements', type=int, default=5)
    ap.add_argument('--seed', type=int, default=0); ap.add_argument('--plot', default='surrogate.png')
    a = ap.parse_args()
    torch.manual_seed(a.seed)

    d = np.load(a.data)
    formulas, w, E, Y, Yerr, Yrep = d['formulas'], d['w'], d['E'], d['Y'], d['Yerr'], d['Yrep']
    G = fluo.response_matrix(E, a.fwhm0) if a.fwhm0 >= 0 else None
    Yd, Yerrd = fluo.apply_response(G, Y, Yerr)                 # what a real detector would record
    sp = split(formulas, a.seed, a.train_max_elements)
    tr, va = sp['train'], sp['val']
    print({k: len(v) for k, v in sp.items()})

    # --- baseline 1: linear mixing  Y ~ w @ B  (least squares on the training set)
    B = np.linalg.lstsq(w[tr], Yd[tr], rcond=None)[0]
    S = Yd[tr].max()
    model = Surrogate(B, S, a.hidden, a.layers)
    wt = torch.tensor(w, dtype=torch.float32)
    zt = torch.tensor(np.sqrt(Yd / S), dtype=torch.float32)     # sqrt space targets

    opt = torch.optim.AdamW(model.parameters(), a.lr, weight_decay=1e-5)
    steps = a.epochs * int(np.ceil(len(tr) / a.batch))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, a.lr, total_steps=steps)
    best, hist, t0 = 1e9, [], time.time()
    for ep in range(a.epochs):
        model.train(); perm = np.random.permutation(tr); tot = 0
        for i in range(0, len(perm), a.batch):
            b = perm[i:i + a.batch]
            loss = ((model(wt[b]) - zt[b]) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step(); sched.step(); tot += loss.item() * len(b)
        model.eval()
        with torch.no_grad():
            v = ((model(wt[va]) - zt[va]) ** 2).mean().item()
        hist.append((tot / len(tr), v))
        if v < best:
            best = v; state = {k: x.clone() for k, x in model.state_dict().items()}
        if ep % 50 == 0 or ep == a.epochs - 1:
            print(f'epoch {ep:4d}  train {hist[-1][0]:.3e}  val {v:.3e}  ({time.time()-t0:.0f}s)')
    model.load_state_dict(state)
    torch.save(dict(state=state, hidden=a.hidden, layers=a.layers, fwhm0=a.fwhm0, E=E, E0=float(d['E0']),
                    B=B, S=float(S), splits=sp), a.out)

    # --- evaluation ---------------------------------------------------------
    with torch.no_grad():
        Ymlp = model.spectrum(wt).numpy()
    Ylin = np.clip(w @ B, 0, None)
    print('\n%-34s %9s %9s %14s' % ('', 'rel.L2', 'chi2_red', 'line-area err'))
    if len(Yrep):
        ri = d['rep_idx']; Yr, _ = fluo.apply_response(G, Yrep)
        nf = (np.linalg.norm(Yr - Yd[ri], axis=1) / np.linalg.norm(Yd[ri], axis=1)).mean() / np.sqrt(2)
        print('%-34s %9.4f %9s' % ('noise floor (repeat runs)', nf, '~1'))
    for name, pred in (('linear mixing', Ylin), ('linear + MLP (surrogate)', Ymlp)):
        for s in ('test', 'extrap'):
            i = sp[s]
            if len(i):
                r = metrics(E, pred[i], Yd[i], Yerrd[i], w[i])
                print('%-34s %9.4f %9.2f %13.1f%%' % (f'{name} [{s}]', r[0], r[1], 100 * r[2]))

    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(16, 4))
    ax[0].semilogy(np.array(hist)); ax[0].legend(['train', 'val']); ax[0].set_xlabel('epoch'); ax[0].set_title('loss (sqrt space)')
    for k, (j, a_) in enumerate(zip(sp['test'][:2], ax[1:])):
        a_.semilogy(E, Yd[j] + 1e-18, lw=.8, label='simulation'); a_.semilogy(E, Ylin[j] + 1e-18, lw=.8, label='linear mixing')
        a_.semilogy(E, Ymlp[j] + 1e-18, lw=.8, label='surrogate'); a_.set_ylim(Yd[j].max() * 1e-5, Yd[j].max() * 3)
        a_.set_title(formulas[j]); a_.set_xlabel('E [keV]'); a_.legend()
    fig.tight_layout(); fig.savefig(a.plot, dpi=110); print('figure ->', a.plot)


# ---------------------------------------------------------------- use a trained model
class Loaded:
    def __init__(self, path):
        ck = torch.load(path, map_location='cpu', weights_only=False)
        self.model = Surrogate(ck['B'], ck['S'], ck['hidden'], ck['layers']); self.model.load_state_dict(ck['state'])
        self.model.eval(); self.E, self.ck = ck['E'], ck

    @torch.no_grad()
    def predict(self, formula_or_w):
        """formula string ('Ti2Fe') or mass-fraction vector(s) -> spectrum (n, nE) [detector-convolved]"""
        w = fluo.mass_fractions(formula_or_w) if isinstance(formula_or_w, str) else np.asarray(formula_or_w)
        out = self.model.spectrum(torch.tensor(np.atleast_2d(w), dtype=torch.float32)).numpy()
        return out[0] if isinstance(formula_or_w, str) else out


def load_surrogate(path):
    return Loaded(path)


if __name__ == '__main__':
    main()
