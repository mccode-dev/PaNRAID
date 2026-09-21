#!/usr/bin/env python3
"""U-Net for powder-diffraction detector images (deconvolution OR denoising).

  python 02_train_unet.py train --x low-res --y high-res --out deconv.pt
  python 02_train_unet.py train --x noisy   --y clean    --out denoise.pt
  python 02_train_unet.py apply --model deconv.pt --x new_low --y new_high   # + metrics/figure
"""
import argparse, os
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
import mcpsd


# ------------------------------------------------------------------- data
def load_paired_data(x_dir, y_dir, tol=1e-3):
    """Pair Sphere.dat files by their E0 header (not by directory number: robust to
    ordering). Both images are normalised with the SAME reference, taken from the
    input image, so that the mapping is invertible at inference time.
    Returns X, Y (n,1,H,W) float32, refs, energies."""
    xs, ys = mcpsd.load_dir(x_dir), mcpsd.load_dir(y_dir)
    yE = np.array([mcpsd.energy_of(d) for d in ys])
    X, Y, R, E = [], [], [], []
    for d in xs:
        e = mcpsd.energy_of(d)
        j = int(np.argmin(abs(yE - e)))
        if abs(yE[j] - e) > tol:
            print(f'no partner for E0={e}'); continue
        zx, ref = mcpsd.to_log(d['I'])
        zy, _ = mcpsd.to_log(ys[j]['I'], ref)
        X.append(zx); Y.append(zy); R.append(ref); E.append(e)
    return (np.stack(X)[:, None], np.stack(Y)[:, None], np.array(R), np.array(E))


# ------------------------------------------------------------------ model
def block(i, o):
    return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.GroupNorm(8, o), nn.GELU(),
                         nn.Conv2d(o, o, 3, padding=1), nn.GroupNorm(8, o), nn.GELU())


class UNet(nn.Module):
    """Encoder-decoder with skip connections. 3 down-samplings: 200 -> 100 -> 50 -> 25
    (4 levels would give 12.5 -> shape mismatch: pad to 208/256 if you want more).
    The network learns a *residual* (output = input + correction)."""

    def __init__(self, c_in=1, base=32):
        super().__init__()
        b = base
        self.e1, self.e2, self.e3 = block(c_in, b), block(b, 2*b), block(2*b, 4*b)
        self.mid = block(4*b, 8*b)
        self.up3 = nn.ConvTranspose2d(8*b, 4*b, 2, stride=2); self.d3 = block(8*b, 4*b)
        self.up2 = nn.ConvTranspose2d(4*b, 2*b, 2, stride=2); self.d2 = block(4*b, 2*b)
        self.up1 = nn.ConvTranspose2d(2*b, b, 2, stride=2);   self.d1 = block(2*b, b)
        self.out = nn.Conv2d(b, c_in, 1)

    def forward(self, x):
        e1 = self.e1(x)
        e2 = self.e2(F.max_pool2d(e1, 2))
        e3 = self.e3(F.max_pool2d(e2, 2))
        m = self.mid(F.max_pool2d(e3, 2))
        d3 = self.d3(torch.cat([self.up3(m), e3], 1))
        d2 = self.d2(torch.cat([self.up2(d3), e2], 1))
        d1 = self.d1(torch.cat([self.up1(d2), e1], 1))
        return x + self.out(d1)


# ---------------------------------------------------------------- training
def augment(x, y, crop=128):
    """Random crop + random flips. Flipping longitude/latitude is legitimate here:
    a powder pattern is symmetric about the beam axis (unpolarised source)."""
    n, _, H, W = x.shape
    i, j = np.random.randint(0, H-crop+1), np.random.randint(0, W-crop+1)
    x, y = x[..., i:i+crop, j:j+crop], y[..., i:i+crop, j:j+crop]
    if np.random.rand() < .5: x, y = x.flip(-1), y.flip(-1)
    if np.random.rand() < .5: x, y = x.flip(-2), y.flip(-2)
    return x, y


