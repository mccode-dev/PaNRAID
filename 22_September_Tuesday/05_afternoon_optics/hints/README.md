# Hints

Optional, ready-to-run starting points for the exercises in
[`../Exercises_Optics.md`](../Exercises_Optics.md).

Nobody has to use these — if you'd rather start from a completely blank
`.instr` file and type things out following the exercise sheet, just ignore
this folder entirely. It's here for anyone who wants a working instrument to
compile, run and start modifying right away, instead of typing from scratch.

| File | Corresponds to |
|------|-----------------|
| `exA2_mcstas_starter.instr` | Part A, Exercise A2 (McStas): source focused onto a guide entrance, a straight `Guide_gravity`, and the `L_monitor`/`PSD_monitor`/`DivPos_monitor` trio at the exit |
| `exB2_mcxtrace_starter.instr` | Part B, Exercise B2, Track 1 (McXtrace): synchrotron-like source and a single `Bragg_crystal` on a rotated arm |

Both starters are completed, runnable instruments for the *geometry* each
exercise builds — but each deliberately leaves the actual physics question
open:

- `exA2_mcstas_starter.instr` ships with gravity switched off (the McStas/
  `mcrun` default). Exercise A3 is to re-run this same file with `-g` /
  `--gravitation` added to the command line and compare — no instrument-file
  edit needed.
- `exB2_mcxtrace_starter.instr` ships with `A1=0`, i.e. the crystal isn't
  rotated onto the Bragg condition yet and nothing will come through
  downstream. Working out `theta` from Bragg's law (step 7) and setting `A1`
  yourself is the actual exercise; the rocking-curve scan (step 8) and
  turning this into a double-crystal monochromator (steps 9–11) are natural
  next steps from the same file.

Exercise A1 (characterising the beam with no guide) and Track 2's multilayer
variant (B2′) aren't covered by a starter file — both are short enough, and
different enough from the files above, that typing them from the exercise
sheet is the better route.
