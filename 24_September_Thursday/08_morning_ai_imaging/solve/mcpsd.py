"""Shared helpers for the PaNRAID powder-diffraction AI session.

  * read/write McCode 2D detector files (Sphere.dat)
  * log-scale normalisation (invertible)
  * pixel -> scattering angle 2theta / Q for the 4PI monitor
  * radial (2theta) profile, peak-width metric
  * a small synthetic generator so everything can be tested without McXtrace
"""
import glob, os, re
import numpy as np

HC = 12.39842  # keV.Angstrom  (lambda[A] = HC / E[keV])
LAB6_A = 4.1569  # LaB6 cubic cell [Angstrom]


# --------------------------------------------------------------------------- IO
def read_mccode_2d(path):
    """Read a McCode 2D monitor file. Returns dict(I, I_err, N, params, xylimits).

    Arrays keep the on-disk orientation: shape (nx, ny), i.e. axis 0 = longitude,
    axis 1 = latitude. Use `I.T` with origin='lower' to display (as mxplot does).
    """
    with open(path) as f:
        lines = f.read().splitlines()
    header = [l for l in lines if l.startswith('#')]
    txt = '\n'.join(header)
    nx, ny = map(int, re.search(r'# type: array_2d\((\d+),\s*(\d+)\)', txt).groups())
    params = dict(re.findall(r'^# Param: (\w+)=(.*)$', txt, flags=re.M))
    lim = re.search(r'# xylimits: (.*)', txt)
    xylim = [float(v) for v in lim.group(1).split()][:4] if lim else [-180, 180, -90, 90]

    def block(tag):
        for i, l in enumerate(lines):
            if l.startswith('# ' + tag + ' ['):
                vals = []
                for l2 in lines[i + 1:]:
                    if l2.startswith('#'):
                        break
                    vals.append(l2)
                return np.loadtxt(vals).reshape(nx, ny) if vals else None
        return None

    return dict(I=block('Data'), I_err=block('Errors'), N=block('Events'),
                params=params, xylimits=xylim, nx=nx, ny=ny)


def load_psd_file(path):
    """Drop-in replacement for the tutorial's load_psd_file (robust to layout)."""
    return read_mccode_2d(path)['I']


def write_mccode_2d(path, I, N=None, params=None, xylim=(-180, 180, -90, 90)):
    nx, ny = I.shape
    N = np.zeros_like(I) if N is None else N
    with open(path, 'w') as f:
        f.write('# Format: McCode with text headers\n# Instrument: synthetic\n')
        for k, v in (params or {}).items():
            f.write(f'# Param: {k}={v}\n')
        f.write(f'# type: array_2d({nx}, {ny})\n# component: Sph_mon\n')
        f.write('# xylimits: %g %g %g %g\n# variables: I I_err N\n' % tuple(xylim))
        for tag, arr in (('Data', I), ('Errors', np.sqrt(np.abs(I))), ('Events', N)):
            f.write(f'# {tag} [Sph_mon/Sphere.dat] {"I" if tag=="Data" else tag}:\n')
            np.savetxt(f, arr, fmt='%.6e')


def energy_of(entry):
    return float(entry['params']['E0'])


def load_dir(directory, pattern='**/Sphere.dat'):
    """All Sphere.dat under `directory` (scan sub-dirs 0,1,2... or a single run),
    sorted by E0. Returns list of dicts."""
    out = []
    for p in glob.glob(os.path.join(directory, pattern), recursive=True):
        d = read_mccode_2d(p)
        d['path'] = p
        out.append(d)
    return sorted(out, key=energy_of)


# ---------------------------------------------------------- log normalisation
DECADES = 6.0


def reference(I, q=99.9):
    """Robust intensity scale (a max would be too noisy for low-statistics images)."""
    pos = I[I > 0]
    return float(np.percentile(pos, q)) if pos.size else 1.0


def to_log(I, ref=None, decades=DECADES):
    """log10 map to ~[0, 1]: value 1 <-> `ref`, 0 <-> ref*10**-decades (zero bins
    sit at the floor instead of -inf). Returns (Z float32, ref)."""
    ref = reference(I) if ref is None else ref
    floor = ref * 10.0 ** (-decades)
    Z = (np.log10(np.clip(I, floor, None)) - np.log10(floor)) / decades
    return Z.astype(np.float32), ref


def from_log(Z, ref, decades=DECADES):
    return ref * 10.0 ** ((np.asarray(Z, dtype=np.float64) - 1.0) * decades)


