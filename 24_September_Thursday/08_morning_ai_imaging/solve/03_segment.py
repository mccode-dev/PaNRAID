{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 #!/usr/bin/env python3\
"""Segmentation of Debye-Scherrer rings: log scale + Otsu + morphology (+ watershed).\
\
  python 03_segment.py low-res/0/Sphere.dat [--multi] [--watershed]\
"""\
import argparse\
import numpy as np\
from scipy import ndimage as ndi\
from skimage import filters, morphology, measure, segmentation, feature\
import mcpsd\
\
\
def segment(I, sigma=1.0, multi=False, watershed=False, min_size=8):\
    Z, ref = mcpsd.to_log(I)                       # 1. log10 (zeros sit at the floor)\
    Zs = filters.gaussian(Z, sigma)                # 2. light smoothing: Otsu hates shot noise\
    vals = Zs[Z > 0]                               #    Otsu only on bins with signal, else\
    if multi:                                      #    the empty floor dominates the histogram\
        t = filters.threshold_multiotsu(vals, classes=3)[-1]   # background | diffuse | rings\
    else:\
        t = filters.threshold_otsu(vals)\
    mask = Zs > t\
    mask = ndi.binary_opening(mask, morphology.disk(1))    # 3. remove speckle\
    mask = ndi.binary_closing(mask, morphology.disk(2))    #    close gaps in rings\
    lab0, n0 = ndi.label(mask)                             #    drop tiny blobs\
    keep = np.isin(lab0, 1 + np.flatnonzero(ndi.sum(mask, lab0, range(1, n0 + 1)) >= min_size))\
    mask = keep\
    if watershed:                                  # 4. split touching rings\
        dist = ndi.distance_transform_edt(mask)\
        pk = feature.peak_local_max(dist, min_distance=4, labels=measure.label(mask))\
        mk = np.zeros_like(mask, int); mk[tuple(pk.T)] = np.arange(1, len(pk)+1)\
        labels = segmentation.watershed(-dist, mk, mask=mask)\
    else:\
        labels = measure.label(mask)\
    edges = feature.canny(Zs, sigma=1.5)           # optional edge map (OpenCV: cv2.Canny)\
    return labels, mask, edges, t, Z\
\
\
def report(labels, E0):\
    """Compare each region's mean 2theta with the expected reflections (LaB6, cubic)."""\
    _, _, tth = mcpsd.angle_maps(*labels.shape)\
    rings = mcpsd.expected_rings(E0)\
    rows = []\
    ids = np.arange(1, labels.max() + 1)\
    means = ndi.mean(tth, labels, ids); areas = ndi.sum(np.ones_like(tth), labels, ids)\
    for lab, area, t in zip(ids, areas, means):\
        s, tr = min(rings, key=lambda z: abs(z[1]-t))\
        rows.append((lab, area, t, tr, f'h2+k2+l2=\{s\}'))\
    return rows\
\
\
if __name__ == '__main__':\
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt\
    ap = argparse.ArgumentParser(); ap.add_argument('file')\
    ap.add_argument('--multi', action='store_true'); ap.add_argument('--watershed', action='store_true')\
    ap.add_argument('--out', default='segmentation.png'); a = ap.parse_args()\
    d = mcpsd.read_mccode_2d(a.file); E0 = float(d['params']['E0'])\
    labels, mask, edges, t, Z = segment(d['I'], multi=a.multi, watershed=a.watershed)\
    print(f'Otsu threshold (log-normalised) = \{t:.3f\}  -> \{labels.max()\} regions')\
    for lab, area, tm, tr, hk in report(labels, E0)[:15]:\
        print(f'  region \{lab:3d\}  area \{area:5.0f\} px  <2theta>=\{tm:6.2f\}  nearest ring \{tr:6.2f\} (\{hk\})')\
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))\
    ax[0].imshow(Z.T, origin='lower', extent=(-180, 180, -90, 90)); ax[0].set_title('log10 intensity')\
    ax[1].imshow(mask.T, origin='lower', extent=(-180, 180, -90, 90), cmap='gray'); ax[1].set_title('Otsu + morphology')\
    ax[2].imshow(np.ma.masked_equal(labels, 0).T % 20, origin='lower', extent=(-180, 180, -90, 90), cmap='tab20')\
    ax[2].set_title('labelled regions')\
    fig.tight_layout(); fig.savefig(a.out, dpi=110); print('figure ->', a.out)}