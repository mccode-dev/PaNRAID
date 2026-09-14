# Powder Diffraction with `PowderN` — Exercises

*PaNRAID School, Day 3 morning — follows the `McStas_McXtrace_Sample_Components` lecture*

`PowderN` exists under the same name, with the same shape parameters (`radius`, `yheight` for a cylindrical powder), in both McStas and McXtrace. What differs is what you're allowed to hand it as the material description via its `reflections=` parameter — and that's the main thing these exercises are here to show you, alongside the satisfying business of actually seeing Debye-Scherrer rings appear on a detector.

Keep both instruments deliberately tiny at first: **source → powder sample → flat detector**, nothing else. A monochromatic (or nearly so) beam gives the cleanest rings, since each (h,k,l) reflection then lands at one well-defined angle instead of smearing over a range of radii.

As always: `mcdoc PowderN` / `mxdoc PowderN` before guessing at a parameter, and plot with `mcplot*` / `mxplot-*`.

---

## Part A — McStas (neutrons)

### A1 — Baseline: source, sample, detector, rings

A ready-to-run starting point for this exact instrument is available in [`hints/`](./hints/) (`ex_powderN_mcstas_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

1. Build a minimal instrument: a `Source_simple` with a narrow wavelength band (e.g. `lambda0=2.5, dlambda=0.02`) focused onto a small aperture a few metres away — this is your sample position.
2. At that position, insert a cylindrical `PowderN` sample:
   ```c
   COMPONENT sample = PowderN(radius=0.005, yheight=0.03, reflections="Al.laz")
   AT (0,0,0) RELATIVE PREVIOUS
   ```
3. A short distance downstream, add a small `Beamstop` centred on the direct beam (to stop the huge unscattered peak from swamping everything else), and a large flat `PSD_monitor` at the same distance (e.g. 1×1 m, placed 0.3–0.5 m after the sample) to catch the scattered rays.
4. Run it (`1e6`–`1e7` rays) and plot the `PSD_monitor`. You should see one or more concentric rings.

**Checkpoints**
- Why rings, and not spots? (Think about what a "powder" physically is compared to the single crystal in a Laue-camera instrument.)
- Each ring is a cross-section of a Debye-Scherrer *cone* — why a cone, geometrically, given that every crystallite in the powder is randomly oriented but the scattering angle for a given (h,k,l) is fixed by Bragg's law?
- What happens to the sharpness of the rings if you widen `dlambda` a lot? Why?
- Try moving the detector further away, or closer. What changes about the ring radii, and why doesn't the *angle* of each ring change?

### A2 — Two ways to describe the same material: classic tables vs. NCrystal

`PowderN`'s `reflections=` parameter can take more than a plain `.laz`/`.lau` file of pre-computed structure factors — recent McStas versions can also hand the physics off to the NCrystal library for a given material.

5. Use `nctool -b` (or browse the [NCrystal material list](https://github.com/mctools/ncrystal/wiki)) to find the built-in NCrystal entry for aluminium (something like `Al_sg225.ncmat`).
6. Check `mcdoc PowderN` carefully for exactly how to point `reflections=` (or a related parameter — check your installed version) at an NCrystal material/cfg-string, and build a second instrument identical to A1 except for that one change.
7. Run both instruments with the same statistics and compare the two `PSD_monitor` ring patterns for what should be the *same* material (aluminium).

**Checkpoints**
- Do the ring positions (angles) agree between the two routes? Should they?
- NCrystal is a general-purpose neutron cross-section library with its own physics for thermal motion, absorption, and incoherent/inelastic backgrounds — where would you expect the two simulations to disagree, if anywhere, and why?
- `nctool -b` lists a large, curated set of real materials; a `.laz`/`.lau` file has to be generated (or found) separately for each one. What would make you reach for one route over the other on a real project?

### A3 (optional) — Attach yesterday's optics

8. If you built a working guide instrument in yesterday's Optics exercises, replace your `Source_simple` here with that guide's exit (source → guide → *this* sample position), the same way the earlier `templateDIFF`-style instrument in this repo goes source → monochromator → sample → detector. Does the beam divergence coming out of the guide broaden your rings into bands? If so, is that a guide problem or simply more realistic than a perfectly parallel pencil beam?

---

## Part B — McXtrace (X-rays)

### B1 — Baseline: source, sample, detector, rings

A ready-to-run starting point for this exact instrument is available in [`hints/`](./hints/) (`ex_powderN_mcxtrace_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

1. Build a minimal instrument: a near-monochromatic `Source_flat` (or `Source_gaussian`), e.g. around 10 keV with a narrow `dE`/`dlambda`, focused onto a small aperture a few metres away — your sample position.
2. At that position, insert a cylindrical `PowderN` sample using a CIF-described material — LaB₆ is the standard McXtrace `PowderN` test case:
   ```c
   COMPONENT sample = PowderN(radius=0.5e-4, yheight=1e-3, reflections="LaB6.cif")
   AT (0,0,0) RELATIVE PREVIOUS
   ```
   The first time this runs, McXtrace calls `cif2hkl` transparently to turn the CIF into structure factors — you don't have to run that step yourself.
3. As in Part A, add a small `Beamstop` plus a large flat `PSD_monitor` some distance downstream.
4. Run it and plot the rings.

**Checkpoints** — same as A1: why rings not spots, why a cone, what a wider energy band does to ring sharpness, what changing the detector distance does to the ring radii.

### B2 — Two ways to describe the same material: CIF vs. pre-computed tables

For `PowderN` in McXtrace, `reflections=` accepts either a CIF file — a full crystallographic description, converted on the fly — or a pre-computed `.lau`/`.laz`/`.hkl` list of structure factors, which skips that conversion step.

5. Generate a pre-computed file for the *same* LaB₆ structure, e.g. with `cif2hkl --powder --mode NUC -o LaB6.laz <your LaB6 CIF>` (you can get a LaB₆ CIF from the Crystallography Open Database, or reuse whichever CIF `cif2hkl` produced/consumed in step B1).
6. Build a second instrument identical to B1, except `reflections="LaB6.laz"` instead of `reflections="LaB6.cif"`.
7. Compare the two ring patterns, and compare how long each simulation took to start up.

**Checkpoints**
- Do the two routes agree on ring positions and intensities? Should they, given they describe the same crystal structure?
- What's the practical trade-off between handing `PowderN` a CIF directly versus pre-computing a `.laz`/`.lau` file once and reusing it?
- If you wanted to publish or share your instrument file for others to reproduce exactly, which route makes that easier?

### B3 (optional) — Attach yesterday's optics

8. If you built a working double-crystal (or multilayer) monochromator instrument in yesterday's Optics exercises, replace your `Source_flat`/`Source_gaussian` here with that monochromator's exit beam. Since your monochromator instrument already fixes a specific energy via Bragg's law, make sure your `PowderN` sample's rings land somewhere sensible for that energy — you may need to adjust the detector distance to see them comfortably.

---

*(Facilitator notes for this session are collected separately in [`Facilitator_Notes.md`](./Facilitator_Notes.md), not shown here.)*
