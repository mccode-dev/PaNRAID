# Optics Exercises — Guides & Gravity (McStas) and Synchrotron Monochromators (McXtrace)

*PaNRAID School, Day 2 afternoon — follows the `McStas_McXtrace_Optics` lecture*

Unlike the Sources & Monitors exercises, the two tracks below build genuinely different instruments — a neutron guide is not "the same component under a different name" as an X-ray monochromator. So this sheet has two independent parts. Do whichever matches the code you're working in; if you have both McStas and McXtrace installed and time to spare, doing both is the best way to see where the shared physics (grazing-incidence reflection, Bragg's law) actually diverges in practice.

As before: look things up with `mcdoc <Component>` / `mxdoc <Component>` as you go rather than guessing parameter meanings, and plot with `mcplot*` / `mxplot-*`. Every exercise below follows the same nine-part structure as the Sources & Monitors sheet — **Learning objectives, Physical background, Starting instrument, Task, Expected output, Questions for interpretation, Optional extension, Data-export step, Checkpoint / solution** — with "n/a" where a part genuinely doesn't apply.

## The general method used in this sheet

Both Part A and Part B apply the same underlying method for characterising an optical element, and you should recognise it as you go:

1. Run the source straight into a monitor, with **no** optical component in the way — this is your baseline.
2. Add exactly **one** optical component.
3. Compare the monitor output to the baseline.
4. Explain the change physically, using the taxonomy below.
5. Repeat step 2 with a systematic **parameter scan**, rather than one-off manual value changes.

Part A's A1 → A2 pair and Part B's B1 → B2 pair are each one full instance of this pattern; A2's length/`m` exploration and B2's rocking-curve scan are step 5.

## How to read a change in your monitor output

Whenever a monitor output changes after you add or adjust a component, sort what you're seeing into one or more of the following categories *before* trying to explain it physically. These distinctions matter beyond this exercise: an AI model trained on this kind of data cannot tell them apart on its own either, so mixing them without recording which is which is a direct route to a model that has learned an artefact of the simulation rather than the physics.

