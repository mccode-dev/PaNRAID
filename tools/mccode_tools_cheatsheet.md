# McStas / McXtrace User Tools Cheat Sheet

Source: `McCode/tools/Python`

**Naming convention:** almost everything named `mc<something>` on the McStas
side has a direct `mx<something>` counterpart on the McXtrace side, built
from the *same* Python source, with the neutron/photon ("particle") wording
and a few McStas-only options (e.g. `--gravity`, time-of-flight mode)
adjusted accordingly. Where a tool has several rendering **variants**
(html / matplotlib / pyqtgraph / webgl / ...), the variant is appended after
a dash, e.g. `mcplot-html` / `mxplot-html`.

---

## 1. mcgui / mxgui

A graphical front-end (editor, compile/run, visualize) — no real
command-line switches beyond an optional instrument file.

| `mcgui` / `mxgui` | |
|---|---|
| `INSTR` | *(optional)* name of an instrument file to open on startup |

---

## 2. mcrun / mxrun

Options are identical between McStas and McXtrace (only the particle name
in help text, and the McStas-only `-g`/`--gravitation` flag, differ).

### mcrun / mxrun — general & compile options

| Option | Description |
|---|---|
| `-c`, `--force-compile` | force rebuilding of the instrument |
| `--cogen COGEN` | choice of code generator (implies `-c`) |
| `-C`, `--c-lint` | run a C linter on generated code; implies `-c -v`; **no simulation is run** |
| `-I PATH` | append `PATH` to the McCode search path (implies `-c`) |
| `--D1/--D2/--D3 VAL` | set extra `-D` compiler args (implies `-c`) |
| `--no-cflags` | disable optimising compiler flags (faster compilation) |
| `--no-main` | do not generate a `main()` (e.g. for `mcstas2vitess.pl`); implies `-c` |
| `--embed` | store a copy of the instrument file in the output directory (default: on) |
| `--verbose` | enable verbose output |
| `--showcfg ITEM` | print a resolved config path (`bindir`, `libdir`, `resourcedir`, `tooldir`) and exit |
| `--write-user-config` | generate a user config file and exit |
| `--edit-user-config` | generate + open the user config file in `$EDITOR` |
| `--override-config PATH` | load config file from a specific directory |

### mcrun / mxrun — parameters, scanning & optimisation

| Option | Description |
|---|---|
| `param=val`, `param=min,max` | fixed parameter, or scan interval (comma-separated) |
| `-p`, `--param FILE` | read `name=value` parameters from `FILE` |
| `-N`, `--numpoints NP` | number of linear scan points |
| `-L`, `--list` | use a fixed list of points for linear scanning |
| `-M`, `--multi` | run a multi-dimensional scan |
| `--seeds SEEDS` | comma-separated range of seeds to scan |
| `--scan_split N` | parallelise scan steps as `N` separate CPU processes (0 = auto) |
| `--optimize` | optimise instrument parameters to maximise (or minimise) monitors |
| `--optimize-monitor NAME` | monitor to optimise (default: all) |
| `--optimize-eval EXPR` | expression to evaluate per detector, e.g. `d.intensity`, `d.intensity/d.dX` |
| `--optimize-minimize` | minimise instead of maximise |
| `--optimize-method METHOD` | scipy `minimize` method (default: `powell`) |
| `--optimize-maxiter N` | max optimisation iterations (default: 1000) |
| `--optimize-tol TOL` | optimisation termination tolerance |
| `--optimise-file FILE` | file to store scan/optimisation results (default: `mccode.dat`) |

### mcrun / mxrun — simulation & instrument options

