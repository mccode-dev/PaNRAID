#!/usr/bin/env python3
"""
Step B: train  mass_fractions -> sqrt(spectrum)  as a correction to a linear
least-squares baseline, using XGBoost.

  target transform : sqrt(I)                         (as in the tutorial)
  baseline          : T ~ X @ S, S fit by np.linalg.lstsq  (5 effective spectra)
  model             : PCA(spectrum residual, ~64 comps) + XGBRegressor with
                       multi_strategy="multi_output_tree" (native multi-output
                       trees, requires xgboost >= 2.0). No autograd involved.

Usage:
    python 03_train_surrogate.py --data dataset.npz --out model
"""
import argparse
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
import xgboost as xgb

from elements import ELEMENTS


def rel_l2(pred, true):
    return np.linalg.norm(pred - true, axis=1) / np.linalg.norm(true, axis=1)


def fit_linear_baseline(X_train, T_train):
    """T ~ X @ S  (5 x n_bins), least squares -- the 5 'effective pure-element spectra'."""
    S, *_ = np.linalg.lstsq(X_train, T_train, rcond=None)
    return S


def train_xgb_on_residual(X_train, R_train, X_val, R_val, n_components=64,
                           n_estimators=600, max_depth=4, lr=0.05, seed=0):
    n_components = min(n_components, R_train.shape[0] - 1, R_train.shape[1])
    pca = PCA(n_components=n_components, random_state=seed)
    C_train = pca.fit_transform(R_train)
    C_val = pca.transform(R_val)

    try:
        model = xgb.XGBRegressor(
            n_estimators=n_estimators, max_depth=max_depth, learning_rate=lr,
            subsample=0.9, colsample_bytree=0.9, reg_lambda=1.0,
            objective="reg:squarederror", tree_method="hist",
            multi_strategy="multi_output_tree",  # xgboost >= 2.0
            random_state=seed, early_stopping_rounds=30, eval_metric="rmse",
        )
        model.fit(X_train, C_train, eval_set=[(X_val, C_val)], verbose=False)
    except TypeError:
        # fallback for xgboost < 2.0: one booster per PCA component
        from sklearn.multioutput import MultiOutputRegressor
        base = xgb.XGBRegressor(n_estimators=n_estimators, max_depth=max_depth,
                                 learning_rate=lr, subsample=0.9, colsample_bytree=0.9,
                                 reg_lambda=1.0, objective="reg:squarederror",
                                 random_state=seed)
        model = MultiOutputRegressor(base).fit(X_train, C_train)
    return pca, model


def predict_residual(pca, model, X):
    return pca.inverse_transform(model.predict(X))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset.npz")
    ap.add_argument("--out", default="model")
    ap.add_argument("--n-components", type=int, default=64)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-elements", type=int, default=None,
                     help="if set, train only on formulae with <= this many "
                          "distinct elements (for question C.2)")
    args = ap.parse_args()

    d = np.load(args.data, allow_pickle=True)
    X, Y, formulas = d["X"], d["Y"], d["formulas"]
    assert list(d["elements"]) == ELEMENTS

    T = np.sqrt(np.clip(Y, 0, None))

    if args.max_elements is not None:
        n_el = (X > 0).sum(axis=1)
        keep = n_el <= args.max_elements
        print(f"Restricting training pool to <= {args.max_elements}-element compounds: "
              f"{keep.sum()}/{len(X)}")
        X, T = X[keep], T[keep]

    # 75 / 10 / 15 split -> test_size=0.25 then 0.6 of that remainder
    X_train, X_tmp, T_train, T_tmp = train_test_split(X, T, test_size=0.25, random_state=args.seed)
    X_val, X_test, T_val, T_test = train_test_split(X_tmp, T_tmp, test_size=0.6, random_state=args.seed)
    print(f"train={len(X_train)}  val={len(X_val)}  test={len(X_test)}")

    S = fit_linear_baseline(X_train, T_train)
    base_train, base_val, base_test = X_train @ S, X_val @ S, X_test @ S

    R_train, R_val = T_train - base_train, T_val - base_val
    pca, model = train_xgb_on_residual(X_train, R_train, X_val, R_val,
                                        n_components=args.n_components, seed=args.seed)

    pred_base_test = base_test
    pred_xgb_test = base_test + predict_residual(pca, model, X_test)

    err_base = rel_l2(pred_base_test, T_test)
    err_xgb = rel_l2(pred_xgb_test, T_test)
    print(f"[test] linear baseline   rel-L2 = {err_base.mean():.4f} +/- {err_base.std():.4f}")
    print(f"[test] XGBoost surrogate rel-L2 = {err_xgb.mean():.4f} +/- {err_xgb.std():.4f}")

    with open(f"{args.out}.pkl", "wb") as f:
        pickle.dump({"S": S, "pca": pca, "model": model, "elements": ELEMENTS}, f)
    np.savez(f"{args.out}_test.npz", X_test=X_test, Y_test=T_test**2)
    print(f"Saved trained surrogate -> {args.out}.pkl")
