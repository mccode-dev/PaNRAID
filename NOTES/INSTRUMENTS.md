## Candidate-instrument models 
_PW 2026/07/09 - Instrument models considered_

1. SAXS / SANS
  * McXtrace: `SOLEIL_SWING.instr` or `ESRF_BM29.instr`
  * McStas: `ISIS_SANS2d_Mantid.instr` or `FZJ_SANS_KWS2.instr` (latter needs adaptation)
2. Powder diffraction:
  * McXtrace: `MAXIV_DanMAX_pxrd2d.instr` or or `SOLEIL_DIFFABS.instr`
  * McStas: `ILL_D20.instr` or `PSI_DMC.instr`
3. Imaging:
  * McXtrace: `SOLEIL_ANATOMIX.instr` (nanoscale) or `Airport_scannerII.instr` (macro)
  * McStas: `PSI_ICON.instr`, `Sword_ODIN.instr`,
    `Radiography_Lithium_Battery.instr` 
4. Spectroscopy:
  * McXtrace: `SOLEIL_MARS` or `SOLEIL_ROCK`
  * ~~McStas: `ILL_IN20` or `SNS_ARCS` (relevant sample...?!)!~~

Class | Instrument     | Eligibility | Adaption
------|------------------------|-----|---------
SANS  | `ISIS_SANS2d_Mantid`   | NO  | (Nexus)
SANS  | `SANS_KWS2_AnySample`  | YES | Fixed parameters. Must parametrise Sphere/Guinier/Debye.
SAXS  | `SOLEIL_SWING`         | YES | Use a PDB set to infer e.g. chemical composition. Or change to Sphere/Cyl/Shell/Nanodisc. Can be used for instr optimisation.
SAXS  | `ESRF_BM29`            | YES | Fixed parameters. Should parametrise gyration radius (sphere).
DIFN  | `templateDIFF` (D20)   | YES | Uses PowderN CIF. Can be trained on Bravais class. Can optimise monochromator curvature.
DIFN  | `PSI_DMC`              | YES | Uses PowderN CIF. Can be trained on Bravais class.
DIFX  | `MAXIV_DanMAX_pxrd2d`  | YES | Uses PowderN CIF. Can be trained on Bravais class.
DIFX  | `SOLEIL_DIFFABS`       | YES | Uses PowderN CIF + Fluo. Can be trained on Bravais class and spectroscopy stoichiometry. Can be used to optimise mirror curvatures.
IMGN  | `PSI_ICON`             | NO  | Nothing is parametrised. sample is fixed. Could still be used for de-noising.
IMGN  | `Radiography_Sword`    | NO  | Using Union. Fixed geometry. Nothing parametrised. Could still be used for de-noising.
IMGN  | `Radiography_Lithium_Battery` | NO | Using Union. Fixed geometry. Nothing parametrised. Could still be used for de-noising.
IMGX  | `SOLEIL_ANATOMIX`      | YES | Flexible geometry. Can be trained for position/angle and geometry.
IMGX  | `Airport_scannerII`    | YES | Many OFF/PLY objects. These could be displaced for segmentation training vs composition, angle and positions.
INS   | `templateTAS` (IN20)   | YES | Can be used for parameter optimisation (monok, analyser).
INS   | `SNS_ARCS`             | YES | May be used to study instrument resolution. But do not know how to use that for AI. Perhaps de-convolution ?
XRF   | `SOLEIL_MARS`          | YES | Uses PowderN CIF + Fluo. Can be trained on Bravais class and spectroscopy stoichiometry. same as `DIFFABS` in structure.
ABSX  | `SOLEIL_ROCK`          | YES | Uses Fluo. Can be trained on X-ray absorption energy on edge.

---------------------------------------------------------------------------------

### SAXS / SANS

Multi-class Classification structure/form factor. This could be done from I(Q) or 2D images. We could select a subsample of all the SASmodels, like sphere, cylinder, core-shell, etc. 

SANS parameter regression: From I(Q), for a specific model, like core-shells, we could generate thousands of sample curves, and then learn the radius, poly dispersity, shell thickness, correlation length, etc. 


#### `ISIS_SANS2d_Mantid.instr`

