# Optics Exercises — Guides & Gravity (McStas) and Synchrotron Monochromators (McXtrace)

*PaNRAID School, Day 2 morning — follows the `McStas_McXtrace_Optics` lecture*

**Time note.** Optics shares the Tuesday-morning session with Sources & Monitors instead of an exercise session on its own, so this sheet has been trimmed to two core exercises (one per code) plus optional "if time allows" material. 

Unlike the Sources & Monitors exercises, the two tracks below build genuinely different instruments — a neutron guide is not "the same component under a different name" as an X-ray monochromator. Do whichever matches the code you're working in; if you have both installed and time to spare, doing both is the best way to see where the shared physics (grazing-incidence reflection, Bragg's law) diverges in practice.

As before: look things up with `mcdoc <Component>`/`mxdoc <Component>` as you go, and plot with `mcplot*`/`mxplot-*`. To compare two runs, `mccoplot`/`mxcoplot` and `mcplotdiff`/`mxplotdiff` need **identically-named files from two different run directories** — they can't diff two differently-named monitors from a single run — so where an exercise below wants a comparison, give the two monitors you'd diff the same filename across the two runs.

## The method, and how to read a change

Both exercises below apply the same method for characterising an optical element:

1. Run the source straight into a monitor, with **no** optical component in the way — your baseline.
2. Add exactly **one** optical component, and compare the monitor output to the baseline.
3. Explain the change physically, using the categories below.
4. Repeat step 2 as a systematic **parameter scan**, rather than one-off manual value changes.

When a monitor output changes, sort what you're seeing into one or more of these categories *before* trying to explain it physically — the same distinctions that matter for Monte Carlo noise and binning in the Sources & Monitors sheet, now showing up downstream of an optical component instead of a bare source:

- **Geometrical** — a change in position, footprint size/shape, or divergence, from geometry (distances, apertures, focusing) rather than intensity or spectrum.
- **Spectral** — a change in the wavelength/energy content of the transmitted beam.
- **Intensity loss** — fewer rays (or less total ray weight) surviving to the monitor: absorption, reflectivity below 1, an aperture vignetting the beam.
- **Resolution / acceptance** — a genuine widening of a peak (mosaic spread, angular acceptance), or which rays get through at all given position+angle (critical angle, aperture size) — distinct from Monte Carlo noise or binning, which are simulation artefacts, not physics.

---

## Exercise 1 — McStas: a guide, and gravity in one flag

**Goal.** Establish a no-guide baseline, add a straight guide, compare and explain the change using the categories above, then scan a parameter properly instead of by hand.

**Task.**
1. Build a small instrument: a source (`Source_gen` or `Source_simple`, radius a few cm) focused onto a small aperture (`focus_xw`, `focus_yh`) 10 m downstream — this is your guide entrance. Add an `L_monitor`, `PSD_monitor` and `DivPos_monitor` trio right there. Run it — this is your baseline, with no guide.
2. Replace the aperture with a `Guide_gravity(l=guide_l, w1=w2=..., h1=h2=..., m=2)` — a straight channel matching your aperture size — and put the monitor trio at its exit instead. Use [`hints/exA2_mcstas_starter.instr`](./hints/) if you'd rather not type it out. Run and compare the `DivPos_monitor`/`L_monitor` to your baseline.
3. Scan properly instead of by hand:
   ```sh
   mcrun exA2_mcstas_starter.instr -N 5 guide_l=5,50 -n 1e6
   ```
   runs 5 evenly-spaced guide lengths between 5 and 50 m. Compare the transmitted intensity (`L_monitor` total) across the 5 points.
4. Add `-g` (`--gravitation`) to a run of a long (30–50 m), long-wavelength (`lambda0` 8–10 Å, narrow `dlambda`) version of your guide, and compare the `PSD_monitor` image to the same run without `-g`.

**Checkpoints.**
- You can point at a specific feature of your guide's `DivPos_monitor`/`L_monitor` output that changed relative to the baseline, and say which category (geometrical, spectral, intensity, resolution/acceptance) explains it.
- You can explain, in one sentence, why gravity is a command-line flag rather than an instrument parameter, and describe how the shift you saw should scale with guide length and wavelength.
- Log the simulation contract for the guide-length scan — the full range and step count belong under `geometry_parameters` in the metadata schema (see [`Data_Generation_Pipeline.md`](../../../../Data_Generation_Pipeline.md)); a scan is many samples, not one.

**If time allows.** Swap the last ~20% of the guide for an `Elliptic_guide_gravity` section instead of continuing the straight channel — a focusing section reshapes phase space (trading spatial size for divergence) rather than just truncating it the way a straight guide does; compare the `DivPos_monitor` picture to the straight-guide case. Or run a two-parameter grid over `guide_l` and `guide_m` together with `-M`/`--multi` (`-N` given as a comma-separated list, one point count per parameter):
```sh
mcrun exA2_mcstas_starter.instr -M -N 5,3 guide_l=5,50 guide_m=1,3 -n 1e6
```

---

## Exercise 2 — McXtrace: a Bragg-crystal monochromator

**Goal.** Establish the broadband synchrotron baseline, add a single Bragg crystal, hit a chosen energy via Bragg's law, compare to baseline, then run a proper rocking-curve scan.

**Task.**
1. Build a small instrument: `Source_gaussian` (e.g. `E0=8` keV, `dE=0.5`) focused onto a small aperture ~30 m downstream. Add an `E_monitor` and `PSD_monitor` there. Run it — this is your baseline.
2. Add a Si(111) `Bragg_crystal` on a rotated arm — [`hints/exB2_mcxtrace_starter.instr`](./hints/) already has this geometry built, with `A1=0` (crystal not yet on the Bragg condition). Work out `theta` from Bragg's law (`n*lambda = 2*d*sin(theta)`, Si(111) `d=3.1356` Å, `lambda[Å]=12.398/E[keV]`) for an energy in your source's range, set `A1` to that angle, and confirm the downstream monitors show your chosen energy coming through. Compare the `E_monitor` output to your baseline.
3. Run the rocking curve properly instead of hand-scanning `A1`:
   ```sh
   mxrun exB2_mcxtrace_starter.instr -N 21 A1=A1_calc-0.05,A1_calc+0.05 -n 1e6
   ```
   (substitute your calculated `A1_calc` on both ends). Plot transmitted intensity against `A1` — you should see a peak right at your calculated angle.

**Checkpoints.**
- You have a rocking-curve plot with a clearly identified peak position and width, and can say whether that narrowness is a resolution effect, an acceptance effect, or both, compared to a mosaic neutron monochromator.
- You can state the reflected beam's direction relative to the incoming beam once `A1` is set, and whether that's a beam you'd send straight to a sample.
- Log the simulation contract for the rocking-curve scan in full — the scan range and point count, not just the final `A1` value, since the scan itself is the dataset (21 samples, not one).

**If time allows.** Turn the single crystal into a double-crystal monochromator (DCM): add a second, identical `Bragg_crystal` a `gap` further on, on an arm rotated by `-A1` (the mirror image of the first reflection), followed by a final arm rotated by `-2*A1` — this restores a beam parallel to the original, un-monochromated beam (offset vertically by an amount that grows with `gap`), which is why real beamlines use two crystals rather than one. Or swap the crystal(s) for a multilayer (`mxdoc multilayer`) and compare its broader, higher-flux reflectivity curve to the Bragg-crystal case — the flux-vs-resolution trade-off between the two technologies.

---

*(Facilitator notes for this session are collected separately in [`Facilitator_Notes.md`](./Facilitator_Notes.md), not shown here.)*
