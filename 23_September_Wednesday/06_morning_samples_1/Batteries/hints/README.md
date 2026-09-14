# Hints

Optional, ready-to-run host instruments for the exercise in
[`../README.md`](../README.md).

Nobody has to use these. The exercise itself asks you to build a host
instrument by copying and adapting `Tomography.instr` / `PSI_ICON.instr`
(McStas, from `$MCSTAS/examples`) or `Airport_scanner.instr` (McXtrace, from
`$MCXTRACE/examples`) — that adaptation, and reading a real templated
instrument's structure, is a genuine part of the exercise, so do that first
if you have time.

These two files exist for a narrower reason: to give you something that
compiles and runs *immediately*, so you can see the `sample_pos` "connecting
point" mechanism from `../README.md` working end to end (source → battery →
detector) before you go anywhere near a bigger template instrument, or as a
fallback if `Tomography.instr`/`Airport_scanner.instr` turn out to be more
than you want to untangle in the time available.

| File | Corresponds to |
|------|-----------------|
| `ex_battery_mcstas_host_starter.instr` | McStas track: source + `sample_pos` Arm + `%include "../LiIon_Battery_Union_Neutron.instr"` + `PSD_monitor` |
| `ex_battery_mcxtrace_host_starter.instr` | McXtrace track: source + `sample_pos` Arm + `%include "../LiIon_Battery_Union_Xray.instr"` + `PSD_monitor` |

Both are deliberately bare — a single radiograph, no rotation stage, no CT.
Turning either into a real radiography/CT setup (rotating the `sample_pos`
Arm, scripting an angle scan, reconstructing) is the actual exercise content
in `../README.md` and isn't done for you here.
