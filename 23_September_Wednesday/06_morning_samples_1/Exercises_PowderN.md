# Powder Diffraction with `PowderN` — Exercises

*PaNRAID School, Day 3 morning — follows the `McStas_McXtrace_Sample_Components` lecture*

`PowderN` exists under the same name, with the same shape parameters (`radius`, `yheight` for a cylindrical powder), in both McStas and McXtrace. What differs is what you're allowed to hand it as the material description via its `reflections=` parameter — and that's the main thing these exercises are here to show you, alongside the satisfying business of actually seeing Debye-Scherrer rings appear on a detector.

Keep both instruments deliberately tiny at first: **source → powder sample → flat detector**, nothing else. A monochromatic (or nearly so) beam gives the cleanest rings, since each (h,k,l) reflection then lands at one well-defined angle instead of smearing over a range of radii.

As always: `mcdoc PowderN` / `mxdoc PowderN` before guessing at a parameter, and plot with `mcplot*` / `mxplot-*`. Several exercises below ask you to compare two ring patterns directly — `mcplotdiff`/`mxplotdiff <run1>/rings.dat <run2>/rings.dat` plots the pixel-by-pixel difference between exactly two runs' output (any monitor present in both, 1D or 2D), which is a much more precise way to check "do these rings actually agree" than comparing two plots by eye; `mccoplot`/`mxcoplot` overlays several 1D datasets on one graph, useful for the wavelength/energy scans in Exercises A4/B4. Both tools match files by name across two *different run directories* — they can't compare two differently-named monitors within one run, so every "compare the two ring patterns" instruction below assumes your `PSD_monitor`'s `filename=` stays the same across the two instruments being compared (which it will, if you build the second instrument as a copy of the first with just one thing changed, as instructed). Every exercise below follows the same nine-part structure used throughout the week — **Learning objectives, Physical background, Starting instrument, Task, Expected output, Questions for interpretation, Optional extension, Data-export step, Checkpoint / solution.**

---

## Part A — McStas (neutrons)

### A1 — Baseline: source, sample, detector, rings

**Learning objectives.** Build the smallest instrument that produces a recognisable Debye-Scherrer pattern, and connect the geometry (cone → ring intersection) to what you actually see.