| Option | Description |
|---|---|
| `-n`, `--ncount COUNT` | number of particles to simulate |
| `-s`, `--seed SEED` | random seed (must be non-zero) |
| `-t`, `--trace N` | enable particle trace through the instrument |
| `--no-trace` | disable particle trace (combine with `-c`) |
| `-g`, `--gravitation`, `--gravity` | *(McStas only)* enable gravitation for all trajectories |
| `-y`, `--yes` | assume default parameter values |
| `-d`, `--dir DIR` | output directory (default: `INSTRUMENT_TIMESTAMP`) |
| `--dirprefix PREFIX` | output directory named `PREFIX_TIMESTAMP` |
| `--dirsuffix SUFFIX` | output directory named `INSTRUMENT_SUFFIX` |
| `-a`, `--append` | append data files to an existing directory |
| `--format FORMAT` | output format, e.g. `McCode` or `NeXus` |
| `--IDF` | *(McStas only)* include XML IDF when `--format=NeXus` |
| `--no-output-files` | do not write any data files |
| `--bufsiz SIZE` | `Monitor_nD` list/buffer size |
| `--mpi NB_CPU` | spread the run over `NB_CPU` MPI processes |
| `--machines FILE` | path to an MPI machinefile |
| `--openacc` | parallelise using OpenACC (GPU) |
| `--funnel` | funnel simulation flow (mixed CPU/GPU) |
| `--vecsize`, `--numgangs`, `--gpu_innerloop` | OpenACC tuning parameters |
| `--autoplot` | open a plotter on the generated dataset after the run |
| `--autoplotter TOOL` | plotter to use with `--autoplot` |
| `--invcanvas` | forward inverted-canvas request to the autoplotter |
| `-i`, `--info` | print detailed instrument information |
| `--list-parameters` | print instrument parameters to stdout |
| `--meta-list` / `--meta-defined` / `--meta-type` / `--meta-data` | query component metadata |

---

## 3. mcplot / mxplot family

Three related tool groups live under `tools/Python/mcplot`, sharing a
loader/matching layer:

- **mcplot / mxplot** — plot one simulation's monitors
- **mcplotdiff / mxplotdiff** — plot the *difference* `a - b` between two simulations (2 datasets only)
- **mccoplot / mxcoplot** — *overlay* 2 or more simulations' monitors on the same axes

Each has three rendering variants: **html**, **matplotlib**, **pyqtgraph**.

### mcplot-html / mxplot-html

| Option | Description |
|---|---|
| `simulation` | file or directory to plot |
| `-n`, `--nobrowse` | do not open a web browser |
| `-l`, `--log` | enable log scale |
| `--autosize` | expand plot to window size on load |
| `--libpath PATH` | path to js library files (default: copy locally) |
| `-o`, `--output FILE` | output `.html` file |
| `-W`, `--width N` | iframe width |
| `-H`, `--height N` | iframe height |

### mcplot-matplotlib / mxplot-matplotlib

| Option | Description |
|---|---|
| `simulation` | file or directory to plot |
| `-t`, `--test` | data-loader test run (print plot graph structure) |
| `--html` | save to html via mpld3 (Linux only) |
| `--format FMT` | save to pdf/png/eps/svg... without opening a window |
| `--output FILE` | output file (extension may set format) |
| `--log` | start with log scale |
| `--backend NAME` | matplotlib backend to use |

### mcplot-pyqtgraph / mxplot-pyqtgraph

| Option | Description |
|---|---|
| `simulation` | file or directory to plot |
| `-t`, `--test` | data-loader test run |
| `--invcanvas` | invert canvas background (black → white) |

### mcplotdiff-html / mxplotdiff-html

Compares exactly two datasets: `diff = a - b`.

| Option | Description |
|---|---|
| `a` | first simulation (minuend) |
| `b` | second simulation (subtrahend) |
| `-A`, `--label-a NAME` | short label for `a` in titles/filenames |
| `-B`, `--label-b NAME` | short label for `b` in titles/filenames |
| `-n`, `--nobrowse` | do not open a web browser |
| `-l`, `--log` | also produce log-scale plot (single-file mode) |
| `-D`, `--no-dat` | do not write McCode-format `.dat`/`mccode.sim` alongside the html |
| `-o`, `--output DIR` | output directory |
| `--autosize` | expand plot to window size on load |
| `--libpath PATH` | path to js library files |
| `-W`, `--width N` / `-H`, `--height N` | iframe dimensions |

### mcplotdiff-matplotlib / mxplotdiff-matplotlib

| Option | Description |
|---|---|
| `a` / `b` | the two simulations to diff (`a - b`) |
| `-A`, `--label-a NAME` / `-B`, `--label-b NAME` | short labels for titles/filenames |
| `-t`, `--test` | plot graph structure test/print |
| `--html` | save to html via mpld3 (Linux only) |
| `--format FMT` / `--output FILE` | save to file without opening a window |
| `--log` | start with log scale |
| `--backend NAME` | matplotlib backend to use |

### mcplotdiff-pyqtgraph / mxplotdiff-pyqtgraph

| Option | Description |
|---|---|
| `a` / `b` | the two simulations to diff (`a - b`) |
| `-A`, `--label-a NAME` / `-B`, `--label-b NAME` | short labels for titles |
| `-t`, `--test` | data-loader test run |
| `--invcanvas` | invert canvas background |