- **Geometrical effects** — a change in beam position, footprint size/shape, or divergence caused by geometry (distances, apertures, focusing) rather than anything about intensity or spectrum.
- **Spectral effects** — a change in the wavelength/energy content of the transmitted beam (a monochromator selecting a narrow band; a guide's `m`-value transmitting long wavelengths differently from short ones).
- **Intensity losses** — fewer rays, or less total ray weight, surviving to the monitor at all: absorption, a reflectivity below 1, an aperture vignetting part of the beam.
- **Resolution broadening** — a genuine physical widening of a peak or feature (mosaic spread, angular acceptance) — distinct from Monte Carlo noise or binning, which are simulation artefacts, not physics (see the Sources & Monitors sheet, Exercise 4).
- **Acceptance and collimation** — which rays are transmitted at all, given a combination of position and angle (a guide's critical angle, an aperture's size) — this is very often the underlying mechanism behind both an intensity loss and a resolution change above.
- **Artefacts from finite sampling** — apparent structure (streaks, patchiness, a "grainy" ring or spot) that comes from `ncount` or monitor binning, not from any physical effect — the same failure mode as Sources & Monitors, Exercise 4, now showing up downstream of an optical component instead of a bare source.

---

## Part A — McStas: a guide, gravity, and phase space

**What you're building:** source → straight neutron guide → monitors, then a look at what gravity actually does to a "cold" (long-wavelength) beam over a long flight path.

### A1 — Baseline: characterise the beam *without* a guide

**Learning objectives.** Establish the no-optic baseline that A2 will be compared against, and record the beam's phase space (position vs. divergence) before anything reshapes it.

**Physical background.** With no guide, a source focused onto a small aperture produces a divergence at that aperture set purely by the source size and the focusing distance — the same geometry as the "anatomy of a simple source" picture from the Sources & Monitors lecture.

**Starting instrument.** None yet — build from scratch or adapt your Sources & Monitors Exercise 2 instrument.

**Task.**
1. Build a small instrument: `Source_gen` (or `Source_simple`) followed, a short distance later, by an `L_monitor` and a `PSD_monitor`. Use a source radius of a few cm, and focus it onto a small aperture (`focus_xw`, `focus_yh`) 10 m downstream — this is your guide entrance.
2. Add a `DivPos_monitor` right next to the `PSD_monitor` (position vs. divergence — one of the shared monitor types from the Sources & Monitors session).
3. Run it.

**Expected output.** A `DivPos_monitor` picture showing divergence roughly proportional to (source size)/(focusing distance), with no truncation — this is the beam's phase space at the guide entrance, unmodified by anything downstream.

**Questions for interpretation.**
- Without any guide, how does the divergence at the aperture relate to the source size and the focusing distance you chose?
- Which of the taxonomy categories above describes this instrument's whole output — is there a spectral, intensity, or resolution effect to speak of yet, or purely a geometrical one?

**Optional extension.** n/a — this is deliberately the simplest possible baseline; A2 is the extension.

**Data-export step.** Log the simulation contract (parameters, seed, `ncount`, monitor settings, output files, software version) for this baseline run — you'll want it side by side with A2's when you compare.

**Checkpoint / solution.** You should have a saved `DivPos_monitor` plot labelled clearly as "no guide" — this is literally step 1 of the general method above, and everything in A2 is compared against it.

### A2 — Add a straight guide, and explore its geometry

**Learning objectives.** Perform steps 2–5 of the general method: add one optical component (a guide), compare against A1, explain the change, then scan a parameter systematically instead of by hand.

**Physical background.** A neutron guide transports rays by total external reflection below a critical angle that scales with `m` (a multiple of natural nickel's critical angle) and wavelength. Rays whose angle of incidence on the guide wall exceeds that critical angle for their wavelength are lost, not reflected — this is an acceptance/collimation effect with an intensity-loss and a spectral consequence (see the taxonomy above).

**Starting instrument.** Your A1 instrument. A ready-to-run starting point for the completed A2 geometry is available in [`hints/`](./hints/) (`exA2_mcstas_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

**Task.**
1. Replace the aperture with a `Guide_gravity` component of length `l`, matching entrance size `w1`×`h1` to your source's focused footprint, and a modest exit size `w2`×`h2` (start with `w1=w2`, `h1=h2` for a straight channel). Set `m=2` (a common real supermirror coating value).
2. Put your `L_monitor`, `PSD_monitor` and `DivPos_monitor` trio again right after the guide exit.
3. Run it, and directly compare the `DivPos_monitor` and `L_monitor` outputs to your A1 baseline — this is step 3 of the general method.
4. Now scan systematically instead of by hand. `mcrun` can scan a numeric instrument parameter natively:
   ```sh
   mcrun exA2_mcstas_starter.instr -N 5 guide_l=5,50 -n 1e6
   ```
   runs 5 evenly-spaced guide lengths between 5 m and 50 m in one command. Compare the transmitted intensity (`L_monitor` total) across the 5 points.
5. Now combine `guide_l` and `guide_m` into a single two-parameter **grid** scan using `-M`/`--multi`, which takes the cartesian product of every scanned parameter's points, together with `-N` given as a comma-separated list (one point count per parameter, in the order listed on the command line):
   ```sh
   mcrun exA2_mcstas_starter.instr -M -N 5,3 guide_l=5,50 guide_m=1,3 -n 1e6
   ```
   This runs 5 guide lengths × 3 `m`-values = 15 simulations in one command, each in its own output subdirectory — inspect that directory structure and confirm it matches the 5×3 grid. (`-M` support is a comparatively recent `mcrun` addition; check `mcrun --help` under "Parameter scan options" if this doesn't work on your installed version — older installations may only support the single-parameter form used in step 4.)

**Expected output.** Compared to A1: a narrower `DivPos_monitor` divergence spread (acceptance/collimation), a possible drop in `L_monitor` total intensity especially at longer wavelengths (intensity loss + spectral effect), but the same wavelength *centre* (the guide doesn't change the source spectrum, only which parts of it survive). The length scan should show intensity roughly flat or slowly falling with length for a good guide, and the `m` scan should show higher throughput and a wider accepted divergence at higher `m`.

**Questions for interpretation.**
- Longer guide, same entrance/exit size: intensity up, down, or unchanged — and why?
- What does increasing `m` actually buy you, physically? (Recall the critical-angle / total-external-reflection picture from the lecture — `m` is a multiple of *what*?)
- Look at the `DivPos_monitor` at the guide exit and compare it to A1. Has the guide truncated the divergence, the position, or both — and which taxonomy category is that?
- In your two-parameter scan (`guide_l` and `guide_m`), which one has the bigger effect on transmitted intensity in the ranges you tried? Would a single-parameter scan of either one, alone, have told you that?

**Optional extension.** Add an `E_monitor`/`L_monitor` comparison specifically at the *short*- and *long*-wavelength ends of your source band, and check whether the guide's transmission loss is wavelength-dependent — this is the spectral-effect side of what a real guide's `m`-value does.

**Data-export step.** Log the simulation contract for at least the `guide_l` scan: the full scan range and step count belong under `input_parameters`/`geometry_parameters` in the metadata schema (see [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md)) — a scan is many samples, not one, and each point needs its own record.

**Checkpoint / solution.** You should be able to point at a specific feature of your A2 `DivPos_monitor`/`L_monitor` output and say which A1 feature it changed, and which taxonomy category (geometrical, spectral, intensity, resolution, acceptance, artefact) explains that specific change.

### A3 — Does gravity matter here?

**Learning objectives.** Treat gravity itself as "one component added" in the sense of the general method — same instrument, one physical effect switched on — and see the geometrical consequence of a genuinely different force acting over a long flight path.

**Physical background.** Gravity is switched off by default; `mcrun` (and `mcgui`) can enable it for every gravity-aware component in the instrument with the `--gravitation` (short: `-g`) flag — `Guide_gravity` is written specifically to integrate the parabolic trajectory this produces. The expected drop scales with flight length squared and inversely with velocity squared (i.e. grows with wavelength).

**Starting instrument.** Your A2 guide instrument, pushed to conditions where gravity is more likely to show up.

**Task.**
1. Take your Exercise A2 guide, but now push it to conditions where gravity is more likely to show up: a longer guide (say 30–50 m) and a longer wavelength (`lambda0` around 8–10 Å with a narrow `dlambda`, i.e. a "cold" beam).
2. Run once normally, then run again adding `-g` (or ticking "gravitation" in `mcgui`). Compare the `PSD_monitor` images from the two runs — this is again steps 2–3 of the general method, with "gravity on" as the one thing added.
3. Repeat with a shorter guide, or a shorter wavelength, with `-g` still on, as a mini parameter scan of "how much does length/wavelength matter to this effect".

**Expected output.** With gravity on, the `PSD_monitor` image should show a vertical downward shift (and possibly some vertical smearing) that grows with guide length and wavelength; with a short guide or short wavelength, the shift should shrink toward negligible.

**Questions for interpretation.**
- What do you see in the `PSD_monitor` with gravity on that isn't there with gravity off? Which taxonomy category is this — geometrical, spectral, or something else?
- The lecture noted the gravitational drop scales with wavelength and flight length. Does your shorter/short-wavelength re-run confirm the effect shrinks as expected?
- Would you expect this effect to matter more at a thermal beamline (~1–2 Å) or a cold beamline (~5–20 Å)? Does your simulation agree?

**Optional extension.** Scan wavelength systematically with `-g` on (`mcrun ... -N 5 lambda0=2,12 -g`) and plot the vertical PSD centroid shift against wavelength — does it look quadratic-in-length, as the physics predicts?

**Data-export step.** Log the simulation contract for both the gravity-on and gravity-off runs — the `-g` flag itself belongs under `simulation_settings` in the metadata schema, since it is not an instrument parameter and is easy to forget to record.

**Checkpoint / solution.** You should be able to state, in one sentence, why turning gravity on or off is a command-line flag rather than an instrument parameter, and describe the shape of the effect (grows with length and wavelength) in your own words.

### A4 (stretch) — An elliptic nose, and phase-space "transport"

**Learning objectives.** Contrast a *transporting* guide section (straight) with a *reshaping* one (focusing), completing the phase-space picture started in A1.

**Physical background.** A straight guide mostly preserves the shape of phase space while cutting off what falls outside its acceptance; a focusing (elliptic) section actively reshapes it — trading spatial size for divergence, or vice versa. This is exactly the "brilliance transfer" idea behind putting a focusing guide segment right before a small sample.

**Starting instrument.** Your A2 straight-guide instrument.

**Task.**
1. Replace the last ~20% of your guide's length with an `Elliptic_guide_gravity` section instead of continuing the straight channel (`mcdoc Elliptic_guide_gravity` for the geometry parameters — it focuses rather than just transports).
2. Compare the `DivPos_monitor` phase-space picture at the very end of the beamline to the straight-guide case from A2.

**Expected output.** A phase-space picture (position vs. divergence) that is visibly reshaped — typically narrower in position and correspondingly wider in divergence near the focal point, or vice versa — rather than simply truncated the way A2's straight guide was relative to A1.

**Questions for interpretation.**
- Is the A4 phase-space picture a rescaled/rotated version of A2's, or a genuinely different shape? What does that tell you about "transport" vs. "reshaping"?
- Where would you want a focusing section like this on a real beamline, relative to the sample?

**Optional extension.** If you want to go further with this, several McStas schools' repositories include a ready-made `Guide_BT_template.instr` plus a `plot_brill` notebook specifically for a proper brilliance-transfer normalisation — worth tracking down if this becomes a recurring beamline design task rather than a one-off exercise.

**Data-export step.** Log the simulation contract, including the elliptic section's geometry parameters under `geometry_parameters`.

**Checkpoint / solution.** You should be able to describe, in physical terms rather than component names, the difference between a guide section that "transports" phase space and one that "reshapes" it.

---

## Part B — McXtrace: a synchrotron monochromator

**What you're building:** a synchrotron-like source, then *either* a double-crystal Bragg monochromator (Track 1, detailed below) *or* a multilayer monochromator (Track 2, more self-directed). Track 1 is the more guided of the two — start there if this is your first monochromator instrument.

### B1 — Baseline: characterise the synchrotron beam

**Learning objectives.** Establish the no-optic baseline (step 1 of the general method) that B2 will be compared against.

**Physical background.** A synchrotron source is broadband in energy; a monochromator's whole purpose is to narrow that band, which only makes sense to demonstrate once you've characterised the broad starting point.

**Starting instrument.** None yet — build from scratch.

**Task.**
1. Build a small instrument with a `Source_gaussian`, e.g. `E0=8` (keV), `dE=0.5`, focused (`focus_xw`, `focus_yh`, `dist`) onto a small aperture a few tens of metres downstream — synchrotron beamlines are long. Check `mxdoc Source_gaussian` for the beam-size parameters (`sigmax`/`sigmay` or similar) if you want a more realistic footprint than the defaults.
2. Add an `E_monitor` (or `L_monitor`) and a `PSD_monitor` at the aperture to check the spectrum and footprint you're starting from.

**Expected output.** A broad, roughly Gaussian energy spectrum centred on `E0` with width set by `dE`, and a footprint set by your focusing parameters.

**Questions for interpretation.**
- What band of energies does your source actually deliver to the aperture? How does that compare to the width you'd want after monochromation (B2, checkpoint on rocking-curve width)?

**Optional extension.** n/a — B2 is the extension.

**Data-export step.** Log the simulation contract for this baseline — you'll compare B2's `E_monitor` output against it directly.

**Checkpoint / solution.** You should have a saved `E_monitor` plot labelled "no monochromator" to compare B2 against.

### B2 — Track 1: a single Bragg crystal, then a double-crystal monochromator (DCM)

**Learning objectives.** Perform steps 2–5 of the general method with a Bragg crystal as the one added component: add it, compare to B1, explain the change (spectral narrowing, angular acceptance), then scan systematically (a rocking curve) instead of guessing the angle by hand.

**Physical background.** A `Bragg_crystal` is placed on a rotated `Arm`, exactly like the McStas monochromator exercise you may have seen before — only the rotation here happens in the vertical plane (rotation about the beam's horizontal axis), which is the usual convention for a synchrotron DCM. Bragg's law, `n*lambda = 2*d*sin(theta)`, fixes which energy is reflected at a given crystal angle; away from that angle, essentially nothing is reflected — a very sharp acceptance compared to a mosaic neutron monochromator.

**Starting instrument.** Your B1 instrument. A ready-to-run starting point for the single-crystal geometry (through step 6 below) is available in [`hints/`](./hints/) (`exB2_mcxtrace_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below. Turning it into the double-crystal monochromator (steps 9–11) is left for you either way.

**Task.**
1. Add an `Arm` called `xtal1_arm` a good distance after your source, `ROTATED (A1,0,0) RELATIVE` the source, with `A1` a new instrument parameter (default 0 for now).
2. Add a `Bragg_crystal` at that arm's position, using silicon's (111) reflection:
   ```c
   COMPONENT xtal1 = Bragg_crystal(length=0.05, width=0.02, V=160.1826, h=1, k=1, l=1, alpha=0)
   AT (0,0,0) RELATIVE xtal1_arm
   ```
   (`V=160.1826` Å³ is silicon's unit-cell volume; `h,k,l=1,1,1` selects the (111) reflection.)
3. Add a second `Arm`, `xtal1_out`, `AT (0,0,0) RELATIVE xtal1_arm`, `ROTATED (2*A1,0,0) RELATIVE xtal1_arm` — this carries the reflected beam's new direction forward, the same trick as the `Mono_out` arm in a neutron monochromator instrument.
4. Put an `E_monitor`/`L_monitor` and a `PSD_monitor` some distance after `xtal1_out`.
5. Use Bragg's law to work out `theta` (and hence `A1`) for a chosen photon energy in your source's range (Si(111) has `d = 3.1356` Å; convert energy to wavelength with `lambda[Angstrom] = 12.398 / E[keV]`). Set `A1` to that value and confirm the monitors downstream show your chosen energy coming through. Compare this `E_monitor` output directly to your B1 baseline — this is step 3 of the general method.
6. Instead of hand-scanning `A1` one value at a time, run the rocking curve as a proper `mxrun` scan:
   ```sh
   mxrun exB2_mcxtrace_starter.instr -N 21 A1=A1_calc-0.05,A1_calc+0.05 -n 1e6
   ```
   (substitute your calculated `A1_calc` on both ends of the range). Plot the transmitted intensity against `A1` — you should see a peak right at your calculated angle. If you also want to scan energy `E0` alongside `A1` as a two-parameter grid (to see how the rocking-curve peak position tracks with energy), use `-M`/`--multi` the same way as the guide-length/`m` grid in Part A, step 5.

Now turn your single crystal into a **double-crystal monochromator (DCM)**: a second crystal, mounted so the outgoing beam ends up parallel to the original incoming beam again (just displaced), which is what makes a DCM practical to use on a beamline where the sample and everything downstream shouldn't move every time you change energy.

7. A short distance after `xtal1_out`, add a second `Bragg_crystal` (identical parameters to the first) on its own arm, rotated by `-A1` relative to `xtal1_out` — i.e. the mirror image of the first reflection:
   ```c
   COMPONENT xtal2_arm = Arm()
   AT (0,0,gap) RELATIVE xtal1_out
   ROTATED (-A1,0,0) RELATIVE xtal1_out

   COMPONENT xtal2 = Bragg_crystal(length=0.05, width=0.02, V=160.1826, h=1, k=1, l=1, alpha=0)
   AT (0,0,0) RELATIVE xtal2_arm
   ```
8. Add a final `Arm`, `xtal2_out`, `ROTATED (-2*A1,0,0) RELATIVE xtal2_arm`, and put your `E_monitor`/`PSD_monitor` pair after it.
9. Run it and confirm: same energy as before, but is the beam direction now parallel to the very first, un-monochromated beam from B1?

**Expected output.** Compared to B1: a sharply narrowed `E_monitor` peak at your chosen energy (spectral effect) and a large intensity loss relative to the broadband baseline (intensity effect — most of the source's energy range is simply not reflected). The rocking-curve scan should show a narrow, roughly symmetric peak in transmitted intensity centred on `A1_calc`. The finished DCM should show the same energy as the single-crystal case but a beam direction parallel to the original B1 beam, offset vertically by an amount that grows with `gap`.

**Questions for interpretation.**
- How wide is your rocking curve, roughly, compared to a mosaic neutron monochromator's? (Recall the lecture's mosaicity comparison table — a perfect Si crystal should be *much* narrower.) Is that narrowness a resolution effect or an acceptance effect, in the taxonomy above — or both?
- What's the reflected beam's direction relative to the incoming beam once `A1` is set — and is that a beam you'd want to send straight to your sample, or does it need fixing?
- Why does the second crystal need the *negative* of the first crystal's rotation, rather than the same rotation again?
- If you increase `gap` (the crystal-to-crystal spacing), what happens to the vertical offset between the incoming and outgoing beam? Would a beamline operator need to re-align anything downstream when they change photon energy (and hence `A1`, and hence this offset) on a real DCM?

**Optional extension.** Scan `A1` (and hence energy) over a wide range with the finished DCM and build an intensity-vs-energy transmission curve — this is your first "instrument response function", the kind of curve a later preprocessing step would need to correct out of raw data before it becomes a fair training label.

**Data-export step.** Log the simulation contract for the rocking-curve scan in full — the scan range and point count, not just the final `A1` value, since the scan itself is the dataset here (21 samples, not one).

**Checkpoint / solution.** You should have a rocking-curve plot with a clearly identified peak position and width, and be able to state which taxonomy categories (spectral, intensity, resolution, acceptance) explain the single-crystal result, and which additional geometrical fact (beam offset) the DCM step fixes.

### B2′ — Track 2 (alternative): a multilayer monochromator

**Learning objectives.** Apply the same method (add one component, compare, explain, scan) to a structurally different monochromator technology, and contrast its resolution/acceptance trade-off with the Bragg crystal's.

**Physical background.** A multilayer works on the same interference principle as a crystal, but with a synthetic, much coarser period — giving a broader bandpass and higher flux, at the cost of energy resolution.

**Starting instrument.** Your B1 instrument, or your Track 1 instrument with the crystal(s) swapped out.

**Task.**
1. Rather than a ready-made snippet, use the doc-reading skill from the Sources & Monitors exercises: run `mxdoc multilayer` (and/or `mxdoc Multilayer_elliptic`) to find the multilayer component(s) available in your McXtrace installation, and identify which parameters set the layer period and number of layers.
2. Swap `xtal1`/`xtal2` in your Track 1 instrument for a multilayer component instead, and re-run your rocking curve (or its energy-scan equivalent) as an `mxrun` scan, the same way as B2 step 6.

**Expected output.** A broader, likely lower-peak-amplitude rocking/energy curve than the Bragg-crystal case, with the multilayer's reflectivity curve possibly showing side peaks rather than one sharp maximum.

**Questions for interpretation.**
- How does the width of your reflectivity/rocking curve compare to the Bragg-crystal case in B2 — narrower or broader? Is that difference a resolution effect, an acceptance effect, or both?
- The lecture mentioned picking "one of the first side peaks" on a multilayer's reflectivity curve — what does that imply about a multilayer's reflectivity curve shape compared to a single sharp Bragg peak?

**Optional extension.** Compare the *integrated* intensity (area under the curve, not just the peak height) between the Bragg-crystal and multilayer cases at similar central energy — which technology would you choose if flux mattered more than energy resolution for a given experiment?

**Data-export step.** Log the simulation contract for the multilayer scan, exactly as for B2's rocking curve.

**Checkpoint / solution.** You should be able to state, in one sentence, the flux-vs-resolution trade-off between a Bragg crystal and a multilayer monochromator, grounded in what you actually measured rather than the lecture slide alone.

---

*(Facilitator notes for this session are collected separately in [`Facilitator_Notes.md`](./Facilitator_Notes.md), not shown here.)*