Needs NeXus ... Should we use this one? Probably **NO**.

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| L1 | m | Variable distance from 1st to 2nd variable slit | 3.926 |
| A1w | m | Width of first collimation slit, rectangular slit | 0.030 |
| A1h | m | Height of first collimation slit, rectangular slit | 0.02 |
| S6 | m | Radius of slit S6 (last of the optis slits) | 0.006 |
| A2 | m | Radius of second collimation slit, circular slit | 0.006 |
| Lmin | AA | Minimum wavelength to produce at the source | 1 |
| Lmax | AA | Maximum wavelength to produce at the source | 14 |
| model_nr |  | SANS_benchmark2 SANS sample nr. E.g. 5: sphere(r=50AA), 15: sphere(r=150AA) | 15.0 |


#### `SANS_KWS2_AnySample.instr` 

##### Instrument Parameters: 
Parameter instruments can be varied, giving for variability due to experimental setup. This can be seen as within variability for a specific sample and model. 

| Name | Unit | Description | Default |
|------|------|-------------|---------|
| lambda | AA | Mean wavelength of neutrons | 7.0 |
| dlambda | AA | Wavelength spread of neutrons | 0.7 |
| FLUX | n/s/cm2/st | incoming neutron flux | 1e8 |
| NGblen | m | collimation width/height | 0.05 |
| sample | int | type of sample, as 0=None, 1='AnySample', 2='Debye' or 3='Guinier' | 0 |
| Clen | m | distance to collimation in 0-20. Sample is at 40 m from source | 10.0 |
| Dlen | m | distance from sample to detector | 10.0 |

Not many instrument parameters that can be used for AI.

##### Sample Parameters

We can use all SAS models, but this would need a slight modification of the instrument component as it is. 
Can be made parametrised with little modifications.

- `SANS_AnySamp`: hard-coded I(q) in INIT (Sphere). Currently with fixed parameters.
- `SANS_DebyeS`: Currently with fixed parameters.
- `SANS_Guinier`: Currently with fixed parameters.

##### Output type 

- 2D: xy image `PSD_monitor`
- 1D: I(q) curve: PSD monitor radial sum `PSD_monitor_rad`
- 1D: I(q) curve: PSD monitor radial average `PSD_monitor_rad`


#### `SOLEIL_SWING.instr`

##### Instrument Parameters:
```
* E0:             [keV]  Nominal energy at the Wiggler.
* dE:             [keV]  Energy half-bandwidth at the Wiggler
* dcm_theta:      [deg]  Rotation angle of the DCM. 0=set from energy E0
* mirror_grazing_angle: [deg] Tilt angle of the mirrors.
* hfm_radius:       [m]  Horizontally focusing mirror radius.
* vfm_radius:       [m]  Vertically focusing mirror radius.
* sample:         [str]  Sample given as a PDB file, or NULL for a 100A dilute Sphere model.
* sample_det:       [m]  Sample to detector distance in m.
```

Can be used to optimise mirror curvatures.

##### Sample Parameters

No sample parameters, using 'SAXSPDBFast'. 

PDB file not easy to train, but we could select some PDB from https://www.wwpdb.org/ and train against e.g. `_chem_comp.formula` ? 
Not sure this is relevant, but this way a model could infer the compound formula in a limited set of atoms (CNHOFClSP).

Could also be adapted to use a static parametrised sample model, e.g. sphere, cylinders, shells, nanodiscs.

##### Output type

- 2D: image 'Monitor_nD'
- 1D: I(q) 'SAXSQMonitor'

#### `ESRF_BM29.instr`

##### Instrument Parameters:
```
* DistanceFromSourceToFirstPinhole: [m]    Distance to first pinhole from source.
* DistanceFromSourceToSecondPinhole: [m]   Distance to second pinhole - used for focussing rays.
* DistanceFromSecondPinholeToSample: [m]   Collimation length.
* DistanceFromSampleToDetector: [m]        Sample-detector-distance.
* RadiusOfDetector: [m]                   Radius of the circular detector.
* Lambda: [AA]                             Wavelength of the rays emitted from source.
* DLambda: []                              Relative deviation of wavelength of the rays emitted from source.
```

Not many instrument parameters that can be used for AI.

##### Sample Parameters

Fixed sample 'SAXSSpheres' with fixed gyration radius. Can be made parametrised.

##### Output

- `SAXSQMonitor`: 1D I(q)


---------------------------------------------------------------------------------

### Powder diffraction 

Regression for structural parameters: lattice parameters, occupancies, sizes or strain.

Phase classification from diffraction patterns.

