# Sources & Monitors — Hands-on Exercises

*McStas (neutrons) & McXtrace (X-rays) — PaNRAID School, Day 2 morning*

These exercises follow directly on from the `McStas_McXtrace_Sources_and_Monitors.pptx` lecture. They are written for absolute beginners to the two codes: no prior `.instr`-file experience is assumed, only that McStas and/or McXtrace are installed and that participants have seen the lecture slides once.

Every exercise is given in parallel for both codes. The instrument logic, parameter names and monitor syntax are close to identical — only component names, typical wavelength/energy scales and a few facility-specific components differ. Participants working in only one code can simply skip the other column; participants with time to spare are encouraged to do both and compare.

Every exercise below follows the same nine-part structure, so once you've done one you know exactly what to expect from the next: **Learning objectives, Physical background, Starting instrument, Task, Expected output, Questions for interpretation, Optional extension, Data-export step, Checkpoint / solution.** A short exercise skips a part with a one-line "n/a" rather than omitting it, so the structure stays predictable throughout the week.

## How to use this sheet

- Work in a fresh folder, e.g. `ex_sources_monitors/`, one `.instr` file per exercise (or one file you keep editing — your choice).
- Compile and run from the command line with `mcrun <file>.instr <params> -n 1e6` (McStas) or `mxrun <file>.instr <params> -n 1e6` (McXtrace), or use `mcgui` / `mxgui` if you prefer a graphical front-end.
- Plot results with `mcplot` / `mcplot-pyqtgraph` / `mcplot-matplotlib` (McStas) or the equivalent `mxplot-*` (McXtrace).
- Look up any component's parameters at any time with `mcdoc <Component>` / `mxdoc <Component>`, or the full manual via `mcdoc -c` / `mxdoc -c`.

A quick name-mapping you'll use throughout:

| Concept | McStas (neutrons) | McXtrace (X-rays) |
|---|---|---|
| Doc tool | `mcdoc` | `mxdoc` |
| Run tool | `mcrun` | `mxrun` |
| GUI | `mcgui` | `mxgui` |
| Plot tool | `mcplot*` | `mxplot-*` |
| Minimal analytic source | `Source_simple` | `Source_flat` |
| Ray state | `x,y,z, vx,vy,vz, t, sx,sy,sz, p` | `x,y,z, kx,ky,kz, Ex,Ey,Ez, phi, t, p` |
| Coupling format | `MCPL_output` / `MCPL_input` (both codes, identical) | |

---

## Recording a simulation contract

Every exercise from here on ends with a short **Data-export step**. Before moving on to the next exercise, write down — in a plain-text file, a lab notebook, or a comment block at the top of your `.instr` file — six facts about the run you just did:

1. **Instrument parameters** — the full set of values you actually ran with, written as `name=value`, not "defaults".
2. **Random seed** — did you set one explicitly with `--seed=<N>` (or the equivalent `mxrun` flag), or leave it to vary from run to run? Either is a legitimate choice; not knowing which you did is not.
3. **Number of rays (`ncount`)** — your `-n`/`--ncount` value. This governs Monte Carlo statistics, not the physical source strength (Exercise 4 is entirely about this distinction).
4. **Monitor settings** — binning, limits, and any `options=` string for every monitor in the instrument.
5. **Output files** — where the run's `.dat`/`.h5` files ended up (`mcrun`'s/`mxrun`'s default `<instr>_<date>/` folder, or your own `-d <dir>`).
6. **Software version** — `mcstas --version` / `mcxtrace --version` (or the banner `mcrun`/`mxrun` prints when a run starts).

This is called a **simulation contract**: the minimum information needed for someone else — or you, in three weeks — to reproduce the run, or at least correctly interpret its output. None of it needs a special tool this week; a short text file next to your output is enough. The reason to build the habit now is that these six facts are exactly what a later, automated dataset-generation pipeline needs to fill in for every run — see [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md) for how this scales from "one run's contract" to "one field in every dataset record".

---

## Exercise 1 — Warm-up: finding your way around the docs

**Learning objectives.** Get comfortable pulling up component documentation before you need it in anger, and learn to distinguish required from optional parameters by reading, not guessing.

**Physical background.** n/a — this exercise is about tooling, not physics.

**Starting instrument.** None — no `.instr` file needed yet.

