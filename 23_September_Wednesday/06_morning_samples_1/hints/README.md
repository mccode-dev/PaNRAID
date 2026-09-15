# Hints

Optional, ready-to-run starting points for the exercises in
[`../Exercises_PowderN.md`](../Exercises_PowderN.md).

Nobody has to use these — if you'd rather start from a completely blank
`.instr` file and type things out following the exercise sheet, just ignore
this folder entirely. It's here for anyone who wants a working instrument to
compile, run and start modifying right away, instead of typing from scratch.

| File | Corresponds to |
|------|-----------------|
| `ex_powderN_mcstas_starter.instr` | Part A, Exercise A1 (McStas): source + `PowderN(reflections=reflections)` + beamstop + `PSD_monitor` |
| `ex_powderN_mcxtrace_starter.instr` | Part B, Exercise B1 (McXtrace): source + `PowderN(reflections=reflections)` + beamstop + `PSD_monitor` |

Both starters are exactly the A1/B1 baseline — four components, source to
detector — and both should already show Debye-Scherrer rings on the first
run (default materials: `Al.laz` for McStas, `LaB6.cif` for McXtrace).
Exercise A2/B2 (comparing the same material described a second way —
NCrystal vs. `.laz`, or CIF vs. pre-computed `.laz`) is left for you to build
as a second instrument or a second `PowderN` component starting from these;
that comparison is the actual point of A2/B2, so it isn't done for you here.

Both files expose `reflections` as a command-line-settable **string**
instrument parameter rather than a hard-coded value, specifically so they
can be used directly for Exercise A4/B4's wavelength/energy × material
scan (`reflections=Cu.laz`, `reflections=Si.laz`, …) without editing the
`.instr` file. The A3/B3 "attach yesterday's optics" option isn't covered by
a starter file — it's a matter of replacing the source in these same files
with your Optics-session guide or monochromator's exit beam.