We can also train a peak detection algorithm for the diffraction patterns, that give us the peak positions, widths, and intensities. 


#### `ILL_D20.instr` (templateDIFF)

Found `templateDIFF` which refers to D20.

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| lambda | Angs | Wavelength at monochromator, computed from DM and THETA_M if left as 0. | 1 |
| DM | Angs | d-spacing of monochromator, computed from lambda and THETA_M if left as 0. | 3.355 |
| Powder | str | File name for powder description | "Na2Ca3Al2F14.laz" |
| RV | m | Monochromator vertical curvature, 0 for flat, -1 for automatic setting | -1 |
| L1 | m | Source-Monochromator distance | 17 |
| L2 | m | Monochromator-Sample distance | 3.2 |
| L3 | m | Sample-Detector distance | 1.471 |
| ALPHA1 | min | Horizontal collimator divergence for L1 arm (before monochromator) | 5 |
| ALPHA2 | min | Horizontal collimator divergence for L2 arm (monochromator-sample) | 60 |
| ALPHA3 | min | Horizontal collimator divergence for L3 arm (sample-detector) | 5 |
| ETA | min | Monochromator horizontal mosaic (gaussian) | 12 |
| verbose | int | Print DIF configuration. 0 to be quiet | 1 |
| THETA_M | deg | Monochromator take-off angle, computed from lambda and DM if left as 0. | 0 |
| SM | int | Scattering sense of beam from Monochromator. 1:left, -1:right | 1 |

Could also be use to demonstrate instrument optimisation, e.g. curvature RV.

##### Sample Parameters

Sample is PowderN. Can use CIF. Train on Bravais class ?

##### Output

- 1D: I(theta) `Monitor_nD`
- 2D: I(theta,y) `Monitor_nD`

#### `PSI_DMC.instr`

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| lambda | AA | Choice of wavelength, affects both monochromator and source component | 2.5666 |
| R | 1 | Reflectivity of non-curved guides | 0.87 |
| R_curve | 1 | Reflectivity of curved guides | 0.87 |
| filename | str | Choice of reflection list file, e.g. from McStas data dir | "Na2Ca3Al2F14.laz" |
| D_PHI | deg | Focusing 'd_phi' for PowderN, see mcdoc page | 6 |
| SHIFT | deg | Rotation of detector, set to 0.1 to displace by half a bin | 0 |
| PACK | 1 | Powder packing factor | 0.7 |
| Dw | 1 | Powder Debye-Waller factor | 0.8 |
| BARNS | 1 | Flag to define if powder reflection file \|F2\| is in Barns or fm | 1 |
| SPLITS |  |  | 58 |

Not many instrument parameters that can be used for AI.

##### Sample Parameters

Sample is PowderN using CIF. Can be trained on Bravais class.

##### Output type

- 2D: I(theta,y) `Monitor_nD`

#### `MAXIV_DanMAX_pxrd2d.instr`

##### Instrument Parameters:
```
* E0: [keV]        The central energy to sample from source model.
* DE: [keV]        Spectral width (std. dev. if gaussian source) to sample from source model.
* undDetune: [eV]  First harmonic detuning in eV. When zero - max flux on axis. If set to approx. 4 eV one can gain ~20% of flux through the aperture.
* undK: [ ]        Undulator K parameter, overrides E0.
* oh_premonoh: [m] Pre-mono (white beam) slit height.
* oh_premonow: [m] Pre-mono (white beam) slit width.
* oh_endh: [m]     OH exit slit height.
* oh_endw: [m]     OH exit slit width.
* PXRDsampleap_h: [m] PXRD clean-up aperture height.
* PXRDsampleap_w: [m] PXRD clean-up aperture width.
* DMM_angle: [deg] Glancing angle of the ML.
* DCM_angle: [deg] Glacing angle of the Si-111 monochromator crystals.
* DCM: [ ]         If nonzero the high-resolution SI DCM is active.
* DCM_e0: [keV]    The energy to tune the Si monochromator to. May be different from E0. If 0 the DCM is controlled by DCM_angle.
* DMM: [ ]         If nonzero the multilayer mono is active.
* DMM_e0: [keV]    The energy to tune the ML monochromator to. May be different from E0. If 0 the DMM is controlled by DMM_angle.
* OH_2DCRL_N: [ ]  Number of 2D focus CRLs in the optics hutch transfocator. 0 means transfocator is inactive.
* pxrd_2d_tthc: [ ] Rotation around the sample tube (i.e. the x-axis) of the 2d-area detector arm.
* pxrd_2d_y: [m]   Offset of 2d-area detector centre perpendicular to the detector arm.
* debugMon: [ ]    If nonzero, all intermediate monitors appear for debugging purposes.
* beamStop: [ ]    If nonzero, a beamstop is in between sample and PXRD 2d-detector.
* SPLITS: [ ]      Split-number at the sample position.
* sample_radius: [m] Powder sample cylinder radius
```

