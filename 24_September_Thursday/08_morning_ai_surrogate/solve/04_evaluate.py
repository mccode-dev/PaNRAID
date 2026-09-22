#!/usr/bin/env python3
"""
Step C: relative L2 error on the test set for the noise floor, the linear
baseline, and the XGBoost surrogate; plot a few predicted vs. simulated
spectra (log scale).

Usage:
    python 04_evaluate.py --model model.pkl --data dataset.npz
"""
import argparse
import pickle
import numpy as np
import matplotlib.pyplot as plt


def rel_l2(pred, true):
    return np.linalg.norm(pred - true, axis=1) / np.linalg.norm(true, axis=1)


def predict_intensity(model, X):
    S, pca, m = model["S"], model["pca"], model["model"]
    base = X @ S
    resid = pca.inverse_transform(m.predict(X))
    T_pred = base + resid
    return np.clip(T_pred, 0, None) ** 2


def estimate_noise_floor(repeat_pairs):
    """repeat_pairs: list of (I_a, I_b), two independent mxrun seeds of the
    SAME formula/ncount. This is the simulation's own statistical noise --
    the best any model could ever do. Generate these by rerunning a handful
    of formulas with `mxrun -s <different_seed> ...`."""
    errs = [np.linalg.norm(np.sqrt(a) - np.sqrt(b)) / np.linalg.norm(np.sqrt(a))
            for a, b in repeat_pairs]
    return np.array(errs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="model.pkl")
    ap.add_argument("--data", default="dataset.npz")
    ap.add_argument("--n-plot", type=int, default=4)
    args = ap.parse_args()

    with open(args.model, "rb") as f:
        model = pickle.load(f)
    d = np.load(args.data, allow_pickle=True)
    X, Y, formulas = d["X"], d["Y"], d["formulas"]

    base_pred = np.clip((X @ model["S"]) ** 2, 0, None)
    xgb_pred = predict_intensity(model, X)

    err_base = rel_l2(np.sqrt(base_pred), np.sqrt(Y))
    err_xgb = rel_l2(np.sqrt(xgb_pred), np.sqrt(Y))
    print(f"linear baseline   rel-L2 = {err_base.mean():.4f} +/- {err_base.std():.4f}")
    print(f"XGBoost surrogate rel-L2 = {err_xgb.mean():.4f} +/- {err_xgb.std():.4f}")
    print("(noise floor: rerun a few formulae with a different mxrun seed and")
    print(" feed the pairs to estimate_noise_floor() -- it needs real repeats)")

    idx = np.random.choice(len(X), size=min(args.n_plot, len(X)), replace=False)
    fig, axes = plt.subplots(1, len(idx), figsize=(4 * len(idx), 4), squeeze=False)
    for ax, i in zip(axes[0], idx):
        ax.semilogy(Y[i] + 1e-6, label="McXtrace", lw=1)
        ax.semilogy(xgb_pred[i] + 1e-6, label="XGB", lw=1, ls="--")
        ax.semilogy(base_pred[i] + 1e-6, label="linear", lw=1, ls=":")
        ax.set_title(str(formulas[i]))
        ax.legend(fontsize=7)
    plt.tight_layout()
    plt.savefig("spectra_comparison.png", dpi=150)
    print("Saved spectra_comparison.png")
