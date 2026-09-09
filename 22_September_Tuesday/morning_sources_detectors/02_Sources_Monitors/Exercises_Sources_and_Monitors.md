# Sources & Monitors — Hands-on Exercises

*McStas (neutrons) & McXtrace (X-rays) — PaNRAID School, Day 2 morning*

These exercises follow directly on from the `McStas_McXtrace_Sources_and_Monitors.pptx` lecture. They are written for absolute beginners to the two codes: no prior `.instr`-file experience is assumed, only that McStas and/or McXtrace are installed and that participants have seen the lecture slides once.

Every exercise is given in parallel for both codes. The instrument logic, parameter names and monitor syntax are close to identical — only component names, typical wavelength/energy scales and a few facility-specific components differ. Participants working in only one code can simply skip the other column; participants with time to spare are encouraged to do both and compare.

## How to use this sheet

- Work in a fresh folder, e.g. `ex_sources_monitors/`, one `.instr` file per exercise (or one file you keep editing — your choice).
- Compile and run from the command line with `mcrun <file>.instr <params> -n 1e6` (McStas) or `mxrun <file>.instr <params> -n 1e6` (McXtrace), or use `mcgui` / `mxgui` if you prefer a graphical front-end.
- Plot results with `mcplot` / `mcplot-pyqtgraph` / `mcplot-matplotlib` (McStas) or the equivalent `mxplot-*` (McXtrace).
- Look up any component's parameters at any time with `mcdoc <Component>` / `mxdoc <Component>`, or the full manual via `mcdoc -c` / `mxdoc -c`.
- Each exercise lists **Checkpoints** — questions you should be able to answer once you've run the simulation. These are the real goal; getting an instrument to compile is only step one.

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

## Exercise 1 — Warm-up: finding your way around the docs

**Goal:** get comfortable pulling up component documentation before you need it in anger.

1. Open a terminal and run `mcdoc` (McStas) and/or `mxdoc` (McXtrace) with no arguments. Confirm the components overview page opens.
2. Look up the source you'll use in Exercise 2: `mcdoc Source_simple` / `mxdoc Source_flat`. Identify, in the parameter list: which parameters are required (no default) vs. optional.
3. Look up `mcdoc PSD_monitor` / `mxdoc PSD_monitor` and `mcdoc L_monitor` / `mxdoc L_monitor` the same way.
4. Generate the full PDF component manual with `mcdoc -c` / `mxdoc -c` and confirm it opens — this is your reference for the rest of the week.

**Checkpoints**
- Which parameters does `Source_simple`/`Source_flat` require you to set explicitly, and which have sensible defaults?
- What unit is `dist` given in? What about `focus_xw`?
- Why might the version of the manual installed on your laptop differ slightly from the one on mcstas.org / mcxtrace.org?

---

## Exercise 2 — Your first beamline: a source and two monitors

**Goal:** build, compile and run a complete (if minimal) instrument, and read its output.

A ready-to-run starting point for this exact instrument is available in [`hints/`](./hints/) (`ex2_mcstas_starter.instr` / `ex2_mcxtrace_starter.instr`) if you'd rather not type it out — but if you want the full experience of building it from a blank file, ignore that folder and type along below.

Below is the same three-component beamline in both codes — a progress bar, a source, and two monitors 5 m downstream. Type it in (or copy it), save it, and run it.

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

Run each with e.g. `mcrun ex2_mcstas.instr -n 1e6` / `mxrun ex2_mcxtrace.instr -n 1e6`, then plot the results.

**Checkpoints**
- What shape and size is the illuminated spot in `psd.dat`? Does it match a parameter you set on the source?
- What shape is the `lm.dat` histogram? Why that shape, given how `lambda0`/`dlambda` are used to draw a wavelength for each ray?
- Every monitor output reports three numbers per bin (and a total): intensity, error, and event count. Which of these three actually counts *rays*, and which are computed from ray *weight*?
- The only line that differs between the two files is the source component name (`Source_simple` vs `Source_flat`). Everything else — parameter names, units, monitor syntax — is identical. Why do you think the two projects chose to keep it that way?

