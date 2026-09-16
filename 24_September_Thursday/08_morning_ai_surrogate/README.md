# Day 4 — Wednesday 24 September (Morning): AI Surrogate (approximator)

*PaNRAID School, Day 4 morning — approximator*

For this exercise, we build a model approximator, called a _surrogate_ model.

Surrogate: `Parameters` -> [ AI ] -> fast `Measurement`

Aim: Train a model to predict the an monitor directly from the parameters, bypassing the need for McXtrace simulations. 
This is especially relevant for heavy computations. 
The surrogate may be used to study the parameter distributions, such as in a Bayesian analysis.

For this exercise, we use as well the `Test_SAXS` example.

## Problem Definition

**Input**: Parameters from the data files.

**Output**: The 2D image from the simulation (`Data [...] I:` block).

**Goal**: Train a model to predict the image directly from the parameters, bypassing the need for simulations.

## Generate Training Data


