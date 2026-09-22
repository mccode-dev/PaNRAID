# Day 4 — Thursday 24 September (Afternoon): AI surrogate model for X-ray fluorescence

*PaNRAID School — surrogate models and inverse problems*

In this exercise, we build an **AI surrogate** of a Monte-Carlo simulation:

`composition` -> [ AI ] -> `fluorescence spectrum`

A McXtrace run takes seconds to minutes and is noisy. A trained network returns a spectrum in microseconds and,
being differentiable, can also be run *backwards* to estimate a composition from a measured spectrum.

We restrict ourselves to compounds built from **five elements: Ti, Fe, Ge, Ru, Ag**.
The `Fluorescence`component can simulate KLM line for atoms within Z=5 (B) and 56 (Cs)

--------------------------------------------------------------------------------
## Baseline: the instrument

We use the McXtrace `Test_samples/Test_Fluorescence` model (file `Test_Fluorescence.instr`). Edit the file and identify
its parts: the source, the `Fluorescence` sample (parameter `material=`, a chemical formula such as `"Fe2O3"`), and the
energy monitor `emon` (file `emon.dat`).

A single spectrum is computed with e.g.:
```
mxrun -d fe2o3 -n 1e6 Test_Fluorescence.instr material=Fe2O3
mxplot fe2o3
```

:arrow_right: Run the model and look at `emon.dat` (`head -40 emon.dat`) and identify the energy axis and the signal, in the `Data [...] I:` block.

--------------------------------------------------------------------------------
## A: Generating the training set

**Aim**: produce a few hundred (formula, spectrum) pairs.

Generate random formulae from `Ti Fe Ge Ru Ag`: a random number of elements (1 to 5), integer coefficients (e.g.
`Ti2FeAg3`), removing duplicates (`Ti2Fe2` and `TiFe` are the same material). Always include the 5 pure elements.

Then run the simulation for each formula in a loop (e.g. Python + `subprocess`, one `mxrun -d runs/<id> -n 1e6 ...
material=<formula>` per call). Make the loop restartable (skip directories that already exist). Read all the
`emon.dat` files into two arrays:
```python
X = mass_fractions(formula)          # (5,)  input
Y = read_emon("runs/00012/emon.dat") # (2001,) output: the `I` column
```

:arrow_right: Ask an AI to write both scripts (formula generator, and the run-and-collect loop).

--------------------------------------------------------------------------------
## B: Building the surrogate

**Aim**: learn `f(mass fractions) -> spectrum`.

- **Input**: the 5 mass fractions.
- **Target transform**: train on `sqrt(I)` rather than `I` — the noise is for Poissonian (but simulation provides a Gaussian noise), 
  so this keeps weak lines from being drowned out by strong ones. Invert with a square at the end.
- **Baseline**: fit `spectrum ≈ sum_i w_i * S_i` by least squares (linear mixing of 5 effective pure-element spectra).
- **Model**: a small MLP (5 -> 256 -> 256 -> 2001, GELU) trained to predict a *correction* to the linear baseline
  (initialise its last layer to zero, so training starts from the baseline). You may as well use _only_ an MLP (no Baseline fit), so, that it learns the fluorescence lines.

Split the data into train (~75%), validation (10%, to pick the best epoch) and test (15%, touched once). Train with
AdamW and a few hundred epochs (seconds to minutes on CPU). 

:arrow_right: Ask an AI to write `class Surrogate(nn.Module)`.

--------------------------------------------------------------------------------
## C: Evaluation

Report, on the **test** set, the relative L2 error `||pred - true|| / ||true||` for: the noise floor, the linear
baseline, and the MLP. Plot a few predicted vs simulated spectra (log scale).

Then answer:
1. How much better is the MLP than the linear baseline? How close is it to the noise floor?
2. Train only on compounds with at most 3 elements, and test on 4-5 element compounds. Does the MLP still beat the
   linear baseline on these unseen, more complex compositions?

--------------------------------------------------------------------------------
## D: Using the surrogate

1. **Speed**: time the prediction of 10 000 spectra and compare with one McXtrace run.
2. **Inverse problem**: ask an AI to inverse the surrogate (because it is differentiable). 
   Given a spectrum, find the mass fractions that best reproduce it. Parametrise
   `w = softmax(theta)` and optimise `theta` by gradient descent against the surrogate's prediction (a few random
   starts). How well are the fractions recovered?

--------------------------------------------------------------------------------
**Take-away**: a surrogate is only as good as the sampling of its input space, and it should always be judged
against the noise of the simulation and against a simple physics-based baseline.
