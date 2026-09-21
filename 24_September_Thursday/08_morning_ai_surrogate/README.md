# Day 4 — Thursday 24 September (Afternoon): AI surrogate model for X-ray fluorescence

*PaNRAID School — surrogate models, emulators and inverse problems*

In this exercise, we build an **AI surrogate** of a Monte-Carlo simulation:

`composition` -> [ AI ] -> `fluorescence spectrum`

A McXtrace run takes seconds to minutes and is noisy. A trained network returns a smooth spectrum in microseconds, and
because it is differentiable it can be run *backwards* to estimate the composition from a measured spectrum.

We restrict ourselves to compounds built from **five elements: Ti, Fe, Ge, Ru, Ag**. Their K edges (4.97, 7.11, 11.10, 22.12, 25.51 keV)
are all below the incident energy (39 keV), so every element shows its K lines.

**Learning goals**
- generate a training set by *sampling the input space* of a simulation (here: random chemical formulae),
- choose a representation (features, target transform) that suits the physics and the noise,
- always compare with a simple baseline, and with the **noise floor** of the simulation itself,
- test interpolation *and* extrapolation,
- use the surrogate for something a simulation cannot easily do: fast evaluation and inversion.

--------------------------------------------------------------------------------
## Baseline: the instrument

We use the McXtrace `Test_samples/Test_Fluorescence` model (file `Test_Fluorescence.instr`).
Edit the instrument file and identify its parts:
- a small lab source `Source_flat` (E0=39 keV, half-width `dE`=0.06 keV) at 3 m from the sample,
- the `Fluorescence` sample: 1 x 1 x 0.1 mm, `material=` given as a **chemical formula** (e.g. `"Pb2SnO4"`),
- the `EXTEND` block, which absorbs the un-scattered photons and stores the interaction type in `Stype`,
- an energy monitor `emon` (`E_monitor`, 2001 bins from 0 to 1.5*E0), then a PSD, and one monitor per process
  (`Fluorescence.dat`, `Compton.dat`, `Rayleigh.dat`, `Si_Escape.dat`, `Si_PileUp.dat`).

A single spectrum is computed with e.g.:
```
mxrun -d fe2o3 -n 1e6 Test_Fluorescence.instr material=Fe2O3
mxplot fe2o3
```
The spectrum we want is in `emon.dat`. **Look at the file first** (`head -40 emon.dat`): identify the header
(`# variables:`, `# xlimits:`, ...) and the data block, and decide what is the energy axis and what is the signal `I`.
The values are in units of "signal per bin", i.e. tiny numbers (about 1e-12 for the whole spectrum).

**Questions to answer before going on**
1. The monitor is 0.1 m *behind* the sample, on the beam axis. What does that imply for the Compton peak position?
2. A bin is 58.5/2001 = 29 eV wide. How does this compare to a real silicon detector (about 150 eV FWHM at 6 keV)?
   The simulated lines are almost delta functions. We will add the detector response *after* the simulation.
3. Which physical effects are in the spectrum? Read the documentation of the `Fluorescence` component: does it include
   self-absorption? Secondary fluorescence (one element excited by the lines of another)? Escape and pile-up?
4. Ag K-alpha (22.16 keV) is just above the Ru K edge (22.12 keV), Ru K-alpha excites Ge, Fe, Ti, etc.
   In which direction do you expect the spectrum of a mixture to deviate from the sum of the pure-element spectra?

--------------------------------------------------------------------------------
## A: Generating the training set

**Aim**: produce a few hundred (formula, spectrum) pairs.

The input space is the composition, i.e. 5 mass fractions summing to 1. We create random formulae with
- a random number of elements (1 to 5) taken from `Ti Fe Ge Ru Ag`,
- integer stoichiometric coefficients from 1 to 6 (e.g. `Ti2FeAg3`) so that the formula is always understood by the component,
- **duplicates removed after dividing by the greatest common divisor**: `Ti2Fe2` and `TiFe` are the same material.

The pure elements are always included. Mixtures of 4-5 elements are rarer than 3-element ones when duplicates are removed:
check the distribution you obtain.

Then run the simulation for each formula. `material` is a string, so it cannot be scanned with `-N`: use a loop, e.g. in Python
with `subprocess` and a thread pool, one `mxrun -d runs/<id> -n 1e6 ... material=<formula>` per process:
```python
subprocess.run(['mxrun', '-d', f'runs/{i:05d}', '-n', '1e6', 'Test_Fluorescence.instr', f'material={formula}'])
```
Make the loop **restartable** (skip existing directories) and store the seed. Then read all `emon.dat` files, e.g.
```python
X = mass_fractions(formula)          # (5,)  input
Y = read_emon("runs/00012/emon.dat") # (2001,) output: the `I` column (the `Data [...] I:` block)
```
Ask an AI to write both scripts. Then re-run the first 20 formulae with another seed to measure the noise floor.