# ------------------------------------------------------------- geometry (4PI)
def angle_maps(nx=200, ny=200, xylim=(-180, 180, -90, 90)):
    """Longitude/latitude [deg] of pixel centres, shape (nx, ny), and the scattering
    angle 2theta [deg] w.r.t. the beam (+z). ASSUMES the beam hits lon=0, lat=0
    (check: the direct-beam/ring centre should be the centre of your image)."""
    lon = np.linspace(xylim[0], xylim[1], nx, endpoint=False) + (xylim[1] - xylim[0]) / nx / 2
    lat = np.linspace(xylim[2], xylim[3], ny, endpoint=False) + (xylim[3] - xylim[2]) / ny / 2
    LO, LA = np.meshgrid(np.radians(lon), np.radians(lat), indexing='ij')
    tth = np.degrees(np.arccos(np.clip(np.cos(LA) * np.cos(LO), -1, 1)))
    return np.degrees(LO), np.degrees(LA), tth


def q_map(E_keV, tth_deg):
    """Q [1/Angstrom] = 4 pi sin(theta) / lambda"""
    return 4 * np.pi * np.sin(np.radians(tth_deg) / 2) * E_keV / HC


def radial_profile(I, tth, bins=np.arange(0, 90.01, 0.25), weights=None):
    """Azimuthal average vs 2theta (only bins with data). The 4PI monitor has equal
    *angle* bins, so we weight by solid angle cos(lat) to get the true mean."""
    w = np.ones_like(I) if weights is None else weights
    s, _ = np.histogram(tth, bins, weights=I * w)
    n, _ = np.histogram(tth, bins, weights=w)
    c = 0.5 * (bins[1:] + bins[:-1])
    return c, s / np.maximum(n, 1e-30)


def peak_fwhm(x, y, x0, halfwin=1.5):
    """FWHM [x units] of the profile peak closest to x0 (crude, linear interp)."""
    m = (x > x0 - halfwin) & (x < x0 + halfwin)
    xs, ys = x[m], y[m]
    if ys.size < 3 or ys.max() <= 0:
        return np.nan
    half = ys.max() / 2
    above = np.where(ys >= half)[0]
    return float(xs[above[-1]] - xs[above[0]] + (x[1] - x[0]))


def expected_rings(E_keV, a=LAB6_A, hmax=6, tth_max=90):
    """2theta [deg] of the cubic-lattice reflections (primitive cell; LaB6 is P)."""
    lam = HC / E_keV
    hkl2 = sorted({h*h + k*k + l*l for h in range(hmax) for k in range(hmax)
                   for l in range(hmax)} - {0})
    out = []
    for s in hkl2:
        d = a / np.sqrt(s)
        if lam / (2 * d) < 1:
            t = 2 * np.degrees(np.arcsin(lam / (2 * d)))
            if t < tth_max:
                out.append((s, t))
    return out


# ------------------------------------------------------------ synthetic data
def synth_image(E0, dE, counts=1e6, nx=200, ny=200, seed=0):
    """Fake 4PI Debye-Scherrer map: Gaussian rings whose width contains an
    energy-spread term 2 tan(theta) dE/E, a smooth incoherent background and
    Poisson noise for `counts` detected events. For testing only!"""
    rng = np.random.default_rng(seed)
    LO, LA, tth = angle_maps(nx, ny)
    solid = np.cos(np.radians(LA))
    I = 0.02 * (1 + 0.5 * np.cos(np.radians(tth)))
    rings = expected_rings(E0)
    arng = np.random.default_rng(1234)                 # same 'crystal' for all images
    amp = {s: arng.uniform(0.3, 3.0) for s, _ in expected_rings(30, hmax=8, tth_max=180)}
    for s, t in rings:
        th = np.radians(t / 2)
        sig = np.degrees(np.sqrt((2 * np.tan(th) * dE / E0 / np.sqrt(3)) ** 2 + 0.03 ** 2))
        sig = np.hypot(sig, 0.9)          # pixel footprint (1.8 deg lon bins)
        I += amp.get(s, 1) * np.exp(-0.5 * ((tth - t) / sig) ** 2) / sig / (1 + 0.5 * np.sin(th))
    I = I * solid
    I *= counts / I.sum()
    N = rng.poisson(I).astype(float)
    return N / counts * 1e-11, N


def make_synthetic_scan(outdir, e_min, e_max, n, dE, counts=1e6, seed=0):
    for i, E0 in enumerate(np.linspace(e_min, e_max, n)):
        os.makedirs(f'{outdir}/{i}', exist_ok=True)
        I, N = synth_image(E0, dE, counts, seed=seed + i)
        write_mccode_2d(f'{outdir}/{i}/Sphere.dat', I, N, dict(E0=f'{E0:.4f}', dE=dE))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Create a synthetic scan (no McXtrace needed)')
    ap.add_argument('outdir'); ap.add_argument('--E', nargs=2, type=float, default=[10, 19])
    ap.add_argument('-N', type=int, default=11); ap.add_argument('--dE', type=float, default=1)
    ap.add_argument('--counts', type=float, default=1e6); ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    make_synthetic_scan(a.outdir, *a.E, a.N, a.dE, a.counts, a.seed)