**Task.**
1. Open a terminal and run `mcdoc` (McStas) and/or `mxdoc` (McXtrace) with no arguments. Confirm the components overview page opens.
2. Look up the source you'll use in Exercise 2: `mcdoc Source_simple` / `mxdoc Source_flat`. Identify, in the parameter list, which parameters are required (no default) vs. optional.
3. Look up `mcdoc PSD_monitor` / `mxdoc PSD_monitor` and `mcdoc L_monitor` / `mxdoc L_monitor` the same way.
4. Generate the full PDF component manual with `mcdoc -c` / `mxdoc -c` and confirm it opens — this is your reference for the rest of the week.

**Expected output.** No simulation output — success here means the docs open and you can name a required and an optional parameter for each component above.

**Questions for interpretation.**
- Which parameters does `Source_simple`/`Source_flat` require you to set explicitly, and which have sensible defaults?
- What unit is `dist` given in? What about `focus_xw`?
- Why might the version of the manual installed on your laptop differ slightly from the one on mcstas.org / mcxtrace.org?

**Optional extension.** Skim the parameter list of one component you *won't* use this week (e.g. `Guide_channeled` or `Multilayer_elliptic`) purely to see how much variety exists — you'll want to know this shelf exists later in the week even if you don't reach for it today.

**Data-export step.** n/a — no run to log yet.

**Checkpoint / solution.** You should be able to open both a single component's page and the full manual on demand, and explain in one sentence what "required" vs. "optional" means for an instrument parameter.

---

## Exercise 2 — Your first beamline: a source and two monitors

**Learning objectives.** Build, compile and run a complete (if minimal) instrument, and read its output correctly — including telling apart the three numbers every monitor reports.

**Physical background.** A minimal beamline is source → free flight → monitor. `Source_simple`/`Source_flat` emit rays with a position, direction and wavelength/energy drawn from the parameters you set; `PSD_monitor` and `L_monitor` histogram, respectively, the ray positions and wavelengths that cross their surface.