def train(a):
    torch.manual_seed(0); np.random.seed(0)
    X, Y, R, E = load_paired_data(a.x, a.y)
    n = len(X)
    val = np.arange(n) % 5 == 2                       # hold out every 5th energy
    Xt, Yt = map(torch.tensor, (X[~val], Y[~val])); Xv, Yv = map(torch.tensor, (X[val], Y[val]))
    print(f'{n} pairs: {len(Xt)} train / {len(Xv)} validation (E0 in {E[val].round(2)})')
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = UNet().to(dev)
    opt = torch.optim.AdamW(model.parameters(), 2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, total_steps=a.epochs * a.steps)
    best = 1e9
    for ep in range(a.epochs):
        model.train(); tot = 0
        for _ in range(a.steps):
            idx = np.random.randint(0, len(Xt), a.batch)
            bx, by = zip(*[augment(Xt[k:k+1], Yt[k:k+1]) for k in idx])
            bx, by = torch.cat(bx).to(dev), torch.cat(by).to(dev)
            loss = F.l1_loss(model(bx), by)            # L1 in log space: robust, keeps small signals
            opt.zero_grad(); loss.backward(); opt.step(); sched.step(); tot += loss.item()
        model.eval()
        with torch.no_grad():
            v = F.l1_loss(model(Xv.to(dev)), Yv.to(dev)).item()
            base = F.l1_loss(Xv, Yv).item()            # "do nothing" baseline
        print(f'epoch {ep+1:3d}  train {tot/a.steps:.4f}  val {v:.4f}  (identity baseline {base:.4f})')
        if v < best:
            best = v
            torch.save(dict(state=model.state_dict(), decades=mcpsd.DECADES), a.out)
    print('saved best model ->', a.out)


# --------------------------------------------------------------- inference
def load_model(path):
    ck = torch.load(path, map_location='cpu')
    m = UNet(); m.load_state_dict(ck['state']); return m.eval()


@torch.no_grad()
def deconvolve_psd(path, model='deconv.pt'):
    """Apply a trained model to a Sphere.dat file. Returns (input, output) in the
    original (linear) intensity units. Works for denoising models as well."""
    m = load_model(model) if isinstance(model, str) else model
    I = mcpsd.load_psd_file(path)
    Z, ref = mcpsd.to_log(I)
    out = m(torch.tensor(Z)[None, None])[0, 0].numpy()
    return I, mcpsd.from_log(np.clip(out, 0, None), ref)


def apply(a):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    m = load_model(a.model)
    xs = mcpsd.load_dir(a.x); ys = mcpsd.load_dir(a.y) if a.y else [None]*len(xs)
    _, _, tth = mcpsd.angle_maps()
    solid = np.cos(np.radians(mcpsd.angle_maps()[1]))
    for d, t in zip(xs, ys):
        E = mcpsd.energy_of(d)
        I, P = deconvolve_psd(d['path'], m)
        rows = [('input', I), ('U-Net', P)] + ([('target', t['I'])] if t else [])
        fig, ax = plt.subplots(1, len(rows)+1, figsize=(4.2*(len(rows)+1), 3.6))
        for k, (name, img) in enumerate(rows):
            Z, _ = mcpsd.to_log(img, mcpsd.reference(I))
            ax[k].imshow(Z.T, origin='lower', extent=(-180, 180, -90, 90), vmin=0, vmax=1.1)
            ax[k].set_title(name)
        # quantitative check: azimuthal profile and width of the strongest ring
        msg = f'E0={E:.2f} keV'
        for name, img in rows:
            x, y = mcpsd.radial_profile(img, tth, weights=solid)
            ax[-1].semilogy(x, y + 1e-30, label=name)
            t0 = x[np.argmax(np.where(x < 40, y, 0))]   # first strong (isolated) ring
            msg += f'  | {name}: FWHM({t0:.1f} deg)={mcpsd.peak_fwhm(x, y, t0):.2f} deg'
        if t:
            Zp, ref = mcpsd.to_log(P, mcpsd.reference(I)); Zt, _ = mcpsd.to_log(t['I'], ref)
            Zi, _ = mcpsd.to_log(I, ref)
            msg += f'  | log-L1 vs target: input {abs(Zi-Zt).mean():.4f} -> U-Net {abs(Zp-Zt).mean():.4f}'
        print(msg)
        ax[-1].set_xlabel('2theta [deg]'); ax[-1].legend(); ax[-1].set_title('radial profile')
        fig.tight_layout(); out = f'{os.path.splitext(a.model)[0]}_E{E:.1f}.png'
        fig.savefig(out, dpi=110); plt.close(fig); print('  figure ->', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
    t = sp.add_parser('train'); t.add_argument('--x', required=True); t.add_argument('--y', required=True)
    t.add_argument('--out', default='deconv.pt'); t.add_argument('--epochs', type=int, default=100)
    t.add_argument('--steps', type=int, default=20); t.add_argument('--batch', type=int, default=8)
    p = sp.add_parser('apply'); p.add_argument('--model', default='deconv.pt')
    p.add_argument('--x', required=True); p.add_argument('--y', default=None)
    a = ap.parse_args(); train(a) if a.cmd == 'train' else apply(a)