**Physical background.** A powder sample presents every (h,k,l) reflection at every possible crystallite orientation simultaneously, so the scattered intensity for a given reflection forms a full cone around the incident beam direction (fixed opening angle, from Bragg's law) rather than a single spot — a flat detector downstream sees that cone as a ring.

**Starting instrument.** A ready-to-run starting point for this exact instrument is available in [`hints/`](./hints/) (`ex_powderN_mcstas_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

**Task.**
1. Build a minimal instrument: a `Source_simple` with a narrow wavelength band (e.g. `lambda0=2.5, dlambda=0.02`) focused onto a small aperture a few metres away — this is your sample position.
2. At that position, insert a cylindrical `PowderN` sample:
   ```c
   COMPONENT sample = PowderN(radius=0.005, yheight=0.03, reflections="Al.laz")
   AT (0,0,0) RELATIVE PREVIOUS
   ```
3. A short distance downstream, add a small `Beamstop` centred on the direct beam (to stop the huge unscattered peak from swamping everything else), and a large flat `PSD_monitor` at the same distance (e.g. 1×1 m, placed 0.3–0.5 m after the sample) to catch the scattered rays.
4. Run it (`1e6`–`1e7` rays) and plot the `PSD_monitor`.

**Expected output.** One or more concentric rings on the `PSD_monitor`, centred on the beamstop.

**Questions for interpretation.**
- Why rings, and not spots? (Think about what a "powder" physically is compared to the single crystal in a Laue-camera instrument.)
- Each ring is a cross-section of a Debye-Scherrer *cone* — why a cone, geometrically, given that every crystallite in the powder is randomly oriented but the scattering angle for a given (h,k,l) is fixed by Bragg's law?
- What happens to the sharpness of the rings if you widen `dlambda` a lot? Why?
- Try moving the detector further away, or closer. What changes about the ring radii, and why doesn't the *angle* of each ring change?

**Optional extension.** Run at a deliberately low `ncount` (e.g. `1e4`) and compare — does the "ring" survive, or does it dissolve into noise? `mcplotdiff` on the low- and high-`ncount` `rings.dat` files shows the noise directly, as the part of the image that doesn't match. This is the same finite-sampling artefact discussed in the Sources & Monitors sheet, now showing up as broken-looking rings rather than a grainy spot.

**Data-export step.** Log the simulation contract (parameters, seed, `ncount`, monitor settings, output files, software version) for your baseline run — you'll need it for comparison in A2 and A4.

**Checkpoint / solution.** You should have a saved `PSD_monitor` plot showing at least one clean ring, and be able to explain in your own words why a cone, not a spot.

### A2 — Two ways to describe the same material: classic tables vs. NCrystal

**Learning objectives.** See that `PowderN`'s `reflections=` parameter is a pluggable material description, not a fixed file format, and that two independent descriptions of the same physical material should (mostly) agree.

**Physical background.** `PowderN`'s `reflections=` parameter can take more than a plain `.laz`/`.lau` file of pre-computed structure factors — recent McStas versions can also hand the physics off to the NCrystal library for a given material, which brings its own physics for thermal motion, absorption, and incoherent/inelastic backgrounds.

**Starting instrument.** Your A1 instrument.

**Task.**
1. Use `nctool -b` (or browse the [NCrystal material list](https://github.com/mctools/ncrystal/wiki)) to find the built-in NCrystal entry for aluminium (something like `Al_sg225.ncmat`).
2. Check `mcdoc PowderN` carefully for exactly how to point `reflections=` (or a related parameter — check your installed version) at an NCrystal material/cfg-string, and build a second instrument identical to A1 except for that one change.
3. Run both instruments with the same statistics and compare the two `PSD_monitor` ring patterns for what should be the *same* material (aluminium). `mcplotdiff` on the two `rings.dat` files is the direct way to do this — any genuine disagreement between the two physics routes shows up as structure in the difference image, rather than noise.

**Expected output.** Two ring patterns with the same ring positions (angles), for a genuinely comparable material description; intensities may differ somewhat given the two routes' different underlying physics models.

**Questions for interpretation.**
- Do the ring positions (angles) agree between the two routes? Should they?
- NCrystal is a general-purpose neutron cross-section library with its own physics for thermal motion, absorption, and incoherent/inelastic backgrounds — where would you expect the two simulations to disagree, if anywhere, and why?
- `nctool -b` lists a large, curated set of real materials; a `.laz`/`.lau` file has to be generated (or found) separately for each one. What would make you reach for one route over the other on a real project?

**Optional extension.** Repeat the comparison at a coarser detector binning and check whether any small disagreement between the two routes survives — or whether it was only visible at fine binning (tying back to the binning-vs-physical-effect distinction from the Sources & Monitors sheet).

**Data-export step.** Log the simulation contract for both runs, being explicit in `input_parameters` about *which* material description (`.laz` filename vs. NCrystal cfg-string) was used — this single field is the difference between the two runs and is easy to lose track of later.

**Checkpoint / solution.** You should be able to show, via `mcplotdiff`, that the two ring patterns agree within statistics (a difference image that looks like noise, not structure), plus name one physical effect NCrystal captures that a plain `.laz` table does not.

### A3 (optional) — Attach yesterday's optics

**Learning objectives.** Chain Tuesday's guide instrument into Wednesday's sample instrument, and see whether a realistic (non-parallel) beam changes your rings.

**Physical background.** A guide's exit beam has a real divergence distribution (Day 2, Optics exercises) rather than the perfectly parallel pencil beam `Source_simple` approximates; powder diffraction rings are sensitive to divergence because it directly adds angular smearing on top of the Bragg angle.

**Starting instrument.** Your A1/A2 instrument, source component to be replaced.

**Task.** If you built a working guide instrument in yesterday's Optics exercises, replace your `Source_simple` here with that guide's exit (source → guide → *this* sample position), the same way the earlier `templateDIFF`-style instrument in this repo goes source → monochromator → sample → detector.

**Expected output.** Rings that are broadened into bands, in proportion to the guide's exit divergence, compared to the sharp rings from A1.

**Questions for interpretation.** Does the beam divergence coming out of the guide broaden your rings into bands? If so, is that a guide problem or simply more realistic than a perfectly parallel pencil beam?

**Optional extension.** Compare quantitatively: measure the angular width of one ring band and check whether it's consistent with the guide exit's `DivPos_monitor` divergence spread from the Optics exercises. `mcplotdiff` between this exercise's `rings.dat` and A1's baseline `rings.dat` visualises the broadening directly, ring by ring.

**Data-export step.** Log the simulation contract, noting under `source_parameters` that the source is now "guide exit from `<your Optics instrument>`" rather than a bare analytic source — this provenance matters for anyone reusing the dataset later.

**Checkpoint / solution.** You should be able to say whether your rings-to-bands broadening is consistent with the guide's own measured divergence, not just that "the rings got fuzzier".

### A4 (optional) — Multi-dimensional scans: wavelength × material

**Learning objectives.** Build a small, structured two-dimensional dataset (wavelength × material) as a single `mcrun` invocation, using its list-mode, multi-dimensional scan support — and understand the difference between a "locked-step" scan and a full grid ("cartesian product") scan, since both are useful in different situations.

**Physical background.** Current `mcrun` releases support scanning any instrument parameter — numeric *or* string-valued — as an explicit list via `-L`/`--list`. A parameter given as `min:delta:max` (e.g. `lambda0=1.5:0.5:2.5`) is expanded into its own equidistant list of values, and can be freely mixed under `-L` with other, explicitly-listed parameters — including a list of filenames, such as `reflections=Al.laz,Cu.laz,Nb.laz`. By default, multiple `-L` lists are scanned together in lockstep (element 1 of each list together, then element 2, and so on — this requires all lists to have the same length). Adding `-M`/`--multi` instead scans the *cartesian product* of every parameter's list — every wavelength with every material — which is what a real two-dimensional dataset needs, and lets the lists have different lengths. This is exactly the structure behind the per-sample metadata schema in [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md): a batch of runs, one manifest row each — only now `mcrun` itself generates the batch, rather than a hand-written shell loop. (This scan support is a recent addition to `mcrun`/`mxrun` — check `mcrun --help` under "Parameter scan options" to confirm your installed version has `-M`/`-L`; older installations may only support the single-parameter `-N`/`par=min,max` form used in step 1 below.)

**Starting instrument.** The [`hints/`](./hints/) starter `ex_powderN_mcstas_starter.instr` already exposes `reflections` as a string instrument parameter for exactly this exercise. If you built your own A1 instrument by hand instead, promote its hard-coded `reflections="Al.laz"` to a parameter first:
```c
DEFINE INSTRUMENT my_powderN(lambda0=2.5, dlambda=0.02, dist_sample=3, dist_detector=0.4,
                              string reflections="Al.laz")
...
COMPONENT sample = PowderN(radius=0.005, yheight=0.03, reflections=reflections)
AT (0,0,0) RELATIVE sample_pos
```

**Task.**
1. Run the wavelength dimension alone first, to confirm the basic scan mechanism: 
   ```sh
   mcrun ex_powderN_mcstas_starter.instr -N 5 lambda0=1.5,3.5 -n 1e6 -d scan_lambda_Al
   ```
   Confirm you get 5 scan points and that ring radii shift systematically with wavelength — since `rings.dat` is a 2D `PSD_monitor`, `mccoplot` won't overlay it directly, but if you add a 1D `L_monitor`/`Monitor_nD` alongside it, `mccoplot` across the 5 scan points' wavelength files is a quick way to confirm the scan swept the range you expected before looking at any rings at all.
2. Now scan wavelength and material together, as a single-command two-dimensional grid:
   ```sh
   mcrun ex_powderN_mcstas_starter.instr -M -L lambda0=1.5:0.5:2.5 reflections=Al.laz,Cu.laz,Nb.laz -n 1e6 -d scan_grid
   ```
   `-L` expands `lambda0=1.5:0.5:2.5` into its own explicit list of equidistant wavelengths, and takes `reflections=...` as an explicit list of three materials; `-M` then runs the cartesian product of the two lists — every wavelength with every material — all in one command, each combination in its own subdirectory under `scan_grid/`.
3. For comparison, try the same two lists *without* `-M` (drop the flag, and make sure both lists have the same length, e.g. three wavelengths and three materials): this scans them together in lockstep instead — (wavelength 1, material 1), (wavelength 2, material 2), (wavelength 3, material 3) — not the full grid. Compare the number of output subdirectories between the two commands, and make sure you understand why they differ.

**Expected output.** The `-M -L` grid command produces one subdirectory per (material, wavelength) combination — 3 materials × however many wavelength points the `1.5:0.5:2.5` delta produces — each holding one `PSD_monitor` "rings" file; the lockstep command instead produces only as many subdirectories as there are elements in each list.

**Questions for interpretation.**
- How does the ring radius change with wavelength, for the same material? Does it match what Bragg's law predicts?
- How does the ring *pattern* (number of rings, relative radii and intensities) differ between materials at the same wavelength? Is that driven by d-spacings, structure factors, or both?
- If you trained a model on all the grid's images with only "wavelength" as a label — no material label — what would it likely end up confusing wavelength effects with?
- Why would the lockstep (non-`-M`) version of this scan be the wrong tool for building a labelled dataset that needs every material seen at every wavelength?

**Data-export step.** This is the natural home for the full per-sample metadata schema from [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md) — build one manifest row per run (material, wavelength, `ncount`, seed, output path) from the scan's own output directory structure, rather than eyeballing each plot by hand. The worked example in that document is drawn directly from this exercise.

**Checkpoint / solution.** You should have one `scan_grid/` output tree with a subdirectory per (material, wavelength) combination, and be able to explain, in your own words, the difference between the lockstep and `-M` (cartesian/grid) scan modes, and why a labelled dataset needs the latter.

**Optional extension.** Re-perform the scan, but recompile to include `NeXus`/`HDF5` suppor (add `-c --format=NeXus and -d NeXus_scan_grid` to your previous command). Inspect the generated `mccode.h5` file using `nexpy` or `silx` that have both been included in your PaNRAID enviroment.

---

## Part B — McXtrace (X-rays)

### B1 — Baseline: source, sample, detector, rings

**Learning objectives.** Build the smallest instrument that produces a recognisable Debye-Scherrer pattern for X-rays, using the CIF-driven route that is the standard McXtrace `PowderN` entry point.

**Physical background.** Identical geometric argument to A1 — a powder's random crystallite orientations turn each (h,k,l) reflection into a cone, seen as a ring on a flat detector — but here the material is described crystallographically via CIF rather than a pre-tabulated neutron structure-factor file.

**Starting instrument.** A ready-to-run starting point for this exact instrument is available in [`hints/`](./hints/) (`ex_powderN_mcxtrace_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

**Task.**
1. Build a minimal instrument: a near-monochromatic `Source_flat` (or `Source_gaussian`), e.g. around 10 keV with a narrow `dE`/`dlambda`, focused onto a small aperture a few metres away — your sample position.
2. At that position, insert a cylindrical `PowderN` sample using a CIF-described material — LaB₆ is the standard McXtrace `PowderN` test case:
   ```c
   COMPONENT sample = PowderN(radius=0.5e-4, yheight=1e-3, reflections="LaB6.cif")
   AT (0,0,0) RELATIVE PREVIOUS
   ```
   The first time this runs, McXtrace calls `cif2hkl` transparently to turn the CIF into structure factors — you don't have to run that step yourself.
3. As in Part A, add a small `Beamstop` plus a large flat `PSD_monitor` some distance downstream.
4. Run it and plot the rings.

**Expected output.** One or more concentric rings on the `PSD_monitor`, as in A1.

**Questions for interpretation.** Same as A1: why rings not spots, why a cone, what a wider energy band does to ring sharpness, what changing the detector distance does to the ring radii.

**Optional extension.** As A1's optional extension: try a deliberately low `ncount` and see the rings degrade into noise.

**Data-export step.** Log the simulation contract for this baseline run.

**Checkpoint / solution.** You should have a saved `PSD_monitor` plot showing at least one clean ring, and be able to explain the cone/ring geometry in your own words.

### B2 — Two ways to describe the same material: CIF vs. pre-computed tables

**Learning objectives.** See the second axis of `PowderN`'s pluggable material description — a full crystallographic file converted on the fly, vs. a pre-computed structure-factor table — and the practical trade-off between them.

**Physical background.** For `PowderN` in McXtrace, `reflections=` accepts either a CIF file — a full crystallographic description, converted on the fly — or a pre-computed `.lau`/`.laz`/`.hkl` list of structure factors, which skips that conversion step.

**Starting instrument.** Your B1 instrument.

**Task.**
1. Generate a pre-computed file for the *same* LaB₆ structure, e.g. with `cif2hkl --powder --mode NUC -o LaB6.laz <your LaB6 CIF>` (you can get a LaB₆ CIF from the Crystallography Open Database, or reuse whichever CIF `cif2hkl` produced/consumed in step B1).
2. Build a second instrument identical to B1, except `reflections="LaB6.laz"` instead of `reflections="LaB6.cif"`.
3. Compare the two ring patterns with `mxplotdiff` on the two `rings.dat` files, and compare how long each simulation took to start up.

**Expected output.** Matching ring positions and (within statistics) intensities between the two routes; a measurable difference in simulation start-up time (CIF conversion vs. reading a pre-computed table).

**Questions for interpretation.**
- Do the two routes agree on ring positions and intensities? Should they, given they describe the same crystal structure?
- What's the practical trade-off between handing `PowderN` a CIF directly versus pre-computing a `.laz`/`.lau` file once and reusing it?
- If you wanted to publish or share your instrument file for others to reproduce exactly, which route makes that easier?

**Optional extension.** Time both routes at a much higher `ncount` and check whether the CIF-conversion overhead becomes negligible relative to the simulation itself, or stays a fixed, noticeable cost regardless of statistics.

**Data-export step.** Log the simulation contract for both runs, recording under `simulation_settings` (or a notes field) which one required the on-the-fly `cif2hkl` step — that's a reproducibility-relevant fact (a missing `cif2hkl` install would silently break the CIF route on someone else's machine).

**Checkpoint / solution.** You should be able to state, from your own timing, which route is faster to *set up* once vs. faster to *run* repeatedly.

### B3 (optional) — Attach yesterday's optics

**Learning objectives.** Chain Tuesday's monochromator instrument into Wednesday's sample instrument, and check that the fixed energy from the monochromator is compatible with your detector geometry.

**Physical background.** A double-crystal (or multilayer) monochromator fixes a specific, narrow energy band (Day 2, Optics exercises); a `PowderN` sample's ring radii depend on that energy through Bragg's law, so the detector distance chosen for a broadband B1 baseline may no longer show the rings at a convenient radius.

**Starting instrument.** Your B1/B2 instrument, source component to be replaced.

**Task.** If you built a working double-crystal (or multilayer) monochromator instrument in yesterday's Optics exercises, replace your `Source_flat`/`Source_gaussian` here with that monochromator's exit beam. Since your monochromator instrument already fixes a specific energy via Bragg's law, make sure your `PowderN` sample's rings land somewhere sensible for that energy — you may need to adjust the detector distance to see them comfortably.

**Expected output.** Rings at radii consistent with your monochromator's fixed energy via Bragg's law — likely requiring a different `dist_detector` than B1's default.

**Questions for interpretation.** Did you need to change the detector distance to see the rings comfortably? Does the required change match what Bragg's law predicts for your monochromator's energy compared to B1's broadband case?

**Optional extension.** Scan the monochromator's `A1` (from the Optics exercises) and watch the `PowderN` ring radii track the resulting energy change in real time — a direct link between Tuesday's rocking curve and Wednesday's rings.

**Data-export step.** Log the simulation contract, recording the monochromator's fixed energy/`A1` value under `source_parameters` even though it comes from a different instrument file.

**Checkpoint / solution.** You should be able to state the energy your monochromator delivers and show that your ring radii are consistent with that energy via Bragg's law.

### B4 (optional) — Multi-dimensional scans: energy × material

**Learning objectives.** Build the same kind of structured two-dimensional dataset as A4, for X-rays: energy × material, as a single `mxrun` grid-scan invocation.

**Physical background.** As in A4: `mxrun` shares the same extended scan support — `-L`/`--list` for explicit (numeric or string) value lists, with a `min:delta:max` range expanded automatically, and `-M`/`--multi` to take the cartesian product across every scanned parameter rather than a locked-step scan. Energy and material become the two axes of one grid, generated in one command rather than a shell loop. (As in A4: confirm your installed `mxrun` has `-M`/`-L` via `mxrun --help` — this is a comparatively recent addition.)

**Starting instrument.** The [`hints/`](./hints/) starter `ex_powderN_mcxtrace_starter.instr` already exposes `reflections` as a string instrument parameter for this exercise.

**Task.**
1. Run the energy dimension alone first:
   ```sh
   mxrun ex_powderN_mcxtrace_starter.instr -N 5 E0=8,15 -n 1e6 -d scan_energy_LaB6
   ```
2. Now scan energy and material together as a single-command grid, e.g. over `LaB6.cif` and a second CIF/`.laz` file of your choice (Si is a common second choice — check the McXtrace example suite for a bundled Si powder file):
   ```sh
   mxrun ex_powderN_mcxtrace_starter.instr -M -L E0=8:3.5:15 reflections=LaB6.cif,Si.laz -n 1e6 -d scan_grid
   ```
   `-L` expands `E0=8:3.5:15` into an explicit list of energies and takes `reflections=...` as an explicit two-material list; `-M` runs their cartesian product in one command.
3. As in A4, try dropping `-M` (with matching list lengths) to see the lockstep scan instead, and confirm it produces far fewer runs than the grid.

**Expected output.** One `scan_grid/` output tree with one subdirectory per (material, energy) combination — 2 materials × however many energy points the `8:3.5:15` delta produces — each holding one `PSD_monitor` "rings" file.

**Questions for interpretation.**
- How does ring radius change with energy for the same material, and does that match Bragg's law's inverse relationship between energy and wavelength?
- How does the ring pattern differ between the two materials at the same energy?
- Which one dimension of this grid would you expect a well-trained model to use to predict *material identity*, and which to predict *beam energy* — and could a model confuse the two if the dataset were built carelessly (e.g. always pairing one material with only one energy)?

**Optional extension.** Deliberately build a *confounded* version of this dataset — pair material A only with low energies and material B only with high energies (this is easiest to do by constructing two separate, non-`-M` lockstep scans rather than one grid) — and discuss (without necessarily training anything) why a model trained on it could appear to "identify material" while actually just detecting energy. This is the shortcut-learning risk flagged in [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md).

**Data-export step.** Build the manifest exactly as in A4, one row per run, using the metadata schema in [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md).

**Checkpoint / solution.** You should have one `scan_grid/` output tree spanning every (material, energy) combination, and be able to explain in your own words why deliberately *crossing* material and energy (the `-M` grid) rather than confounding them (two separate lockstep scans) is necessary for a resulting dataset to teach a model the right thing.

**Optional extension.** Re-perform the scan, but recompile to include `NeXus`/`HDF5` suppor (add `-c --format=NeXus and -d NeXus_scan_grid` to your previous command). Inspect the generated `mccode.h5` file using `nexpy` or `silx` that have both been included in your PaNRAID enviroment.

---

*(Facilitator notes for this session are collected separately in [`Facilitator_Notes.md`](./Facilitator_Notes.md), not shown here.)*
