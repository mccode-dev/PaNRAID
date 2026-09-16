# Sources & Monitors — Hands-on Exercises

*McStas (neutrons) & McXtrace (X-rays) — PaNRAID School, Day 2 morning*

**Time note.** Sources & Monitors and Optics now share a single Tuesday-morning session instead of a full morning each, so this sheet has been trimmed to three core exercises plus optional "if time allows" material. Because of that, it deliberately does **not** use the nine-part exercise template (Learning objectives / Physical background / Starting instrument / Task / Expected output / Questions for interpretation / Optional extension / Data-export step / Checkpoint) used elsewhere in the school this week — each exercise here is just **Goal / Task / Checkpoints**, with occasional short "If time allows" notes. If a future run of the school restores a dedicated block for this topic, the fuller template (and the material trimmed out below) is easy to reinstate.

These exercises follow directly on from the `McStas_McXtrace_Sources_and_Monitors.pptx` lecture and are written for absolute beginners: no prior `.instr`-file experience is assumed, only that McStas and/or McXtrace are installed and the lecture has been seen once.

Every exercise is given in parallel for both codes. Instrument logic, parameter names and monitor syntax are close to identical — only component names, typical wavelength/energy scales and a few facility-specific components differ. Working in only one code is fine; skip the other column.

## How to use this sheet

- Work in a fresh folder, one `.instr` file per exercise (or one file you keep editing — your choice).
- Compile and run with `mcrun <file>.instr <params> -n 1e6` (McStas) or `mxrun <file>.instr <params> -n 1e6` (McXtrace), or use `mcgui`/`mxgui` for a graphical front-end.
- Plot with `mcplot`/`mcplot-pyqtgraph`/`mcplot-matplotlib` (McStas) or `mxplot-*` (McXtrace). To co-plot or diff two runs, `mccoplot`/`mxcoplot` overlays several 1D datasets and `mcplotdiff`/`mxplotdiff` shows the difference between two — but both tools compare **identically-named files across two different run directories**; they can't diff two differently-named monitors from a single run. Where an exercise below wants a comparison, it gives the two monitors you'd diff the same filename so this works.
- Look up any component's parameters with `mcdoc <Component>`/`mxdoc <Component>`, or the full manual via `mcdoc -c`/`mxdoc -c`.

A quick name-mapping you'll use throughout:

| Concept | McStas (neutrons) | McXtrace (X-rays) |
|---|---|---|
| Doc tool | `mcdoc` | `mxdoc` |
| Run tool | `mcrun` | `mxrun` |
| GUI | `mcgui` | `mxgui` |
| Plot tool | `mcplot*` | `mxplot-*` |
| Minimal analytic source | `Source_simple` | `Source_flat` |
| Coupling format | `MCPL_output` / `MCPL_input` (both codes, identical) | |

---

## Recording a simulation contract

Every exercise's Task ends with a short note to write down six facts about the run you just did — your **simulation contract**:

1. **Instrument parameters** — the full set of values you actually ran with, as `name=value`, not "defaults".
2. **Random seed** — set explicitly with `--seed=<N>`, or left to vary?
3. **Number of rays (`ncount`)** — your `-n`/`--ncount` value (Monte Carlo statistics, not physical source strength).
4. **Monitor settings** — binning, limits, `options=` string for every monitor.
5. **Output files** — where the run's `.dat`/`.h5` files ended up.
6. **Software version** — `mcstas --version`/`mcxtrace --version`.

None of this needs a special tool — a short text file next to your output is enough. These six facts are exactly what a later, automated dataset-generation pipeline needs for every run — see [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md) for how this scales into a per-sample metadata schema.

---

## Exercise 1 — Your first beamline

**Goal.** Get comfortable pulling up component documentation, then build, compile and run a complete (if minimal) instrument and read its output correctly.

**Task.**
1. Before typing anything: `mcdoc Source_simple`/`mxdoc Source_flat` and `mcdoc PSD_monitor`/`mxdoc PSD_monitor` — note which parameters are required vs. optional. (Full manual: `mcdoc -c`/`mxdoc -c`.)
2. Build the beamline below — source, then two monitors 5 m downstream — or start from [`hints/`](./hints/) (`ex2_mcstas_starter.instr`/`ex2_mcxtrace_starter.instr`) if you'd rather not type it.

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

3. Run: `mcrun ex2_mcstas.instr -n 1e6` / `mxrun ex2_mcxtrace.instr -n 1e6`. Plot both monitors.

**Checkpoints.**
- `psd.dat` shows a filled spot/square matching `focus_xw`/`focus_yh`; `lm.dat` shows a flat-topped histogram between `lambda0±dlambda`.
- Every monitor reports three numbers per bin (and a total): intensity, error, event count. You can say which one actually counts *rays*, and which two are computed from ray *weight*.
- Write your six-fact simulation contract for this run.

**If time allows.** Add a second `PSD_monitor` right after the source (`AT (0,0,0.01) RELATIVE src`) and compare footprints at the two distances.

---

## Exercise 2 — Shaping the source

**Goal.** Connect source parameters to visible monitor effects, and separate "where/which way" (geometry) from "what spectrum" (wavelength content) — two effect categories you'll need to tell apart all week.

