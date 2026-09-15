# Day 4 — Wednesday 24 September (Morning): ML Optimization

*PaNRAID School, Day 4 morning — optimization*

For this exercise, we shall use an existing model, and search to optimize its parameters to get better flux and resolution.

The **DIFFABS beamline** at Synchrotron SOLEIL is designed for **combined X-ray diffraction and absorption studies**. It covers an energy range of **3–23 keV** and is optimized for:

- **High flux** at the sample.
- **Low divergence** for high-resolution experiments.
- **Micro-focusing** using KB mirrors (not modeled here, but M1/M2 can be tuned for similar effects).

## DIFFABS Key Components

| Component        | Role                                                                                | Parameters to Optimize                                 |
| ---------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **BM D13-1**     | Bending magnet source (B=1.71 T, critical energy 8.6 keV).                          | None (fixed source properties).                        |
| **Primary Slit** | Collimates the beam.                                                                | `xwidth`, `yheight` (fixed).                        |
| **M1 Mirror**    | Vertically focuses the beam onto the DCM. Coated with Rh/Si.                        | `M1_radius` (curvature), `M1_angle` (incidence angle). |
| **DCM**          | Double Crystal Monochromator (Si 111) for energy selection and horizontal focusing. | `DCM_theta` (Bragg angle).                             |
| **M2 Mirror**    | Horizontally focuses the beam onto the sample. Coated with Rh.                      | `M2_radius` (curvature).                               |
| **Sample Stage** | Hosts the sample and detectors (PowderN, Fluorescence, XRD).                        | None.                                                  |


## Optimization Goals

1. **Maximize intensity** at the sample (`sample_stage` monitor).
2. **Minimize beam spot size** (narrower `dX` and `dY` at the sample).
3. **Balance trade-offs**: Higher curvature can focus the beam but may reduce flux due to reflectivity or acceptance.

## Optimization Tools

The optimization can be triggered from the GUI (for simple cases), as well as from the command line (with more flexibility).

```
mxrun/mcrun Instr params={min,max|min,guess,max}...
    --optimize          Optimize instrument variable parameters to maximize
                        monitors
    --optimize-maxiter=optimize_maxiter
                        Maximum number of optimization iterations to perform.
                        Default=1000
    --optimize-tol=optimize_tol
                        Tolerance for optimization termination. When optimize-
                        tol is specified, the selected optimization algorithm
                        sets some relevant solver-specific tolerance(s) equal
                        to optimize-tol
    --optimize-method=optimize_method
                        Optimization solver in ['powell', 'nelder-mead', 'cg',
                        'bfgs', 'newton-cg', 'l-bfgs-b', 'tnc', 'cobyla',
                        'slsqp', 'trust-constr', 'dogleg', 'trust-ncg',
                        'trust-exact', 'trust-krylov'] (default: powell) You
                        can use your custom method method(fun, x0, args,
                        **kwargs, **options). Please refer to scipy
                        documentation for proper use of it: https://docs.scipy
                        .org/doc/scipy/reference/generated/scipy.optimize.mini
                        mize.html?highlight=minimize
    --optimize-eval=optimize_eval
                        Optimization expression to evaluate for each detector
                        "d" structure. You may combine: "d.intensity" The
                        detector intensity; "d.error"     The detector
                        intensity uncertainty; "d.values"    An array with
                        [intensity, error, counts]; "d.X0 d.Y0"   Center of
                        signal (1st moment); "d.dX d.dY"   Width  of signal
                        (2nd moment). Default is "d.intensity". Examples are:
                        "d.intensity/d.dX" and "d.intensity/d.dX/d.dY"
    --optimize-minimize
                        Choose to minimize the monitors instead of maximize
    --optimize-monitor=optimize_monitor
                        Name of a single monitor to optimize (default is to
                        use all)
```

## Step 1: Run a Baseline Simulation

Load the McXtrace simulation model from the File menu. On the neutron side, you may experiment with the `Templates/templateDIFF.instr` diffractometer model, and aim to optimize its monochromator vertical curvature `RV`.

Run a simulation with default parameters. Inspect the `sample_stage` monitor output file, and search for metadata:
  - `intensity`: Total counts at the sample.
  - `dX`, `dY`: Beam width and height (standard deviation).
  
## Step 2: Simple Optimization

Re-run, and this time, select the 'Optimize' simulation mode. 
Choose the `sample_stage` monitor in the *Inspect* drop-down list.
Indicate the parameters to optimize by setting their variation range, e.g. `M1_radius=1000,1800` and `M2_radius=1000,1800`.
Press 'Run' and wait for completion. 

:warning: the MPI option seems broken with optimization, do *not* use parallel computing. This can be long, e.g. 10 steps/minute for a total of 180 steps, i.e. ~15 minutes. 

You should get something like (here with `M1_radius` optimization only):
```
mxrun --optimize --optimize-monitor=sample_stage  SOLEIL_DIFFABS.instr E0=13 M1_radius=1000,1800
...
Optimization terminated successfully.
         Current function value: -25005700000.000000
         Iterations: 5
         Function evaluations: 178
INFO: Parameter uncertainties:

INFO: M1_radius = 1494.447391 ± 209.535869
```

Plot results and estimate best parameters. Do you think this is satisfactory ? Why ?

## Step 3: Advanced Optimization

NOTE: this step can be started while the previous one is still running.

The metric to optimize can be defined either directly as a monitor in the model (and then we search for its maximum value), or can combine metadata from specific monitor(s). 
In our case, the `mxrun`/`mcrun` command allows to set the monitor and its value to maximize with the `--optimize-eval` option. 
At least one fixed parameter must be specified (here we use `E0`).

Open a terminal from the File menu, and start the optimization:
```
mxrun --optimize --optimize-monitor=sample_stage --optimize-eval=d.intensity/d.dX/d.dY SOLEIL_DIFFABS.instr E0=13 M1_radius=1000,1800 M2_radius=1000,1800
```

This time, the intensity reaching the monitor is scaled with the inverse widths, which is quite common to maximize brightness.

Plot results and estimate best parameters. Is this better ?