*(2D diff monitors use a diverging blue/white/red colour map; press `c` to cycle colour maps as usual.)*

### mccoplot-html / mxcoplot-html

Overlays **2 or more** datasets (unlike mcplotdiff, not limited to two).

| Option | Description |
|---|---|
| `datasets` | 2+ simulation files/directories to overlay |
| `-L`, `--labels A,B,C` | comma-separated short labels, one per dataset (default: derived from each path) |
| `-C`, `--colours c1,c2,...` | comma-separated overlay colours, one per dataset |
| `-n`, `--nobrowse` | do not open a web browser |
| `-l`, `--log` | also produce log-scale plot (single-file mode) |
| `-o`, `--output DIR` | output directory |
| `--autosize` | expand plot to window size on load |
| `--libpath PATH` | path to js library files |
| `-W`, `--width N` / `-H`, `--height N` | iframe dimensions |

### mccoplot-matplotlib / mxcoplot-matplotlib

| Option | Description |
|---|---|
| `datasets` | 2+ simulation files/directories to overlay |
| `-L`, `--labels A,B,C` | comma-separated short labels per dataset |
| `-C`, `--colours c1,c2,...` | comma-separated overlay colours per dataset |
| `-t`, `--test` | print matched monitor groups before plotting |
| `--html` | save to html via mpld3 (Linux only) |
| `--format FMT` / `--output FILE` | save to file without opening a window |
| `--log` | start with log scale |
| `--backend NAME` | matplotlib backend to use |

### mccoplot-pyqtgraph / mxcoplot-pyqtgraph

| Option | Description |
|---|---|
| `datasets` | 2+ simulation files/directories to overlay |
| `-L`, `--labels A,B,C` | comma-separated short labels per dataset |
| `-C`, `--colours c1,c2,...` | comma-separated overlay colours per dataset |
| `-t`, `--test` | print matched monitor groups before plotting |
| `--invcanvas` | invert canvas background |

*(Legends always show compact letters `A`, `B`, `C`, ...; the full dataset identity is shown separately in the title/header.)*

---

## 4. mcdisplay family

All variants wrap `mcrun --trace` under the hood; `INSTR` plus any
`name=value` instrument parameters are forwarded straight to it. The
**default** is `mcdisplay`/`mxdisplay` → pyqtgraph.

### mcdisplay / mxdisplay *(default = pyqtgraph)*

| Option | Description |
|---|---|
| `INSTR` | instrument file (`.instr` or compiled binary) |
| `name=value ...` | simulation parameters, passed through to `mcrun` |
| `--default` | automatically use instrument default parameter values |
| `-n`, `--ncount N` | number of particles to trace (default: 300) |
| `--dirname DIR` | override output directory name |
| `--inspect COMP` | show only rays reaching component `COMP` |
| `--invcanvas` | invert canvas background |
| `--tof`, `--TOF`, `--ToF` | *(McStas only)* enable time-of-flight display mode |

**Interactive keys:** `q` quit · `p` save png · `s` save svg (not on Windows) · `space`/`F5` next ray · click a subplot to zoom, right-click to exit zoom · `h`/`F1` component list.

### mcdisplay-matplotlib / mxdisplay-matplotlib

Thin bash wrapper piping `mcrun --trace` output into a matplotlib 3D viewer — options are parsed by the wrapper script itself, not Python argparse.

| Option | Description |
|---|---|
| `INSTR` | instrument file |
| `name=value ...` | simulation parameters |
| `-n N`, `--ncount N`, `--ncount=N` | number of particles to trace (capped at 1e2 by the wrapper) |
| `--trace={1,2}` | classic (1) or new (2, default) visualisation mode |
| `--backend=NAME` | matplotlib backend; `pdf`/`pgf`/`ps`/`svg` save a hardcopy instead of showing a window |
| `--help` | show wrapper usage and exit |

### mcdisplay-webgl / mxdisplay-webgl *(NodeJS/vite-based)*

| Option | Description |
|---|---|
| `INSTR` | instrument file |
| `name=value ...` | simulation parameters |
| `--default` | automatically use instrument default parameter values |
| `-n`, `--ncount N` | number of particles to trace (default: 300) |
| `-t`, `--trace N` | visualisation mode (default: 2) |
| `-d`, `--dirname DIR` | override output directory name |
| `--inspect COMP` | show only rays reaching component `COMP` |
| `--first COMP` / `--last COMP` | zoom range start/end component |
| `--invcanvas` | invert canvas background |
| `--nobrowse` | do not open a web browser |
| `--timeout SEC` | shutdown time of the npm/vite dev server (default: 300) |