---

## Exercise 3 — Shaping the source: position, direction, spectrum

**Goal:** connect each source parameter to a visible effect on your monitors, and separate "where/which way" from "what spectrum".

Starting from your Exercise 2 instrument, make each of the following changes **one at a time**, re-running and re-plotting between changes:

1. Double `focus_xw` and `focus_yh` (e.g. to 0.2/0.2). What changes on the PSD monitor?
2. Put `focus_xw`/`focus_yh` back, and instead double `radius` (source size) to 0.1. What changes on the PSD monitor this time — and what *doesn't* change, even though you made the source bigger?
3. Move the monitors twice as far away (`dist=10`, and move both monitor `AT` positions to `10` and `10.01`), keeping `focus_xw`/`focus_yh` fixed. Add a `Divergence_monitor` (McStas) / `Divergence_monitor` (McXtrace — same name in both) just before the PSD monitor. How does the divergence distribution change compared to the `dist=5` case?
4. Reset the geometry, and instead vary the spectrum: try `lambda0=1.0, dlambda=0.5` and then `lambda0=5.0, dlambda=0.5`. Confirm the `lm.dat` histogram tracks the change.

**Checkpoints**
- Why does changing `radius` barely change the illuminated area on the PSD monitor, even though it clearly changes where rays start?
- What *does* control the size of the illuminated spot at a given distance?
- If you doubled the distance but kept the focus target the same physical size, did the beam get more or less divergent? Does that match the geometry in the "anatomy of a simple source" picture from the lecture?

---

## Exercise 4 — Statistics: `ncount`, weight, and the error bar

**Goal:** understand that Monte Carlo statistics, not the physical source strength, are what `ncount` controls.