**Starting instrument.** A ready-to-run starting point for this exact instrument is available in [`hints/`](./hints/) (`ex2_mcstas_starter.instr` / `ex2_mcxtrace_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

**Task.** Below is the same three-component beamline in both codes — a progress bar, a source, and two monitors 5 m downstream. Type it in (or copy it), save it, and run it with `mcrun ex2_mcstas.instr -n 1e6` / `mxrun ex2_mcxtrace.instr -n 1e6`.

**McStas** — `ex2_mcstas.instr`
```c
DEFINE INSTRUMENT ex2_mcstas()

TRACE

COMPONENT origin = Progress_bar()
AT (0,0,0) ABSOLUTE

COMPONENT src = Source_simple(radius=0.05, lambda0=2.5, dlambda=1.5,
                               focus_xw=0.1, focus_yh=0.1, dist=5)
AT (0,0,0) RELATIVE origin

COMPONENT psd = PSD_monitor(xwidth=0.2, yheight=0.2, filename="psd.dat")
AT (0,0,5) RELATIVE src

COMPONENT lm = L_monitor(xwidth=0.2, yheight=0.2, filename="lm.dat", Lmin=0, Lmax=8)
AT (0,0,5.01) RELATIVE src

END
```

**McXtrace** — `ex2_mcxtrace.instr`
```c
DEFINE INSTRUMENT ex2_mcxtrace()

TRACE

COMPONENT origin = Progress_bar()
AT (0,0,0) ABSOLUTE

COMPONENT src = Source_flat(radius=0.05, lambda0=2.5, dlambda=1.5,
                             focus_xw=0.1, focus_yh=0.1, dist=5)
AT (0,0,0) RELATIVE origin

COMPONENT psd = PSD_monitor(xwidth=0.2, yheight=0.2, filename="psd.dat")
AT (0,0,5) RELATIVE src

COMPONENT lm = L_monitor(xwidth=0.2, yheight=0.2, filename="lm.dat", Lmin=0, Lmax=8)
AT (0,0,5.01) RELATIVE src

END
```

**Expected output.** `psd.dat` shows a filled disc or square (depending on which focusing/aperture shape you gave) roughly matching your `focus_xw`/`focus_yh`. `lm.dat` shows a flat-topped histogram between `lambda0-dlambda` and `lambda0+dlambda`.

**Questions for interpretation.**
- What shape and size is the illuminated spot in `psd.dat`? Does it match a parameter you set on the source?
- What shape is the `lm.dat` histogram? Why that shape, given how `lambda0`/`dlambda` are used to draw a wavelength for each ray?
- Every monitor output reports three numbers per bin (and a total): intensity, error, and event count. Which of these three actually counts *rays*, and which are computed from ray *weight*?
- The only line that differs between the two files is the source component name (`Source_simple` vs `Source_flat`). Everything else — parameter names, units, monitor syntax — is identical. Why do you think the two projects chose to keep it that way?

**Optional extension.** Add a second `PSD_monitor` immediately after the source (`AT (0,0,0.01) RELATIVE src`) and compare it to the one 5 m downstream — this is your first look at how a beam's footprint depends on distance, which Exercise 3 explores properly.

**Data-export step.** Write your six-fact simulation contract for this run (see "Recording a simulation contract" above): instrument parameters, seed, `ncount`, monitor settings, output files, software version.

**Checkpoint / solution.** You should have a compiling, running instrument and be able to say, without looking it up again, which of intensity/error/event-count is the raw ray tally and which two are derived from ray weight.

---

## Exercise 3 — Shaping the source: position, direction, spectrum

**Learning objectives.** Connect each source parameter to a visible effect on your monitors, and separate "where/which way" (geometry) from "what spectrum" (energy/wavelength content) — two effect categories you'll need to tell apart all week.

**Physical background.** A source's spatial extent (`radius`), its focusing target (`focus_xw`/`focus_yh`, `dist`) and its spectral content (`lambda0`/`dlambda`) are independent knobs: a bigger source with the same focusing target produces the same footprint downstream but a *different* angular (divergence) spread, because every point on the source is still aimed at the same target.

**Starting instrument.** Your Exercise 2 instrument.

**Task.** Make each of the following changes **one at a time**, re-running and re-plotting between changes:
1. Double `focus_xw` and `focus_yh` (e.g. to 0.2/0.2). What changes on the PSD monitor?
2. Put `focus_xw`/`focus_yh` back, and instead double `radius` (source size) to 0.1. What changes on the PSD monitor this time — and what *doesn't* change, even though you made the source bigger?
3. Move the monitors twice as far away (`dist=10`, and move both monitor `AT` positions to `10` and `10.01`), keeping `focus_xw`/`focus_yh` fixed. Add a `Divergence_monitor` (same name in both codes) just before the PSD monitor. How does the divergence distribution change compared to the `dist=5` case?
4. Reset the geometry, and instead vary the spectrum: try `lambda0=1.0, dlambda=0.5` and then `lambda0=5.0, dlambda=0.5`. Confirm the `lm.dat` histogram tracks the change.

**Expected output.** Steps 1 and 3 change the PSD footprint size and the divergence spread respectively; step 2 changes neither footprint size nor divergence noticeably; step 4 shifts the `lm.dat` histogram's centre and width but leaves the PSD monitor unchanged.

**Questions for interpretation.**
- Why does changing `radius` barely change the illuminated area on the PSD monitor, even though it clearly changes where rays start?
- What *does* control the size of the illuminated spot at a given distance?
- If you doubled the distance but kept the focus target the same physical size, did the beam get more or less divergent? Does that match the geometry in the "anatomy of a simple source" picture from the lecture?
- Of the four changes you just made, which were **geometrical** effects (footprint, divergence) and which were **spectral** effects (wavelength content)? Could you tell the two apart from a PSD monitor alone, or would you need the `L_monitor`/`Divergence_monitor` too?

**Optional extension.** Set `focus_xw`/`focus_yh` to something *smaller* than the source `radius` and see whether the PSD footprint shrinks below the source size — is there a limit to how tightly a simple analytic source can be focused, and does the answer depend on distance?

**Data-export step.** Log the simulation contract for whichever of the four sub-runs you consider most informative — at minimum, the parameter that changed and the resulting monitor files.

**Checkpoint / solution.** You should be able to predict, before running, whether changing a given source parameter will move the PSD footprint, the divergence, the wavelength histogram, or none of the three.

---

## Exercise 4 — Statistics and normalisation: what actually changed?

**Learning objectives.** Learn to tell apart four distinct reasons a monitor output can look different from a previous run: a genuine **physical parameter change**, **Monte Carlo noise** (too few rays), a **monitor binning** choice, or a **normalisation convention** — the single most important interpretive skill for anyone who will later feed this kind of data to an AI model, since a model cannot tell these apart on its own either.

**Physical background.** McStas/McXtrace are weighted Monte Carlo codes: each simulated ray carries a statistical weight `p`, and a monitor's reported intensity `I` is the weight-sum of the rays that crossed it, not a raw count. The error `E` is the Monte Carlo statistical uncertainty on `I`, and — for a fixed instrument — shrinks roughly as `1/sqrt(N)` as the number of simulated rays `N` (`ncount`) grows; it says nothing about the physical source strength, which is fixed by the instrument's parameters. Separately, a monitor's *binning* (e.g. `nx`/`ny`, or an `options="... bins=N"` string) trades resolution for per-bin statistics: coarser bins average over more rays per bin (lower apparent noise, less detail), finer bins do the opposite, for the *same* underlying physics and the *same* `ncount`. Separately again, a monitor's *normalisation* — intensity "as simulated", "per cm²", per unit solid angle, per unit time, or per incident intensity — rescales or reshapes the reported numbers by a convention you chose, not by anything physical changing in the beam.

**Starting instrument.** Your Exercise 2 instrument.

**Task.** Run four single-variable comparisons, changing only the one thing named each time:
1. **Isolate Monte Carlo noise.** Run with `-n 1e3`, then `-n 1e5`, then `-n 1e7`, changing nothing else. Note `I`, `E` and event count `N` for `psd.dat` each time (McStas/McXtrace prints this at the end of the run; it's also in the `.dat` file header).
2. **Isolate binning.** Fix `ncount` at `1e6`. Run once with your monitor's default binning, then again with a much coarser one (e.g. add `nx=10, ny=10` to `PSD_monitor`, or a much finer one, e.g. `nx=400, ny=400`).
3. **Isolate a physical change.** Fix `ncount` and binning. Change `focus_xw`/`focus_yh` as in Exercise 3, step 1.
4. **Isolate a normalisation choice.** Fix everything else. Replace your `PSD_monitor` with a `Monitor_nD` using `options="x y"`, then rerun with `options="x y, per cm2"` (see also Exercise 5). Compare the reported total intensity between the two — same rays, same physics, different convention.
5. Add `EXTEND %{ t = 10e-3*rand01(); %}` (McStas) / the equivalent line (McXtrace) after your source component to force a 1 ms pulse, and add a `TOF_monitor` after the PSD monitor. Does pulsing the source change the *intensity* reported by the PSD monitor?

**Expected output.** A short table you fill in yourself, one row per sub-task, with columns for what you changed, whether `I` changed, whether `E` changed, and whether the *shape* (not just the scale) of the output changed. Case 1 changes `E` a lot and `I` only within statistics; case 2 changes apparent smoothness but not the total `I`; case 3 changes the footprint shape/size genuinely; case 4 changes the reported number without changing anything about the simulated rays.

**Questions for interpretation.**
- Does the total intensity `I` change meaningfully between the three `ncount` values in step 1? Should it? Does `E` scale roughly like `1/sqrt(N)`?
- If you wanted a *higher-flux* virtual source, would raising `ncount` help? What would you change instead?
- In step 2, did the underlying physics change between the coarse- and fine-binned runs? What did change, and how would you notice it from the numbers alone (without looking at a plot)?
- In step 4, if someone handed you the two `Monitor_nD` outputs without telling you about the `per cm2` option, could you tell whether the beam intensity had physically changed, or only the reporting convention? What extra piece of metadata would let you tell?
- Does pulsing the source in step 5 change the *total* PSD intensity? Why or why not?

**Optional extension.** Deliberately under-sample: run the Exercise 2 instrument at `-n 1e2` and look at the PSD monitor. The "texture" you see is now dominated by Monte Carlo noise rather than physics — keep this image in mind for Day 3's Debye-Scherrer rings, which need enough `ncount` to look like real rings rather than noise.

**Data-export step.** For each of the five sub-runs, log the simulation contract — `ncount` and monitor `options=`/binning matter most here, since they're exactly the two things this exercise is about.

**Checkpoint / solution.** Given two monitor plots that look different, you should be able to list the four possible causes (physical change, MC noise, binning, normalisation) and name at least one piece of metadata that would let you distinguish between each pair of them. This is the core skill this exercise sheet is building toward: a model trained on data that mixes these causes without recording which is which can just as easily learn the mixing artefact as the physics (see [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md) on data leakage).

---

## Exercise 5 — The swiss-army knife: `Monitor_nD`

**Learning objectives.** Reproduce the results of Exercise 2 using a single, more general monitor type, then push it further than `PSD_monitor`/`L_monitor` can go — and connect its normalisation options back to Exercise 4.

**Physical background.** `Monitor_nD` exists under the same name, with the same `options=` grammar, in both codes; `PSD_monitor` and `L_monitor` are themselves thin, convenience-named wrappers around specific `Monitor_nD` configurations.

**Starting instrument.** Your Exercise 2 instrument.

**Task.**
1. Replace your `psd` component with:
   ```c
   COMPONENT psd_nd = Monitor_nD(xwidth=0.2, yheight=0.2, options="x y")
   AT (0,0,5) RELATIVE src
   ```
   Confirm it reproduces the same picture as your original `PSD_monitor`.
2. Replace your `lm` component similarly, using `options="lambda limits=[0 8] bins=100"`. Confirm it reproduces the same histogram as `L_monitor`.
3. Add a third `Monitor_nD` with `options="x y, per cm2"` and compare — this is the normalisation case from Exercise 4, step 4.
4. Stretch: try `options="banana, theta limits=[-20 20], bins=80"` on a monitor placed with `radius=5` and see how a curved ("banana") monitor differs from a flat one.

**Expected output.** Steps 1–2 reproduce Exercise 2's plots exactly (within statistics); step 3 reproduces the same *shape* but a rescaled intensity; step 4 produces an angle-binned histogram rather than a position map.

**Questions for interpretation.**
- What did you have to change to get `Monitor_nD` to reproduce `PSD_monitor` and `L_monitor` exactly? What does that tell you about what those "simple" monitors are, under the hood?
- Look up `mcdoc monitor` / `mxdoc monitor` — how many monitor components are listed, and how many of them could in principle be replaced by a suitably configured `Monitor_nD`?
- Why might "per cm2" be a more useful unit than raw intensity when comparing monitors of different sizes, or comparing your simulation to a real detector's published sensitivity?

**Optional extension.** Combine two variables in one `options=` string, e.g. `"x y, lambda limits=[0 8] bins=20"`, to get a position-resolved wavelength histogram in a single monitor — the beginning of the multi-dimensional monitor outputs you'll see again in Day 3.

**Data-export step.** Log the simulation contract, with particular attention to the exact `options=` string used — this is the one part of the "monitor settings" fact that's easy to transcribe wrong.

**Checkpoint / solution.** You should be able to write a `Monitor_nD` `options=` string from scratch that reproduces a given `PSD_monitor`/`L_monitor` configuration, and state which one convenience monitor you'd reach for instead of `Monitor_nD` in ordinary use (readability), and when you'd reach for `Monitor_nD` instead (anything a named monitor can't express).

---

## Exercise 6 (stretch) — Two source landscapes

**Learning objectives.** Swap your simple analytic source for a facility-realistic one, and see how the two codes diverge here specifically — because real neutron and X-ray sources are parameterised very differently.

**Physical background.** McStas's `Source_gen` models a continuous (reactor-like) moderator spectrum as a sum of Maxwellian components; McXtrace's `Bending_magnet` models a synchrotron bending-magnet source from accelerator parameters (energy, current, field). Neither has a close analogue in the other code, which is itself the point of this exercise.

**Starting instrument.** Your Exercise 2 instrument, source component to be replaced.

**Task.**
- **McStas:** replace `Source_simple` with `Source_gen`, using a three-component Maxwellian continuous-source spectrum (values below are a real ILL-style set, taken from the `templateDIFF` example instrument elsewhere in this repository):
  ```c
  COMPONENT src = Source_gen(radius=0.11, dist=5, focus_xw=0.1, focus_yh=0.1,
      lambda0=2.5, dlambda=1.5,
      T1=229.6, I1=5.32e13, T2=1102, I2=4.37e12, T3=437.1, I3=3.84e13)
  AT (0,0,0) RELATIVE origin
  ```
- **McXtrace:** rather than a ready-made snippet, use the doc-reading skill from Exercise 1: run `mxdoc Bending_magnet` and identify the parameters you'd need to set to model a synchrotron bending-magnet source (accelerator energy, current, magnetic field, and the energy/wavelength range of interest). Build a minimal instrument around it.

**Expected output.** McStas: the `L_monitor`/`Monitor_nD` wavelength spectrum now shows the characteristic Maxwellian shape rather than a flat top. McXtrace: a continuous, strongly energy-dependent spectrum shaped by the accelerator parameters rather than a flat band.

**Questions for interpretation.**
- Which source family did you use for McStas (reactor/continuous, pulsed, or particle-list), and why does that match "Maxwellian" better than a pulsed spallation source component would?
- For McXtrace, what physical parameters does `Bending_magnet` need that `Source_flat` didn't? Why do you think X-ray sources are parameterised in terms of the accelerator, while (continuous) neutron sources are parameterised in terms of a moderator temperature?

**Optional extension.** Compare the flat-spectrum Exercise 2 source and this exercise's realistic source side by side on the same wavelength axis — how much would a downstream analysis be misled by assuming a flat spectrum when the real source is Maxwellian (or vice versa)?

**Data-export step.** Log the simulation contract, including the full Maxwellian/bending-magnet parameter set — these are exactly the "source_parameters" field of the metadata schema in [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md).

**Checkpoint / solution.** You should be able to name, for your code, which real facility-type source family you used and one physical reason its parameterisation looks the way it does.

---

## Exercise 7 (stretch) — Coupling instruments with MCPL

**Learning objectives.** Decouple your source from your monitors into two separate instruments, connected only by a particle-list file — the same mechanism used to couple McStas and McXtrace to each other or to codes like MCNP/Geant4.

**Physical background.** `MCPL_output`/`MCPL_input` write and read a standardised, code-agnostic list of rays (position, direction, energy/wavelength, weight, and more). Once written, the file no longer "knows" which source produced it.

**Starting instrument.** Your Exercise 2 source (McStas or McXtrace).

**Task.**
- **Step A — write the rays out.** In place of your monitors, add:
  ```c
  COMPONENT vout = MCPL_output(filename="beam.mcpl", doubleprec=1, polarisationuse=1)
  AT (0,0,5) RELATIVE src
  ```
  Run it once to produce `beam.mcpl` (or `beam.mcpl.gz`).
- **Step B — read the rays back in.** Build a *second*, separate instrument containing only:
  ```c
  COMPONENT origin = Progress_bar() AT (0,0,0) ABSOLUTE

  COMPONENT vin = MCPL_input(filename="beam.mcpl", polarisationuse=1)
  AT (0,0,0) RELATIVE origin

  COMPONENT psd = PSD_monitor(xwidth=0.2, yheight=0.2, filename="psd.dat")
  AT (0,0,0.01) RELATIVE vin

  COMPONENT lm = L_monitor(xwidth=0.2, yheight=0.2, filename="lm.dat", Lmin=0, Lmax=8)
  AT (0,0,0.02) RELATIVE vin
  ```
  Run instrument B and compare its monitor output to the monitors you had directly after the source in Exercise 2.

**Expected output.** Instrument B's monitors should agree with Exercise 2's, within Monte Carlo statistics.

**Questions for interpretation.**
- Do the two monitor outputs agree (within statistics)? Should they?
- What happens if you set `ncount` on instrument B higher than the number of rays actually stored in `beam.mcpl`?
- Instrument B never mentions `Source_simple`/`Source_flat`/`Source_gen` at all — what does that tell you about what MCPL is actually storing?
- (If you have both codes installed) try writing the MCPL file from the McStas instrument and reading it into the McXtrace instrument, or vice versa. What would need to be true of the ray's physical meaning for this to make sense?

**Optional extension.** Treat `beam.mcpl` itself as a dataset artefact: it has its own implicit "simulation contract" (which instrument and parameters produced it, at what `ncount`). Write that down alongside the file — an MCPL file with no record of its origin is exactly the kind of untraceable intermediate the metadata schema in [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md) is meant to prevent.

**Data-export step.** Log two simulation contracts — one for instrument A (the writer) and one for instrument B (the reader) — and record which MCPL file connects them.

**Checkpoint / solution.** You should be able to explain, in one sentence, why an MCPL file can be read into an instrument that never defines a source component.

---

*(Facilitator notes for this session are collected separately in [`Facilitator_Notes.md`](./Facilitator_Notes.md), not shown here.)*
