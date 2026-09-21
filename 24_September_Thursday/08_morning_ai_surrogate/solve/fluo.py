"""Helpers for the fluorescence-surrogate session (no torch needed here).

  * random formula generation / parsing / mass fractions
  * reader for McCode 1D monitor files (emon.dat)
  * detector energy-response (Si-like) applied after the simulation
  * line-area metric
  * a TOY spectrum generator (xraylib fundamental parameters) used as a stand-in
    for McXtrace when it is not available. It is NOT the McXtrace model.
"""
import math, os, re
from functools import reduce
import numpy as np

ELEMENTS = ['Ti', 'Fe', 'Ge', 'Ru', 'Ag']
ATOMIC_WEIGHT = dict(Ti=47.867, Fe=55.845, Ge=72.630, Ru=101.07, Ag=107.868)    # g/mol
DENSITY = dict(Ti=4.54, Fe=7.874, Ge=5.323, Ru=12.41, Ag=10.5)                   # g/cm3
# K-alpha2 / K-alpha1 energies [keV]
KALPHA = dict(Ti=(4.5049, 4.5108), Fe=(6.3908, 6.4038), Ge=(9.8553, 9.8864),
              Ru=(19.1504, 19.2792), Ag=(21.9903, 22.1629))
E0_DEFAULT, NE, EMAX_FACTOR = 39.0, 2001, 1.5     # as in Test_Fluorescence.instr


# ------------------------------------------------------------------ formulas
def parse_formula(s):
    """'Ti2FeAg0.5' -> {'Ti': 2.0, 'Fe': 1.0, 'Ag': 0.5}"""
    out = {}
    for el, n in re.findall(r'([A-Z][a-z]?)(\d*\.?\d*)', s):
        out[el] = out.get(el, 0) + (float(n) if n else 1.0)
    return out


def make_formula(counts):
    """counts: dict/array of integers per ELEMENTS -> 'Ti2FeAg3' (fixed element order)."""
    if not isinstance(counts, dict):
        counts = dict(zip(ELEMENTS, counts))
    return ''.join(f"{el}{int(n) if n > 1 else ''}" for el, n in counts.items() if n > 0)


def random_formulas(n, rng, max_count=6, size_probs=(.15, .3, .3, .15, .1)):
    """n unique random compounds from ELEMENTS: k elements (1..5), integer counts 1..max_count.
    Counts are divided by their gcd, so that 'Ti2Fe2' and 'TiFe' (same composition,
    hence the same spectrum) can never both be in the set."""
    seen, out = set(), []
    for i, el in enumerate(ELEMENTS):           # always include the pure elements
        seen.add(((i, 1),)); out.append(el)
    while len(out) < n:
        k = rng.choice(len(size_probs), p=size_probs) + 1
        els = sorted(rng.choice(len(ELEMENTS), k, replace=False))
        c = rng.integers(1, max_count + 1, k)
        c = c // reduce(math.gcd, c)
        key = tuple((els[i], c[i]) for i in range(k))
        if key in seen:
            continue
        seen.add(key)
        counts = np.zeros(len(ELEMENTS), int); counts[els] = c
        out.append(make_formula(counts))
    return out


def mass_fractions(formula):
    d = parse_formula(formula)
    m = np.array([d.get(el, 0.0) * ATOMIC_WEIGHT[el] for el in ELEMENTS])
    return m / m.sum()


def n_elements(formula):
    return len(parse_formula(formula))


# ------------------------------------------------------------------------ IO
def read_mccode_1d(path):
    """Read a McCode 1D monitor file (emon.dat).
    Returns dict(E, I, I_err, N, params). The usual layout is a text header (# lines,
    including '# variables: E I I_err N') followed by one column per variable; if only
    one column is found it is taken as I and E is rebuilt from '# xlimits'.
    -> ALWAYS look at your file first (`head -40 emon.dat`)."""
    hdr, rows = [], []
    with open(path) as f:
        for l in f:
            (hdr if l.startswith('#') else rows).append(l.strip())
    rows = [r for r in rows if r]
    txt = '\n'.join(hdr)
    params = dict(re.findall(r'^# Param: (\w+)=(.*)$', txt, flags=re.M))
    var = re.search(r'# variables: (.*)', txt)
    var = var.group(1).split() if var else ['E', 'I', 'I_err', 'N']
    a = np.loadtxt(rows, ndmin=2)
    if a.shape[1] == 1:
        lim = [float(v) for v in re.search(r'# xlimits: (.*)', txt).group(1).split()]
        n = a.shape[0]; E = lim[0] + (np.arange(n) + .5) * (lim[1] - lim[0]) / n
        return dict(E=E, I=a[:, 0], I_err=None, N=None, params=params)
    col = {v: a[:, i] for i, v in enumerate(var[:a.shape[1]])}
    return dict(E=col['E'], I=col['I'], I_err=col.get('I_err'), N=col.get('N'), params=params)