Not many instrument parameters that can be used for AI.

##### Sample Parameters

Sample is PowderN. Can be used to train CIF sample Bravais class.

##### Output type

- 2D xy image

#### `SOLEIL_DIFFABS.instr`

Mixed diff/fluo (spectroscopy).

##### Instrument Parameters:
```
* E0:       [keV]  Central energy of the interval to be looked at
* dE:       [keV]  Half-width     of the energy interval
* M1_angle: [mrad] Rotation angle of M1/M2 mirrors. When left as 0, it is set automatically from E0.
* M1_radius:[m]    Curvature radius of M1 mirror (Rh, 1300x100) longitudinal. Positive=mirror is focusing. 0=flat.
* M2_radius:[m]    Curvature radius of M2 mirror (Rh, 1300x100) sagittal. Positive=mirror is focusing. 0=flat.
* DCM_theta:[deg]  Rotation angle of DCM crystals. When left as 0, it is set automatically from E0.
* sample:   [str]  Sample structure file, LAU/CIF format.
```

Can be used to optimise mirror curvatures.

##### Sample Parameters

Using CIF2HKL in 'PowderN+Fluorescence'. We could train with classes from Bravais classes.
Need to select some files from e.g. Crystallography.net, create classes, and train with corresponding CIF.

##### Output type

- 1D: I(theta) 'Monitor_nD'
- 2D: I(theta,y) banana 'Monitor_nD'

---------------------------------------------------------------------------------

### Imaging / tomography

* Segmentation: from the x-ray radiographies we could generate data for a U-Net, and segment (a bit time consuming). We could also train to defects, or cracks, or pores, etc.

Binary Classification: presence and absence of something in the images. Detection

De-noising possibility low vs high quality images and learning mappings.


#### `PSI_ICON.instr`

probably not usable. Nothing is parametrised.

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| lambda_min | AA | Minimum wavelength on wavelength monitors | 0.3 |
| lambda_max | AA | Maximum wavelength on wavelength monitors | 10.0 |
| eventmode | 1 | Flag to store neutron events with calculated sample-detector travel | 0 |
| nx | 1 | Number of x-pixels, camera | 512 |
| ny | 1 | Number of y-pixels, camera | 512 |
| Lambda_Min | AA | Minimum wavelength produced from source | 4.1 |
| Lambda_Max | AA | Maximum wavelength produced from source | 10 |
| sp | m | Overall goniometer z-position wrt. camera | 0 |
| tx | m | Goniometer x-translation | 0 |
| ty | m | Goniometer y-translation | -0.0075 |
| tz | m | Goniometer z-translation | 0 |
| rx | m | Goniometer x-rotation | 0 |
| ry | m | Goniometer y-rotation | 0 |
| rz | m | Goniometer z-rotation | 0 |
| delta_eps | m | Finite distance separating metal-slabs in sample | 1e-9 |
| delta_y | 1 | Size-factor between slabs of Zr and Al | 0.1 |

##### Sample Parameters

A set of 'Refractor' components. Fixed geometry.

##### Output type

- 2D: many !!

#### `Sword_ODIN.instr` (`Radiography_Sword`)

Found Radiography_Sword

##### Instrument Parameters:
```
* chopper_mode:              [1] Choose between 6 different chopper modes from 0 to 5. Chooper mode 5 is a white beam.
* Lambda:                   [AA] Choose a specific wavelength 1AA-10AA to use in the simulation. The wavelength must correspond to choosen chopper mode. Lambda=0 means that all wavelengths permitted by the chopper mode are used.
* Sample:                    [0] Choose if the sample is pressent in the simulation or not, Sample=0: not in the beam, Sample=1: sample is in the beam.
* pinhole_diameter:          [m] Diameter of the pinhole. Allowed sizes are 0.01-0.1m.
* pinhole_detector_distance: [m] Distance between the pinhole and the detector. Allowed distances are 10m-25m.
* pinhole_sample_distance:   [m] Distance between the pinhole and the sample. Allowed distances are between 1-25m.
* X_sample_pos:              [m] Translation of sample in x-direction.
* Y_sample_pos:              [m] Translation of sample in x-direction.
* angle:                   [deg] Sample-stage rotation (around y).
* Zoom:                      [1] Detector zooom: Reduce area and increase resolution detector by the same fact. Values between 1 and 10.
```