*(First run performs a one-time `npm`/`vite` module install, which needs internet access and can take minutes.)*

### mcdisplay-webgl-classic / mxdisplay-webgl-classic

| Option | Description |
|---|---|
| `INSTR` | instrument file |
| `name=value ...` | simulation parameters |
| `--default` | automatically use instrument default parameter values |
| `-n`, `--ncount N` | number of particles to trace (default: 300) |
| `-t`, `--trace N` | visualisation mode (default: 1) |
| `-d`, `--dirname DIR` | override output directory name |
| `--inspect COMP` | show only rays reaching component `COMP` |
| `--first COMP` / `--last COMP` | zoom range start/end component |
| `--invcanvas` | invert canvas background |
| `--nobrowse` | do not open a web browser |

### mcdisplay-cad / mxdisplay-cad *(bonus: export instrument geometry to CAD)*

Requires the `cadquery` Python package.

| Option | Description |
|---|---|
| `INSTR` | instrument file |
| `name=value ...` | simulation parameters |
| `--default` | automatically use instrument default parameter values |
| `-n`, `--ncount N` | number of particles to trace (default: 0 — geometry export doesn't need rays) |
| `--dirname DIR` | override output directory name |
| `-f`, `--format FMT` | output format: `step` (default), `stl`, `xml`, `vrml`, `gltf`, `vtkjs` |

---

## 5. mctest family

Installation testing / benchmarking tools, under `tools/Python/mctest`.

### mctest / mxtest

Runs every `%Example` test embedded in the instrument library, compiling,
displaying (single-particle), and running each one, then compares the
result against the target value recorded in the instrument header.

| Option | Description |
|---|---|
| `TESTVERSION` | *(optional)* specific McCode version to test |
| `--ncount N`, `-n N` | ncount sent to `mcrun` (default: `1e6`) |
| `--seed S`, `-s S` | seed sent to `mcrun` (default: `1000`; `0`/`NULL` randomises) |
| `--mpi N` | MPI node count sent to `mcrun` |
| `--openacc` | pass `--openacc` to `mcrun` |
| `--nexus` | compile/run with NeXus output format everywhere |
| `--lint` | just run the C-linter (no simulation run) |
| `--config CONFIG` | test only this specific config — label name or absolute path |
| `--instr PATTERN` | test only instruments matching this regex (comma-separated for multiple) |
| `--comp COMP` | test only instruments that use component `COMP` |
| `--mccoderoot DIR` | root search folder for McCode installations |
| `--testdir DIR` | write test results directly into `DIR` (default: cwd) |
| `--local DIR` | pick up instruments to test from `DIR` instead of the McCode installation |
| `--limit N` | test only the first `N` instruments per version |
| `--skipnontest` | skip compiling instruments that have no `%Example` test |
| `--suffix SUFFIX` | append `SUFFIX` to the test directory name |
| `--uid ID` | unique identifier for the suffix (default: timestamp) |
| `--compilemax S` | max seconds allowed per compilation (default: 600; x100 with `--lint`) |
| `--runmax S` | max seconds allowed per test run (default: 3600) |
| `--displaymax S` | max seconds allowed per test display run (default: 60) |
| `--permissive` | exit 0 even if some tests fail |
| `--versions` | display local version info |
| `--verbose` | print a test/no-test status header before each test |

### mcviewtest / mxviewtest

Builds a single browsable HTML comparison report from one or more `mctest`
result sets (as written by `mctest --testdir`), diffing/co-plotting each
row against a chosen reference column via `mcplotdiff-html`/`mccoplot-html`.

| Option | Description |
|---|---|
| `testdir` | *(optional)* root folder containing `mctest` result subfolders (default: cwd) |
| `--reflabel LABEL` | reference column/label to compare against (default: oldest subfolder in cwd) |
| `--testroot DIR` | test-root folder for interactive result management/cleanup |
| `--verbose` | output excessive debug information |
| `--nobrowse` | do not open a browser on completion |
| `--nodiff` | do not generate diff/co-plot comparison cells |
| `--diff-errors-only` | only diff rows that show a discrepancy (default: diff every valid row) |
| `--diffmax S` | max seconds per diff/co-plot comparison (default: 300) |
| `--diffworkers N` | number of comparisons to run in parallel (default: number of CPUs) |

---

## 6. mcdoc / mxdoc

Generates browsable documentation for installed and local instrument/component files, under `tools/Python/mcdoc`.

| Option | Description |
|---|---|
| `searchterm` | *(optional)* search filter, or a specific `.instr`/`.comp` filename |
| `-i`, `--install` | generate the full installation master doc page |
| `-d`, `--dir DIR` | also include search results from `DIR` (local instruments/components) |
| `-m`, `--manual` | open the user manual PDF |
| `-c`, `--comps` | open the component manual PDF |
| `-w`, `--web` | open the McStas/McXtrace website |
| `-v`, `--verbose` | print a parsing log during execution |
| `-M`, `--md` | also emit Markdown (`.md`) doc files (HTML is always written) |
| `-T`, `--tex` | also emit LaTeX (`.tex`) doc files |
| `-A`, `--all-formats` | emit HTML, Markdown, and LaTeX together |
| `--in-repo` | place output next to the source files instead of the installed docdir (no master page) |
| `-o`, `--outdir DIR` | write results to `DIR` (in-repo use only) |

*(No `searchterm`/`--install`/`--manual`/`--comps`/`--web` at all → browse the existing installed docs directly.)*

---

## 7. Matlab / Octave / iFit tools

A second, older `mcplot`/`mcdisplay` pair lives under `tools/matlab`, implemented as bash wrapper scripts around `.m` files rather than Python. They run under **Matlab**, **Octave**, or **iFit** (a Matlab-compiler-based standalone runtime, see <https://ifit.mccode.org>) — the wrapper auto-detects whichever is available, preferring Matlab, then Octave, then iFit, and falls back to the plain Python `mcplot`/`mcdisplay` if none of the three are found.

### mcplot-matlab / mxplot-matlab

| Option | Description |
|---|---|
| `FILE`\|`DIR` | monitor file or simulation directory to plot (default: current directory) |
| `-m` | explicitly request Matlab (skip auto-detection) |
| `-o` | explicitly request Octave |
| `-i` | explicitly request iFit |
| `-h` | show wrapper usage and exit |
| `-png`, `-jpg`, `-fig`, `-eps`, `-pdf` | *(parsed by `mcplot.m` itself, not the wrapper)* export each plotted monitor to the given format instead of just displaying it |

*(`-m`/`-o`/`-i`/`-h` are wrapper-level flags and must come first; the export-format flags are forwarded as-is to the underlying `.m` script.)*

### mcdisplay-matlab / mxdisplay-matlab

| Option | Description |
|---|---|
| `INSTR` | instrument file (`.instr` or compiled binary) |
| `name=value ...` | simulation parameters, forwarded to `mcrun` |
| `-m` | explicitly request Matlab |
| `-o` | explicitly request Octave |
| `-h` | show wrapper usage and exit |
| `-n N`, `--ncount N` | number of particles to simulate |
| `--inspect=COMP` | only plot components matching `COMP` — a partial name (e.g. `Monitor`), or an interval (`Monok:Sample`, `2:10`, `2:end`) |
| `-png`, `-jpg`, `-fig`, `-eps`, `-pdf`, `-tif` | *(parsed by `mcdisplay.m` itself)* export the 3D view to the given format |

---

## Quick reference: which tool for which job?

| I want to... | Use |
|---|---|
| Edit/compile/run instruments interactively | `mcgui` / `mxgui` |
| Run a simulation from the command line, or a parameter scan/optimisation | `mcrun` / `mxrun` |
| Plot one simulation's results | `mcplot-{html,matplotlib,pyqtgraph}` |
| Compare exactly two simulations (`a - b`) | `mcplotdiff-{html,matplotlib,pyqtgraph}` |
| Overlay 2+ simulations for direct comparison | `mccoplot-{html,matplotlib,pyqtgraph}` |
| Visualise instrument geometry + particle trajectories | `mcdisplay-{pyqtgraph,matplotlib,webgl,webgl-classic}` |
| Export instrument geometry to a CAD file | `mcdisplay-cad` |
| Plot/display results in Matlab, Octave, or iFit instead | `mcplot-matlab` / `mcdisplay-matlab` |
| Test/benchmark the whole instrument library against a McCode installation | `mctest` |
| Build a browsable pass/fail + diff report from `mctest` results | `mcviewtest` |
| Generate/browse instrument & component documentation | `mcdoc` |
