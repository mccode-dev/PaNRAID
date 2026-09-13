# Optics Exercises — Guides & Gravity (McStas) and Synchrotron Monochromators (McXtrace)

*PaNRAID School, Day 2 afternoon — follows the `McStas_McXtrace_Optics` lecture*

Unlike the Sources & Monitors exercises, the two tracks below build genuinely different instruments — a neutron guide is not "the same component under a different name" as an X-ray monochromator. So this sheet has two independent parts. Do whichever matches the code you're working in; if you have both McStas and McXtrace installed and time to spare, doing both is the best way to see where the shared physics (grazing-incidence reflection, Bragg's law) actually diverges in practice.

As before: look things up with `mcdoc <Component>` / `mxdoc <Component>` as you go rather than guessing parameter meanings, and plot with `mcplot*` / `mxplot-*`.

---

## Part A — McStas: a guide, gravity, and phase space

**What you're building:** source → straight neutron guide → monitors, then a look at what gravity actually does to a "cold" (long-wavelength) beam over a long flight path.

### A1 — Baseline: characterise the beam *without* a guide

1. Build a small instrument: `Source_gen` (or `Source_simple`) followed, a short distance later, by an `L_monitor` and a `PSD_monitor`. Use a source radius of a few cm, and focus it onto a small aperture (`focus_xw`, `focus_yh`) 10 m downstream — this is your guide entrance.
2. Add a `DivPos_monitor` right next to the `PSD_monitor` (McStas: 2D, position vs. divergence — one of the shared monitor types from the Sources & Monitors session).
3. Run it. This position–divergence picture is the beam's **phase space** at the guide entrance — you'll compare it to the same picture at the guide exit later.

