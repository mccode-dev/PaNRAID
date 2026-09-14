# Facilitator Notes — PowderN

Internal notes for whoever is running [`Exercises_PowderN.md`](./Exercises_PowderN.md); not intended for participants.

- Both parts are intentionally minimal (3–4 components) for the baseline — the point is to get to a recognisable Debye-Scherrer pattern fast, not to build a realistic diffractometer on the first pass.
- Real bundled reference files used in the exercise sheet: `Al.laz` and `LaB6.cif` are both standard example materials already used elsewhere in the McStas/McXtrace example suites (the `Tests_samples/Test_PowderN` McXtrace example is exactly the LaB₆-via-CIF case shown here, and produces the `PowderN.png` Debye-Scherrer image already referenced in this project's samples notes).
- The exact McStas syntax for pointing `PowderN` at an NCrystal material (A2, step 6) is left as a doc-lookup/verification step deliberately — worth confirming against the installed McStas version before the session, and adjusting the exercise text once confirmed.
- A natural Day-4 follow-on: turn the A3/B3 "attach yesterday's optics" option into the required starting point, i.e. build the full source → optics → sample → detector diffractometer in one pass, mirroring how the NECSA/ISIS school repositories build their powder diffractometer exercise directly on top of their monochromator exercise.
- A [`hints/`](./hints/) folder with ready-made starter `.instr` files now exists, covering the A1/B1 baseline only (both codes). A2/B2 (the NCrystal/CIF-vs-table comparison, which is the actual point of that step) and the A3/B3 optics-attachment option are not covered by a starter file and are still built from scratch.
