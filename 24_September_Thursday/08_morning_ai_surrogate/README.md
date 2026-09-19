# Day 4 — Wednesday 24 September (Morning): AI Surrogate (approximator)

*PaNRAID School, Day 4 morning — surrogate/approximator*

For this exercise, we build a model approximator, called a _surrogate_ model.

Surrogate: `Parameters` -> [ AI ] -> fast `Measurement`

**Aim**: Train a model to predict the a monitor directly from the parameters, bypassing the need for McXtrace simulations. 
This is especially relevant for heavy computations. 
The surrogate may be used to study the parameter distributions, such as in a Bayesian analysis.

For this exercise, we use the McXtrace `Test_Fluorescence` example. It computes a material fluorescence spectrum from its chemical formula. Edit the instrument file and identify its parts.

## Problem Definition

**Input**: Material stoichiometry, parameter `material`.

**Output**: The fluorescence spectrum from the simulation (`Data [...] I:` block), file `emon.dat`.

**Goal**: Train a model to predict the spectrum directly from the stoichiometry, bypassing the need for simulations.

## Generate Training Data

In order to simplifiy the exercise, we shall use a reduced set of atoms to combine into a chemical formula. this way we may create atom categories which can easily be sent to an AI. 

Select 5 different atoms with Z within 5 (B) and 55 (Cs), say Ti, Fe, Ge, Ru, Ag. 

We need to start a large number of simulations with chemical formula using these atoms, e.g. `Ti0.1Fe0.5Ge0Ru0.3Ag0.9`.