**Checkpoint:** without any guide, how does the divergence at the aperture relate to the source size and the focusing distance you chose? (Hint: it's basically the geometry from the "anatomy of a simple source" picture.)

### A2 — Add a straight guide, and explore its geometry

4. Replace the aperture with a `Guide_gravity` component of length `l`, matching entrance size `w1`×`h1` to your source's focused footprint, and a modest exit size `w2`×`h2` (start with `w1=w2`, `h1=h2` for a straight channel). Set `m=2` (a common real supermirror coating value).
5. Put your `L_monitor`, `PSD_monitor` and `DivPos_monitor` trio again right after the guide exit.
6. Run it, then repeat with the guide length doubled and halved (keep everything else fixed). Compare the transmitted intensity (`L_monitor` total) each time.
7. Now repeat at fixed length but with `m` set to 1 and then 3. What happens to the transmitted divergence and intensity?

**Checkpoints**
- Longer guide, same entrance/exit size: intensity up, down, or unchanged — and why?
- What does increasing `m` actually buy you, physically? (Recall the critical-angle / total-external-reflection picture from the lecture — `m` is a multiple of *what*?)
- Look at the `DivPos_monitor` at the guide exit and compare it to the one from A1. Has the guide truncated the divergence, the position, or both?

### A3 — Does gravity matter here?

Gravity is switched off by default; `mcrun` (and `mcgui`) can enable it for every gravity-aware component in the instrument with the `--gravitation` (short: `-g`) flag — `Guide_gravity` is written specifically to integrate the parabolic trajectory this produces.

8. Take your Exercise A2 guide, but now push it to conditions where gravity is more likely to show up: a longer guide (say 30–50 m) and a longer wavelength (`lambda0` around 8–10 Å with a narrow `dlambda`, i.e. a "cold" beam).
9. Run once normally, then run again adding `-g` (or ticking "gravitation" in `mcgui`). Compare the `PSD_monitor` images from the two runs.

**Checkpoints**
- What do you see in the `PSD_monitor` with gravity on that isn't there with gravity off?
- The lecture noted the gravitational drop scales with wavelength and flight length. Try a shorter guide, or a shorter wavelength, with `-g` still on — does the effect shrink as expected?
- Would you expect this effect to matter more at a thermal beamline (~1–2 Å) or a cold beamline (~5–20 Å)? Does your simulation agree?

### A4 (stretch) — An elliptic nose, and phase-space "transport"

10. Replace the last ~20% of your guide's length with an `Elliptic_guide_gravity` section instead of continuing the straight channel (`mcdoc Elliptic_guide_gravity` for the geometry parameters — it focuses rather than just transports).
11. Compare the `DivPos_monitor` phase-space picture at the very end of the beamline to the straight-guide case from A2.

**Interpretation:** a straight guide mostly *preserves* the shape of phase space while cutting off what falls outside its acceptance; a focusing (elliptic) section actively *reshapes* it — trading spatial size for divergence, or vice versa, which is exactly the "brilliance transfer" idea behind putting a focusing guide segment right before a small sample.

**Extra:** if you want to go further with this, several McStas schools' repositories include a ready-made `Guide_BT_template.instr` plus a `plot_brill` notebook specifically for a proper brilliance-transfer normalisation — worth tracking down if this becomes a recurring beamline design task rather than a one-off exercise.

---

## Part B — McXtrace: a synchrotron monochromator

**What you're building:** a synchrotron-like source, then *either* a double-crystal Bragg monochromator (Track 1, detailed below) *or* a multilayer monochromator (Track 2, more self-directed). Track 1 is the more guided of the two — start there if this is your first monochromator instrument.

### B1 — Baseline: characterise the synchrotron beam

1. Build a small instrument with a `Source_gaussian`, e.g. `E0=8` (keV), `dE=0.5`, focused (`focus_xw`, `focus_yh`, `dist`) onto a small aperture a few tens of metres downstream — synchrotron beamlines are long. Check `mxdoc Source_gaussian` for the beam-size parameters (`sigmax`/`sigmay` or similar) if you want a more realistic footprint than the defaults.
2. Add an `E_monitor` (or `L_monitor`) and a `PSD_monitor` at the aperture to check the spectrum and footprint you're starting from.

### B2 — Track 1: a single Bragg crystal, then a double-crystal monochromator (DCM)

A `Bragg_crystal` is placed on a rotated `Arm`, exactly like the McStas monochromator exercise you may have seen before — only the rotation here happens in the vertical plane (rotation about the beam's horizontal axis), which is the usual convention for a synchrotron DCM.

3. Add an `Arm` called `xtal1_arm` a good distance after your source, `ROTATED (A1,0,0) RELATIVE` the source, with `A1` a new instrument parameter (default 0 for now).
4. Add a `Bragg_crystal` at that arm's position, using silicon's (111) reflection:
   ```c
   COMPONENT xtal1 = Bragg_crystal(length=0.05, width=0.02, V=160.1826, h=1, k=1, l=1, alpha=0)
   AT (0,0,0) RELATIVE xtal1_arm
   ```
   (`V=160.1826` Å³ is silicon's unit-cell volume; `h,k,l=1,1,1` selects the (111) reflection.)
5. Add a second `Arm`, `xtal1_out`, `AT (0,0,0) RELATIVE xtal1_arm`, `ROTATED (2*A1,0,0) RELATIVE xtal1_arm` — this carries the reflected beam's new direction forward, the same trick as the `Mono_out` arm in a neutron monochromator instrument.
6. Put an `E_monitor`/`L_monitor` and a `PSD_monitor` some distance after `xtal1_out`.
7. Use Bragg's law, $n\lambda = 2d\sin\theta$, to work out $\theta$ (and hence `A1`) for a chosen photon energy in your source's range (Si(111) has $d = 3.1356$ Å; convert energy to wavelength with $\lambda[\text{Å}] = 12.398 / E[\text{keV}]$). Set `A1` to that value and confirm the monitors downstream show your chosen energy coming through.
8. Do a rocking curve: scan `A1` a fraction of a degree either side of your calculated value and look at the transmitted intensity — you should see a peak right at your calculated angle.

**Checkpoints**
- How wide is your rocking curve, roughly, compared to a mosaic neutron monochromator's? (Recall the lecture's mosaicity comparison table — a perfect Si crystal should be *much* narrower.)
- What's the reflected beam's direction relative to the incoming beam once `A1` is set — and is that a beam you'd want to send straight to your sample, or does it need fixing?

Now turn your single crystal into a **double-crystal monochromator (DCM)**: a second crystal, mounted so the outgoing beam ends up parallel to the original incoming beam again (just displaced), which is what makes a DCM practical to use on a beamline where the sample and everything downstream shouldn't move every time you change energy.

9. A short distance after `xtal1_out`, add a second `Bragg_crystal` (identical parameters to the first) on its own arm, rotated by `-A1` relative to `xtal1_out` — i.e. the mirror image of the first reflection:
   ```c
   COMPONENT xtal2_arm = Arm()
   AT (0,0,gap) RELATIVE xtal1_out
   ROTATED (-A1,0,0) RELATIVE xtal1_out

   COMPONENT xtal2 = Bragg_crystal(length=0.05, width=0.02, V=160.1826, h=1, k=1, l=1, alpha=0)
   AT (0,0,0) RELATIVE xtal2_arm
   ```
10. Add a final `Arm`, `xtal2_out`, `ROTATED (-2*A1,0,0) RELATIVE xtal2_arm`, and put your `E_monitor`/`PSD_monitor` pair after it.
11. Run it and confirm: same energy as before, but is the beam direction now parallel to the very first, un-monochromated beam from B1?

**Checkpoints**
- Why does the second crystal need the *negative* of the first crystal's rotation, rather than the same rotation again?
- If you increase `gap` (the crystal-to-crystal spacing), what happens to the vertical offset between the incoming and outgoing beam? Would a beamline operator need to re-align anything downstream when they change photon energy (and hence `A1`, and hence this offset) on a real DCM?

### B2′ — Track 2 (alternative): a multilayer monochromator

A multilayer works on the same interference principle as a crystal, but with a synthetic, much coarser period — giving a broader bandpass and higher flux, at the cost of energy resolution.

12. Rather than a ready-made snippet, use the doc-reading skill from the Sources & Monitors exercises: run `mxdoc multilayer` (and/or `mxdoc Multilayer_elliptic`) to find the multilayer component(s) available in your McXtrace installation, and identify which parameters set the layer period and number of layers.
13. Swap `xtal1`/`xtal2` in your Track 1 instrument for a multilayer component instead, and re-run your rocking curve (or its energy-scan equivalent).

**Checkpoints**
- How does the width of your reflectivity/rocking curve compare to the Bragg-crystal case in B2 — narrower or broader?
- The lecture mentioned picking "one of the first side peaks" on a multilayer's reflectivity curve — what does that imply about a multilayer's reflectivity curve shape compared to a single sharp Bragg peak?

---

## Facilitator notes

- Part A (A1–A3) and Part B (B1–B2) are the core material; A4 and B2′ are natural extensions for fast finishers or a follow-up session, matching the "pick two of the three: CRLs, KB mirrors, monochromators" framing on the last lecture slide — a CRL-focused exercise (following the worked Be/Al stack example on slide 9) would be a natural third addition later.
- Bragg-crystal numbers in Part B (Si, V=160.1826 Å³) match the syntax already documented in this project's X-ray optics component notes; the DCM arm/rotation pattern follows the lecture's own worked snippet directly.
- As with the Sources & Monitors sheet, no starter `.instr` files are included here yet — happy to draft ready-to-run starters (and a `hints/` folder, as before) for either or both parts if that would help participants get moving faster.
