# Day 4 — Thursday 24 September: AI Workflows and Challenge Work

## Morning: AI workflows

The morning offers three practical ways to combine AI with McStas or McXtrace simulations:

- [`08_morning_ai_imaging`](08_morning_ai_imaging): image deconvolution/denoising, and segmentation using simulated powder-diffraction data.
- [`08_morning_ai_optimise`](08_morning_ai_optimise): optimization of beamline parameters for improved flux and resolution.
- [`08_morning_ai_surrogate`](08_morning_ai_surrogate): training a surrogate model to approximate simulated fluorescence spectra.

## Tools to be used

Generic libraries:

- pytorch (CNN, U-net, ...)
- sk-learn
- sk-image
- xgboost (very fast and efficient)
- tabnet (fast and efficient)

McXtrace/McStas optimisation:

- based upon scipy.optimize **'powell'**, **'nelder-mead'**, 'cg', 'bfgs', 'newton-cg', 'l-bfgs-b', 'tnc', 'cobyla', 'slsqp', 'trust-constr', 'dogleg', 'trust-ncg', 'trust-exact', 'trust-krylov'

## Afternoon: team challenge

The afternoon is reserved for teams to work on the challenge that will be presented on Friday morning.

The challenge and its expectations are introduced on Monday 21 September. Read the full instructions in [`challenge.pdf`](../21_September_Monday/challenge.pdf) before starting, agree on the team objective and responsibilities, and use this session to complete the implementation, validate the result, and prepare the Friday presentation.
