#!/usr/bin/env python3
"""
Step D:
  D1: time 10,000 surrogate predictions and compare with one mxrun call.
  D2: inverse problem -- recover mass fractions from a spectrum.
      XGBoost trees aren't differentiable, so instead of backprop this
      optimises theta with L-BFGS-B (scipy computes a numerical gradient
      by finite differences); since the surrogate call is microseconds,
      this is still fast. w = softmax(theta), a few random restarts.

Usage:
    python 05_inverse_and_speed.py --model model.pkl --data dataset.npz
"""
import argparse
import pickle
import time
import numpy as np
from scipy.optimize import minimize

from elements import ELEMENTS


def predict_intensity(model, X):
    S, pca, m = model["S"], model["pca"], model["model"]
    base = X @ S
    resid = pca.inverse_transform(m.predict(X))
    return np.clip(base + resid, 0, None) ** 2


def softmax(theta):
    e = np.exp(theta - theta.max())
    return e / e.sum()


def inverse_fit(model, target_I, n_starts=8, seed=0):
    rng = np.random.default_rng(seed)
    target_T = np.sqrt(np.clip(target_I, 0, None))

    def loss(theta):
        w = softmax(theta)
        pred_T = np.sqrt(predict_intensity(model, w[None, :]))[0]
        return np.sum((pred_T - target_T) ** 2)

    best = None
    for _ in range(n_starts):
        theta0 = rng.normal(size=len(ELEMENTS))
        res = minimize(loss, theta0, method="L-BFGS-B")
        if best is None or res.fun < best.fun:
            best = res
    return softmax(best.x), best.fun


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="model.pkl")
    ap.add_argument("--data", default="dataset.npz")
    args = ap.parse_args()

    with open(args.model, "rb") as f:
        model = pickle.load(f)
    d = np.load(args.data, allow_pickle=True)
    X, Y, formulas = d["X"], d["Y"], d["formulas"]

    # ---- D1: speed ----
    n = 10_000
    X_rand = np.random.dirichlet(np.ones(len(ELEMENTS)), size=n)
    t0 = time.perf_counter()
    _ = predict_intensity(model, X_rand)
    t1 = time.perf_counter()
    print(f"{n} surrogate predictions: {t1 - t0:.3f} s total, "
          f"{(t1 - t0) / n * 1e6:.1f} us/spectrum")
    print("Compare with a single `mxrun ... -n 1e6` call (seconds to minutes).")

    # ---- D2: inverse problem, on a test-set spectrum ----
    i = 0
    w_hat, resid = inverse_fit(model, Y[i])
    print(f"\nTrue formula:        {formulas[i]}  w={np.round(X[i], 3)}")
    print(f"Recovered fractions: w={np.round(w_hat, 3)}  (final loss={resid:.4g})")
    print(f"|w_hat - w_true| (L1) = {np.abs(w_hat - X[i]).sum():.4f}")
