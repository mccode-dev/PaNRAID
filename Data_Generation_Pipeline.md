# Data Generation Pipeline: From Instrument to AI Model

*PaNRAID School — cross-cutting reference, relevant from Day 2 (Sources & Monitors) through Day 5 (Inference)*

The course objective is to combine multi-scale material simulations and digital twins of X-ray/neutron facilities — instrumental effects and artefacts included — into supervised-learning datasets. Days 2–3 build the instrument- and sample-side half of that (McStas/McXtrace instruments, realistic sources, optics, samples); Days 4–5 build the AI-side half (training, inference). This document is the missing middle: a single, explicit description of how a McStas/McXtrace simulation run becomes one row of a labelled dataset, so that the join between the two halves is a reproducible procedure rather than an assumption.

Two ideas carry the whole document. First, every simulation run needs a **simulation contract** — the fixed set of facts that let anyone reproduce, or at least correctly interpret, that run — introduced in the Day 2 Sources & Monitors exercises (see [`Exercises_Sources_and_Monitors.md`](./22_September_Tuesday/04_morning_sources_detectors/Sources_Monitors/Exercises_Sources_and_Monitors.md#recording-a-simulation-contract)) and used throughout Days 2–3. Second, every dataset sample needs a fixed **metadata schema** — one record per run, built directly from that contract plus the run's outputs and labels. The schema below is that record.

---

## The pipeline

```text
physical parameters
        |
        v
material / sample model            (NCrystal, xraylib, CIF, DFT/MD input — Day 3)
        |
        v
McStas or McXtrace instrument       (Days 2-3: sources, optics, samples)
        |
        v
raw simulated detector/monitor output   (.dat / .h5 / .mcpl files, per the simulation contract)
        |
        v
instrument corrections and artefacts    (binning, dead time, background, resolution — as modelled)
        |
        v
preprocessing                       (normalisation, cropping, unit conversion, denoising choices — made explicit, never silent)
        |
        v
labelled dataset                    (one record per run: inputs + processed output + target label)
        |
        v
train / validation / test split     (split by *underlying physical sample/instrument config*, not by file, to avoid leakage — see below)
        |
        v
AI model                            (Day 4)
        |
        v
inference and physical evaluation   (Day 5: does the model use physics, or a simulation artefact?)
```

Each arrow in this diagram is a session, or part of one, somewhere in the programme:

| Stage | Where it's built in this school |
|---|---|
| Physical parameters | Set by you, as instrument/component parameters, in every exercise from Day 2 onward |
| Material / sample model | Day 3 morning (`PowderN`, NCrystal/xraylib materials — [`Exercises_PowderN.md`](./23_September_Wednesday/06_morning_samples_1/Exercises_PowderN.md), [`Batteries/README.md`](./23_September_Wednesday/06_morning_samples_1/Batteries/README.md)) and Day 3 afternoon (spectroscopy, SANS) |
| McStas/McXtrace instrument | Day 2 morning (sources & monitors, optics — combined), Day 3 (samples) |
| Raw detector/monitor output | Every `mcrun`/`mxrun` invocation — governed by the simulation contract |
| Instrument corrections & artefacts | Discussed per-exercise (e.g. finite binning, beamstop shadow, guide acceptance) — not yet a dedicated pass; a natural Day 3/4 bridge topic |
| Preprocessing | Not yet formalised in this repo — a concrete candidate for the start of Day 4 |
| Labelled dataset | The metadata schema below, applied to a batch of runs (e.g. the PowderN wavelength × material scan) |
| Train/validation/test split | Day 4 |
| AI model | Day 4 |
| Inference & physical evaluation | Day 5 |

The point of writing this out is that the "raw output → labelled dataset" half is presently the least specified part of the programme. The rest of this document proposes one concrete, minimal way to specify it.

---

## Per-sample metadata schema

One record per simulation run (per "sample" in the AI sense — not to be confused with the physical sample inside the instrument). Every field should be filled from what `mcrun`/`mxrun` and the instrument file already know; nothing here should require the student to remember a value by hand.

| Field | Meaning | Where it comes from |
|---|---|---|
| `sample_id` | Unique identifier for this run/record | Assigned when the record is created (e.g. output directory name) |
| `instrument_id` | Which `.instr` file, and which named exercise/track it corresponds to | Instrument filename + your own tracking (e.g. exercise number) |
| `software_version` | McStas/McXtrace version used | `mcstas --version` / `mcxtrace --version`, or `mcrun`'s/`mxrun`'s own startup banner |
| `random_seed` | Monte Carlo seed | `--seed=<N>` if you set one explicitly; otherwise record that it was *not* fixed for that run (see the Sources & Monitors exercise on why this matters) |
| `input_parameters` | The full set of instrument-parameter values actually used for this run | The command line / scan table you ran with — not "defaults", the resolved numeric values |
| `geometry_parameters` | Component positions, rotations, sizes relevant to the physics | Usually a subset of `input_parameters`, called out separately because it's what a geometry-aware model would need |
| `source_parameters` | Source type and its settings (wavelength/energy band, size, divergence/focusing) | Subset of `input_parameters` |
| `detector_parameters` | Monitor type(s), binning, limits, `options=` string, distance/size | Subset of `input_parameters` + the monitor components used |
| `simulation_settings` | `ncount`, MPI/thread count if used, any `--gravitation` or similar mode flags | The `mcrun`/`mxrun` command line |
| `raw_output` | Path(s) to the unmodified monitor output file(s) | Whatever `-d <dir>` / default output directory `mcrun`/`mxrun` wrote |
| `processed_output` | Path to whatever preprocessing produced (normalised array, cropped image, extracted peak list, …) | Your preprocessing step — and the *procedure*, not just the result, should be recorded or scripted, not done by hand once and forgotten |
| `target_labels` | The physical quantity the model is meant to learn (material identity, lattice parameter, defect class, state of charge, …) | Known because you generated the run — this is what makes it a *supervised* sample |

None of this is bookkeeping for its own sake. If a model performs suspiciously well, the first thing to check is whether train and test records share something in `simulation_settings` or `random_seed` that has nothing to do with `target_labels` — that's data leakage, and it's invisible unless the metadata exists to check.

### Worked example

One record from the wavelength × material scan built in the PowderN exercises ([`Exercises_PowderN.md`](./23_September_Wednesday/06_morning_samples_1/Exercises_PowderN.md), Exercise A4):

```json
{
  "sample_id": "powderN_mcstas_0007",
  "instrument_id": "ex_powderN_mcstas_starter.instr",
  "software_version": "McStas 3.5.1",
  "random_seed": null,
  "input_parameters": {
    "lambda0": 2.5,
    "dlambda": 0.02,
    "dist_sample": 3,
    "dist_detector": 0.4,
    "reflections": "Cu.laz"
  },
  "geometry_parameters": {
    "dist_sample": 3,
    "dist_detector": 0.4
  },
  "source_parameters": {
    "type": "Source_simple",
    "lambda0": 2.5,
    "dlambda": 0.02
  },
  "detector_parameters": {
    "type": "PSD_monitor",
    "xwidth": 1,
    "yheight": 1,
    "nx": 200,
    "ny": 200
  },
  "simulation_settings": {
    "ncount": 1e7,
    "mpi": null
  },
  "raw_output": "scan_Cu/lambda0_2.5/rings.dat",
  "processed_output": "processed/powderN_mcstas_0007_rings_normalised.npy",
  "target_labels": {
    "material": "Cu",
    "lambda0": 2.5
  }
}
```

`random_seed: null` here is itself meaningful — it records that this run relied on an unfixed seed, which matters for whether it can be exactly reproduced (see the simulation contract discussion).

---

## Splitting without leakage

A train/validation/test split must be drawn along the same lines a real generalisation test would use — not by file, not by row. If several `random_seed` values were simulated for the *same* `input_parameters` (to build up statistics or study MC noise, as in the Sources & Monitors exercise on statistics), all of them belong in the same split: putting seed-1 in train and seed-2 in test for otherwise-identical settings lets a model "cheat" by memorising the instrument's non-physical quirks rather than learning the physics in `target_labels`. Split by the physical configuration (material, geometry, source condition) that the model is actually meant to generalise across, and only then, within each configuration, decide whether repeated-seed runs stay together or exist to test seed-robustness specifically.

## Practical next step

This document doesn't yet ship a reference implementation — deliberately: a first concrete instance of the pipeline (a small script that walks a batch of `mcrun`/`mxrun` output directories, fills in this schema automatically from each run's command line and monitor-file headers, and writes one `manifest.json`/`manifest.csv` per batch) is a natural and genuinely useful thing to build together at the start of Day 4, using the PowderN wavelength × material scan from Day 3 as the first real dataset to run it on.