No easy parameter to train. 

##### Sample Parameters

Fixed sample (Union).

##### Output type

- 2D: image `PSD_monitor_Filter`

#### `Radiography_Lithium_Battery.instr` 

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| D | m | Diameter of pinhole before sample | 0.01 |
| L | m | Distance between pinhole and sample | 5 |
| l | m | Distance between sample and detector | 0.10 |
| sample_used | 1 | Flag to indicate if battery stack sample (0) or single-slab calibration sample (1) is in the beam | 0 |
| battery_charge | 1 | Level of charge of battery (Currently not functional!) | 1.0 |

No easy parameter to train. 

##### Sample Parameters

Fixed sample (Union).

##### Output type

- 2D: image `PSD_monitor`

#### `SOLEIL_ANATOMIX.instr` (nanoscale) 

coil 

##### Instrument Parameters:
```
* E0:    [keV] Energy selected at the Undulator.
* Emono: [keV] Energy selected at the monochromator. When 0, it is set to E0.
* dE:    [keV] Energy spread at the Undulator.
* ANGLE: [deg] Rotation angle of the sample stage.
* sample:[str] Sample geometry file, OFF/PLY format.
```

No easy parameter to train. 

##### Sample Parameters

Using `Filter` with Ge material. Geometry is OFF/PLY.

##### Output type

- 2D: image `PSD_monitor`

#### `Airport_scannerII.instr` (macro)

##### Instrument Parameters:
```
* SFILE: [ ]    Name of file that contains the off/ply parameters for the scene
* ANGLE: [ ]    Rotation around y-axis
* posX: [m]     Displacement of scene along x-axis
* posY: [m]     Displacement of scene along y-axis
* posZ: [m]     Displacement of scene along z-axis
* Ncount: [1]   Set X-ray particle count for the simulation (same as -n #)
```

No easy parameter to train. 

##### Sample Parameters

Using `Abs_objects` with many OFF/PLY objects. These could be displaced for segmentation training vs composition, angle and positions.

##### Output type

- 2D: image `PSD_monitor`


---------------------------------------------------------------------------------

### Spectroscopy

regression problems 

Classification of samples, or elemental composition.

Signal/background detection and estimation in spectra


#### `ILL_IN20` (templateTAS)

Typical 3 axis spectrometer.

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| KF | Angs-1 | Outgoing neutron wavevector | 3 |
| KI | Angs-1 | Incoming neutron wavevector | 0 |
| QM | Angs-1 | Wavevector transfer in crystal | 0.5 |
| EN | meV | Energy transfer in crystal | 0 |
| verbose | 1 | print TAS configuration. 0 to be quiet | 1 |
| WM | m | Width of monochromator | 0.20 |
| HM | m | Height of monochromator | 0.19 |
| RMH | m | Monochromator horizontal curvature, 0 for flat, -1 for automatic setting | -1 |
| RMV | m | Monochromator vertical curvature, 0 for flat, -1 for automatic setting | -1 |
| DM | Angs | Monochromator d-spacing | 3.155 |
| NHM | 1 | Number of horizontal slabs composing the monochromator | 15 |
| NVM | 1 | Number of vertical slabs composing the monochromator | 15 |
| WA | m | Width of analyzer | 0.16 |
| HA | m | Height of analyzer | 0.08 |
| RAH | m | Analyzer horizontal curvature, 0 for flat, -1 for automatic setting | -1 |
| RAV | m | Analyzer vertical curvature, 0 for flat, -1 for automatic setting | -1 |
| DA | Angs | Analyzer d-spacing | 3.155 |
| NHA | 1 | Number of horizontal slabs composing the analyzer | 15 |
| NVA | 1 | Number of vertical slabs composing the analyzer | 15 |
| L1 | m | Source-Monochromator distance. Contains 1st Collimator of length 5.34 | 2.33 |
| ALF1 | arc min | Horizontal collimation from Source to Monochromator | 60 |
| ALF2 | arc min | Horizontal collimation from Monochromator to Sample A | 60 |
| ALF3 | arc min | Horizontal collimation from Sample to Analyzer | 60 |
| ALF4 | arc min | Horizontal collimation from Analyzer to Detector | 60 |
| BET1 | arc min | Vertical collimation from Source to Monochromator | 120 |
| BET2 | arc min | Vertical collimation from Monochromator to Sample A | 120 |
| BET3 | arc min | Vertical collimation from Sample to Analyzer | 120 |
| BET4 | arc min | Vertical collimation from Analyzer to Detector | 120 |