1. Run your Exercise 2 instrument three times with `-n 1e3`, `-n 1e5` and `-n 1e7`.
2. For each run, note the total intensity `I`, error `E`, and event count `N` reported for `psd.dat` (McStas prints this to the terminal at the end of the run; it's also in the header of the `.dat` file).

**Checkpoints**
- Does the total intensity `I` change meaningfully between the three runs? Should it?
- Does the error `E` change? Roughly how does it scale with `N` — does it look consistent with the Monte Carlo `1/√N` behaviour mentioned in the lecture?
- If you wanted a *higher-flux* virtual source, would raising `ncount` help? What would you change instead?
- Add `EXTEND %{ t = 10e-3*rand01(); %}` (McStas) / the equivalent line (McXtrace) after your source component to force a 1 ms pulse. Add a `TOF_monitor` after the PSD monitor. Does pulsing the source change the *intensity* reported by the PSD monitor?

---

## Exercise 5 — The swiss-army knife: `Monitor_nD`

**Goal:** reproduce the results of Exercise 2 using a single, more general monitor type, then push it further than `PSD_monitor`/`L_monitor` can go.

`Monitor_nD` exists under the same name, with the same `options=` grammar, in both codes.

1. Replace your `psd` component with:
   ```c
   COMPONENT psd_nd = Monitor_nD(xwidth=0.2, yheight=0.2, options="x y")
   AT (0,0,5) RELATIVE src
   ```
   Confirm it reproduces the same picture as your original `PSD_monitor`.
2. Replace your `lm` component similarly, using `options="lambda limits=[0 8] bins=100"`. Confirm it reproduces the same histogram as `L_monitor`.
3. Now go further: add a third `Monitor_nD` with `options="x y, per cm2"` and compare — what does normalising "per cm2" do to the reported intensity, and why might that be a more useful unit when comparing monitors of different sizes?
4. Stretch: try `options="banana, theta limits=[-20 20], bins=80"` on a monitor placed with a `radius=5` and see how a curved ("banana") monitor differs from a flat one.

**Checkpoints**
- What did you have to change to get `Monitor_nD` to reproduce `PSD_monitor` and `L_monitor` exactly? What does that tell you about what those "simple" monitors are, under the hood?
- Look up `mcdoc monitor` / `mxdoc monitor` — how many monitor components are listed, and how many of them could in principle be replaced by a suitably configured `Monitor_nD`?

---

## Exercise 6 (stretch) — Two source landscapes

**Goal:** swap your simple analytic source for a facility-realistic one, and see how the two codes diverge here specifically.

**McStas:** replace `Source_simple` with `Source_gen`, using a three-component Maxwellian continuous-source spectrum (values below are a real ILL-style set, taken from the `templateDIFF` example instrument elsewhere in this repository):
```c
COMPONENT src = Source_gen(radius=0.11, dist=5, focus_xw=0.1, focus_yh=0.1,
    lambda0=2.5, dlambda=1.5,
    T1=229.6, I1=5.32e13, T2=1102, I2=4.37e12, T3=437.1, I3=3.84e13)
AT (0,0,0) RELATIVE origin
```
Compare the `L_monitor`/`Monitor_nD` wavelength spectrum to the flat spectrum from Exercise 2 — it should now show the characteristic Maxwellian shape rather than a flat top.

**McXtrace:** rather than a ready-made snippet, use the doc-reading skill from Exercise 1: run `mxdoc Bending_magnet` and identify the parameters you'd need to set to model a synchrotron bending-magnet source (accelerator energy, current, magnetic field, and the energy/wavelength range of interest). Build a minimal instrument around it and compare its spectrum shape to `Source_flat`.

**Checkpoints**
- Which source family did you use for McStas (reactor/continuous, pulsed, or particle-list), and why does that match "Maxwellian" better than a pulsed spallation source component would?
- For McXtrace, what physical parameters does `Bending_magnet` need that `Source_flat` didn't? Why do you think X-ray sources are parameterised in terms of the accelerator, while (continuous) neutron sources are parameterised in terms of a moderator temperature?

---

## Exercise 7 (stretch) — Coupling instruments with MCPL

**Goal:** decouple your source from your monitors into two separate instruments, connected only by a particle-list file — the same mechanism used to couple McStas and McXtrace to each other or to codes like MCNP/Geant4.

**Step A — write the rays out.** Take your Exercise 2 source (McStas or McXtrace) and add, in place of your monitors:
```c
COMPONENT vout = MCPL_output(filename="beam.mcpl", doubleprec=1, polarisationuse=1)
AT (0,0,5) RELATIVE src
```
Run it once to produce `beam.mcpl` (or `beam.mcpl.gz`).

**Step B — read the rays back in.** Build a *second*, separate instrument containing only:
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

**Checkpoints**
- Do the two monitor outputs agree (within statistics)? Should they?
- What happens if you set `ncount` on instrument B higher than the number of rays actually stored in `beam.mcpl`?
- Instrument B never mentions `Source_simple`/`Source_flat`/`Source_gen` at all — what does that tell you about what MCPL is actually storing?
- (If you have both codes installed) try writing the MCPL file from the McStas instrument and reading it into the McXtrace instrument, or vice versa. What would need to be true of the ray's physical meaning for this to make sense?

---

## Facilitator notes

- Exercises 1–4 are the core material for absolute beginners and should comfortably fit a ~2 hour hands-on block; 5 is a natural extension once time allows; 6–7 are stretch goals for fast finishers or a follow-up session.
- All code snippets above are self-contained and were checked against the parameter names used in the accompanying lecture slides (`McStas_McXtrace_Sources_and_Monitors.pptx`) and against the `templateDIFF` example instrument already in this repository (`instruments/mcstas/templateDIFF/templateDIFF.instr`).
- Suggested next step: turn Exercises 2, 5 and 7 into ready-made starter `.instr` files (with a few `???` gaps for participants to fill in) rather than have participants type from scratch — happy to draft those next if useful.