Choices to discuss:
- **Number of rays** (`-n`): trace elements need statistics. Compare 1e5 and 1e6 for a mixture with 5 % Ge.
- **Size of the set**: 300-500 compositions are enough for this exercise. What limits it in practice?
- **Detector response**: the network is asked to reproduce what a detector would measure. Convolve the simulated
  spectrum with an energy-dependent Gaussian, FWHM(E)^2 = FWHM0^2 + 2.355^2 F eps E (Si: F = 0.12, eps = 3.66 eV,
  FWHM0 about 0.1 keV). It is cheap, it can be changed later without re-running the simulation, and it makes the target much
  smoother. Try training with and without.

--------------------------------------------------------------------------------
## B: Building the surrogate

**Aim**: learn `f(mass fractions) -> spectrum`.

*Representation.* Use the 5 mass fractions as input (X-ray attenuation and fluorescence are governed by mass fractions, not by
atom counts). The output is the 2001-bin spectrum. Notice that the **line energies do not depend on the composition**
(E0 is fixed): only the amplitudes do. The network never has to move a peak.

*Target transform.* The noise is Poissonian, so large peaks are noisy in absolute terms and the background is not.
Train on `sqrt(I / I_scale)`: the noise then has a nearly constant variance and a plain mean-square loss is appropriate,
while the weak lines are not overwhelmed by the strong ones. Invert with a square.

*Baseline 1: linear mixing.* Physics tells us to first order `spectrum = sum_i w_i * S_i`. Fit the 5 effective pure-element
spectra `S_i` by least squares on the training set (5 x 2001 numbers). Report its error.

*Model: baseline + MLP.* A multi-layer perceptron (5 -> 256 -> 256 -> 256 -> 2001, GELU) that predicts a **correction** to the
linear baseline (initialise the last layer to zero, so training starts from the baseline). Physics does the bulk of the
work and the network only has to learn the matrix effects.

Split the data in train (about 75 %), validation (10 %, to select the epoch) and test (15 %, touched once).
Train with AdamW, one-cycle learning rate, a few hundred epochs (seconds to minutes on a CPU).

Ask an AI to write it: `class Surrogate(nn.Module)` with `forward(w)` and `spectrum(w)`.

--------------------------------------------------------------------------------
## C: Evaluation

A single number hides a lot. Report for the **test** set:
- the relative L2 error `||pred - true|| / ||true||`, for (i) the noise floor, (ii) the linear model, (iii) the MLP,
- the reduced chi-square on well-populated bins, using `I_err` (a perfect model gives about 1),
- the error on the **line areas** (K-alpha windows of each element): this is what an analyst cares about.

Then answer:
1. Where is the linear model wrong, and for which elements? Does it match your prediction from the questions above?
2. How far is the MLP from the noise floor? Is more data, a bigger network or more rays the remedy?
3. Plot a few test spectra (log scale). Do you see **spurious lines** for absent elements? A network knows nothing about the
   fact that no Fe in the sample means no line at 6.4 keV. How could you enforce it (e.g. multiply the amplitude of each line
   by a function that is exactly zero when `w_i = 0`)?

**Extrapolation test.** Train only on compounds with at most 3 elements, and test on compounds with 4-5 elements.
Compare the linear baseline and the surrogate. Why is this the relevant test for a tool that will be used on new materials?

--------------------------------------------------------------------------------
## D: Using the surrogate

1. **Speed**: time the prediction of 10 000 spectra and compare with one McXtrace run.
2. **Check against a new simulation**: pick a formula that is not in the training set, run McXtrace, and overlay the surrogate
   (with the same detector response).
3. **Inverse problem**: given a measured (or simulated) spectrum, find the mass fractions that minimise the difference with the
   surrogate. Parametrise `w = softmax(theta)`, use automatic differentiation (Adam) and several random starts.
   How well are the fractions recovered? Which element is the hardest, and why (think of Ge-Fe or Ru-Ag overlaps and of the
   absorption of Ti K-alpha at 4.5 keV)?
   Extension: the absolute intensity of a real measurement is unknown. Add a free scale factor to the fit.

--------------------------------------------------------------------------------
## E: Going further

- Add `E0` as an input (a new simulation grid, with the energies in a range where all edges are exceeded).
- Predict the separate `Fluorescence`, `Compton` and `Rayleigh` spectra (multi-task): they are more interpretable.
- Predict the PCA coefficients of the spectra instead of the 2001 bins.
- Ensembles of 5 networks give an uncertainty estimate. Is it larger where the training data are scarce?
- **Active learning**: simulate more where the surrogate and the linear model disagree most or where an ensemble is uncertain.
- Add trace elements (a few % of Ge in Fe): are they retained after the sqrt transform?

**Take-away.** A surrogate is only as good as the sampling of the input space, and it must be judged against the noise of the
simulation and against a physics-based baseline. Its gains are speed and differentiability, not accuracy beyond the
simulation.