Can be optimised for e.g curvatures (monok, analyser).

##### Sample Parameters

Using `Isotropic_Sqw` which allows any structural and dynamic stuff. Probably too complex for the sample side.

##### Output type

- 2D: image `PSD_monitor` very small in xy space. Moves around (requires scans).

#### `SNS_ARCS` (relevant sample...?)

##### Instrument Parameters:
| Name | Unit | Description | Default |
|------|------|-------------|---------|
| filename |  |  | "source_sct521_bu_17_1.dat" |
| Fermi_nu | Hz | Frequency of the Fermi chopper | 420 |
| T0_nu | Hz | Frequency of the T0 chopper | 90 |
| nrad | m | Radius of the Fermi chopper blades | 0.58 |
| nchans | 1 | Number of channels in the Fermi chopper | 40 |
| Edes | meV | Desired/target energy | 50 |
| Et | meV | Energy transfer of the Spot_sample | 25 |
| ttheta | deg | Scattering angle of the Spot_sample | 25 |
| T0_off |  |  | 0 |
| sxmin | m | Sample slit horz min value | -0.04 |
| sxmax | m | Sample slit horz max value | 0.04 |
| symin | m | Sample slit vert min value | -0.04 |
| symax | m | Sample slit vert max value | 0.04 |
| run_num | 1 | Virtual source run number (unused at present) | 1 |

##### Sample Parameters

Using `Spot_sample` which provides the resolution function (N-Dirac).
Not sure what can be used for training.

##### Output type

- 2D: image `Monitor_nD` large detector in (theta,y).


#### `SOLEIL_MARS`

##### Instrument Parameters:
```
* E0: [keV]     Central energy to be emitted by the source
* dEr: [1]    Relative half width to emitted by the source, e.g. 1e-4
* alpha: [deg]  Asymmetry angle for the crystals.
* reflections: [str] Sample structure file, LAU/CIF format.
* reflec_material_M12: [str] reflecting coating on curved mirrors, e.g. Pt
```

Same as `DIFFABS` in structure. Less parameters.

##### Sample Parameters

Uses PowderN CIF + Fluo. Can be trained on Bravais class and spectroscopy stoichiometry. 

##### Output type

- 1D: I(theta) 'Monitor_nD'
- 2D: I(theta,y) banana 'Monitor_nD'

#### `SOLEIL_ROCK`

##### Instrument Parameters:
```
* E0:               [keV]    Energy to hit, i.e. selected by the channel-cut monochromator
* dE:               [keV]    Energy spread at the source
* cc:               [0-3]    Channel-cut monochromator type. 0 for Si 220 with an energy range of  5.62883-46.2834 eV/4-35 deg (hit-table:11.752-34.055 ev/5.44-15.94 deg); 1 for Si 111 long 3.44694-28.3427 eV/4-35 deg (hit-table:7.196-20.854 ev/5.44-15.94 deg); 2 for Si 111 short 3.44694-18.914.3 eV/6-35 deg (hittable:5.323-18.914 ev/6-21.8 deg); 3 changes cc dynamically
* scan:             [0-1]    0 no energy scan, 1 energy scan
* angle_m2a_m2b:    [rad]    M2A/M2B mirror's deviation angle, can vary from 0.0035 to 0.0104
* angle_m1:         [rad]    M1 mirror's deviation angle
* sample_file:      [string] Sample chemical formulae
* reflec_material_M1:      [str] Material reflectivity file name for M1 mirror, e.g. "Ir.dat"
* reflec_material_M2A_M2B: [str] Material reflectivity file name for M2A and M2B mirror. Use NULL for automatic setting.
```

Nothing to optimise here.

##### Sample Parameters

Uses Fluo component. Can be trained on X-ray absorption energy on edge.

##### Output type

- 1D: energy 'Monitor_nD'
- 2D: XY 'Monitor_nD'

