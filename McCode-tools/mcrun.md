[&larr; back to overview](README.md)

# mcrun / mxrun

Options are identical between McStas and McXtrace (only the particle name
in help text, and the McStas-only `-g`/`--gravitation` flag, differ).

## mcrun / mxrun — general & compile options

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

## mcrun / mxrun — parameters, scanning & optimisation

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

## mcrun / mxrun — simulation & instrument options

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
[&larr; back to overview](README.md)