**Task.** Starting from Exercise 1's instrument, change **one thing at a time**, re-running between changes:
1. Double `focus_xw`/`focus_yh` — what changes on the PSD monitor?
2. Put focus back, double `radius` instead — what changes this time, and what *doesn't*, even though the source is now bigger?
3. Move both monitors to `dist=10` (and `10.01`), keeping focus fixed, and add a `Divergence_monitor` — how does the divergence spread compare to the `dist=5` case?
4. Reset the geometry; instead try `lambda0=1.0, dlambda=0.5`, then `lambda0=5.0, dlambda=0.5` — confirm `lm.dat` tracks the change while the PSD monitor doesn't.

**Checkpoints.**
- You can predict, before running, whether a given source parameter will move the PSD footprint, the divergence, the wavelength histogram, or none of the three.
- You can explain why changing `radius` barely changes the illuminated area, even though it changes where rays start.
- Log the contract for whichever sub-run you found most informative.

**If time allows.** Set the focus target smaller than the source `radius` — is there a limit to how tightly a simple analytic source can be focused?

---

## Exercise 3 — Statistics and normalisation: what actually changed?

**Goal.** Tell apart a genuine physical change, Monte Carlo noise, a monitor binning choice, and a normalisation convention — the single most important interpretive skill for anyone who will later feed this kind of data to an AI model, since a model can't tell these apart on its own either.

**Background, briefly.** McStas/McXtrace are weighted Monte Carlo codes: a monitor's intensity `I` is a weight-sum of the rays that crossed it, not a raw count, and its error `E` is the statistical uncertainty on `I` — for a fixed instrument, `E` shrinks roughly as `1/sqrt(N)` as `ncount` grows, but this says nothing about physical source strength. A monitor's *binning* trades resolution for per-bin statistics without changing the underlying physics. A monitor's *normalisation* (as-simulated, per cm², per unit solid angle, …) rescales the reported numbers by a convention, not by anything physical changing in the beam.

**Task.** Two single-variable comparisons, fixing everything except the one thing named:
1. **Monte Carlo noise.** Run at `-n 1e3`, then `1e5`, then `1e7`, changing nothing else. Note `I`, `E` and event count for `psd.dat` each time.
2. **Normalisation.** Replace `PSD_monitor` with `Monitor_nD(xwidth=0.2, yheight=0.2, options="x y")`, run, then rerun with `options="x y, per cm2"`. Compare the reported total intensity — same rays, same physics, different convention.

**Checkpoints.**
- Does `I` change meaningfully across the three `ncount` values in step 1? Should it? Does `E` scale roughly like `1/sqrt(N)`?
- Given two monitor outputs that look different, you can list at least three possible causes (physical change, MC noise, binning, normalisation) and name one piece of metadata that would distinguish each pair.
- Log the contract for both sub-runs — `ncount` and the monitor `options=` string matter most here (see [`Data_Generation_Pipeline.md`](../../../Data_Generation_Pipeline.md) on why mixing these causes without recording which is which risks a model learning the artefact instead of the physics).

**If time allows.** Binning: rerun step 2's baseline `PSD_monitor` with `nx=10, ny=10` and then `nx=400, ny=400` at fixed `ncount` — same physics, different apparent smoothness. Pulsing: add `EXTEND %{ t = 10e-3*rand01(); %}` (or the McXtrace equivalent) after the source and a `TOF_monitor` after the PSD monitor — does pulsing change the *intensity* the PSD monitor reports? Under-sampling: run Exercise 1's instrument at `-n 1e2` and look at the PSD monitor — the "texture" is now Monte Carlo noise, not physics, worth keeping in mind for Day 3's Debye-Scherrer rings.

---

## Further material, if time allows

These were full exercises in the original, dedicated Sources & Monitors session; with the morning now shared with Optics, treat them as pointers to follow up on independently rather than exercises to complete in the room.

- **`Monitor_nD`, the swiss-army-knife monitor.** `PSD_monitor` and `L_monitor` are themselves thin wrappers around specific `Monitor_nD(options=...)` configurations. Try reproducing Exercise 1's two monitors as `Monitor_nD(options="x y")` and `Monitor_nD(options="lambda limits=[0 8] bins=100")` — then look up `mcdoc monitor`/`mxdoc monitor` to see how many named monitors could, in principle, be replaced by a suitably configured `Monitor_nD`.
- **Realistic source spectra.** McStas's `Source_gen` models a continuous moderator spectrum as a sum of Maxwellian components (a real ILL-style parameter set is in the `templateDIFF` example instrument elsewhere in this repo); McXtrace's `Bending_magnet` models a synchrotron bending-magnet source from accelerator parameters. Swapping either in for `Source_simple`/`Source_flat` shows how far a flat-spectrum assumption can mislead a downstream analysis.
- **Coupling instruments with MCPL.** `MCPL_output`/`MCPL_input` write and read a standardised, code-agnostic ray list — the same mechanism used to couple McStas and McXtrace to each other or to codes like MCNP/Geant4. Writing a beam out from one instrument and reading it into a second, source-free instrument is a good way to see that MCPL genuinely doesn't "know" which source produced it — and, as with any intermediate file, it needs its own simulation contract recorded alongside it.

---

*(Facilitator notes for this session are collected separately in [`Facilitator_Notes.md`](./Facilitator_Notes.md), not shown here.)*