def write_mccode_1d(path, E, I, I_err, N, params, Emax):
    with open(path, 'w') as f:
        f.write('# Format: McCode with text headers\n# Instrument: Test_Fluorescence.instr (TOY synthetic data)\n')
        for k, v in params.items():
            f.write(f'# Param: {k}={v}\n')
        f.write(f'# type: array_1d({len(E)})\n# component: emon\n# filename: emon.dat\n')
        f.write(f'# xvar: E\n# xlabel: Energy [keV]\n# xlimits: 0 {Emax}\n# variables: E I I_err N\n')
        np.savetxt(f, np.c_[E, I, I_err, N], fmt='%.8e')


# ---------------------------------------------------------- detector response
def response_matrix(E, fwhm0=0.10, fano=0.12, eps_si=0.00366):
    """Gaussian energy resolution of a Si detector, FWHM(E)^2 = fwhm0^2 + 2.355^2 F eps E
    (E in keV). Column i = how a photon of energy E_i is spread over the bins; the
    total is conserved. Y_measured = G @ Y_simulated."""
    fwhm = np.sqrt(fwhm0 ** 2 + 2.355 ** 2 * fano * eps_si * E)
    sig = fwhm / 2.355
    G = np.exp(-0.5 * ((E[:, None] - E[None, :]) / sig[None, :]) ** 2)
    G /= G.sum(0, keepdims=True)
    return G


def apply_response(G, Y, Yerr=None):
    if G is None:
        return Y, Yerr
    Yd = Y @ G.T
    return Yd, (None if Yerr is None else np.sqrt((Yerr ** 2) @ (G.T ** 2)))


# ------------------------------------------------------------------- metrics
def line_areas(E, Y, half=0.15):
    """Sum of the signal in a window around each element's K-alpha doublet.
    Y: (..., nE). Returns (..., len(ELEMENTS))."""
    out = []
    for el in ELEMENTS:
        lo, hi = KALPHA[el]
        m = (E > lo - half) & (E < hi + half)
        out.append(Y[..., m].sum(-1))
    return np.stack(out, -1)


def energy_grid(E0=E0_DEFAULT, nE=NE):
    Emax = EMAX_FACTOR * E0
    return (np.arange(nE) + .5) * Emax / nE, Emax


# ------------------------------------------------------------------ toy model
def toy_spectrum(formula, E0=E0_DEFAULT, dE=0.06, thickness_cm=0.01):
    """Expected spectrum (arbitrary units per bin) of a slab measured in transmission
    geometry: primary K fluorescence (xraylib line cross sections) attenuated on the way
    in (E0) and out (line energy), plus Rayleigh + Compton at ~E0 (forward geometry:
    negligible Compton shift). No secondary fluorescence, no L lines. Toy!"""
    import xraylib as xl
    E, Emax = energy_grid(E0)
    w = mass_fractions(formula)
    Z = [xl.SymbolToAtomicNumber(e) for e in ELEMENTS]
    rho = 1.0 / np.sum(w / np.array([DENSITY[e] for e in ELEMENTS]))
    mu = lambda en: sum(wi * xl.CS_Total(z, en) for wi, z in zip(w, Z) if wi > 0)   # cm2/g
    mu0, t = mu(E0) * rho, thickness_cm
    S = np.zeros_like(E); db = Emax / len(E)
    lines = [xl.KL2_LINE, xl.KL3_LINE, xl.KM2_LINE, xl.KM3_LINE]
    for wi, z in zip(w, Z):
        if wi == 0 or E0 < xl.EdgeEnergy(z, xl.K_SHELL):
            continue
        for ln in lines:
            El = xl.LineEnergy(z, ln)
            prod = wi * xl.CS_FluorLine_Kissel(z, ln, E0)
            B = mu(El) * rho
            integ = t * math.exp(-mu0 * t) if abs(mu0 - B) < 1e-9 else \
                (math.exp(-B * t) - math.exp(-mu0 * t)) / (mu0 - B)
            S[min(int(El / db), len(E) - 1)] += rho * prod * integ / (4 * math.pi)
    ray = sum(wi * xl.CS_Rayl(z, E0) for wi, z in zip(w, Z) if wi > 0)
    com = sum(wi * xl.CS_Compt(z, E0) for wi, z in zip(w, Z) if wi > 0)
    el = (1.5 * ray + 1.0 * com) * rho * t * math.exp(-mu0 * t) / (4 * math.pi)
    m = (E > E0 - dE) & (E < E0 + dE)
    S[m] += el / m.sum()
    return E, S * 1e-11, Emax


def toy_run(outdir, formula, counts=1e6, seed=0, E0=E0_DEFAULT, dE=0.06):
    """Write outdir/emon.dat as McXtrace would (Poisson-like noise for `counts` rays)."""
    rng = np.random.default_rng(seed)
    E, S, Emax = toy_spectrum(formula, E0, dE)
    p = S / S.sum()
    N = rng.poisson(counts * 0.05 * p).astype(float)          # 5 % of rays end up on emon
    wray = S.sum() / max(N.sum(), 1)                          # weight per event
    os.makedirs(outdir, exist_ok=True)
    write_mccode_1d(f'{outdir}/emon.dat', E, N * wray, np.sqrt(N) * wray, N,
                    dict(material=formula, E0=E0, dE=dE), Emax)
