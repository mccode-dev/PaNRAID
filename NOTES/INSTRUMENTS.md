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



### SAXS / SANS

Multi-class Classification structure/form factor. This could be done from I(Q) or 2D images. We could select a subsample of all the SASmodels, like sphere, cylinder, core-shell, etc. 

SANS parameter regression: From I(Q), for a specific model, like core-shells, we could generate thousands of sample curves, and then learn the radius, polidispesity, shell thickness, correlation length, etc. 

#### `SANS_KWS2_AnySample.instr` 

##### Instrument Parameters: 

Parameter instruments can be varied, giving for variablity due to experimental setup. This can be seen as within variability for a specific sample and model. 

```bash
* lambda: [AA] Mean wavelength of neutrons
* dlambda: [AA]  Wavelength spread of neutrons
* sample: [int] type of sample, as 0=None, 1='AnySample', 2='Debye' or 3='Guinier'
* Clen: [m] distance to collimation in 0-20. Sample is at 40 m from source
* Dlen: [m] distance from sample to detector
* NGblen: [m] collimation width/height
* FLUX: [n/s/cm2/st] incoming neutron flux
```

##### Sample Parameters:

We can use all SAS models, but this would need a slight modification of the instrument component as it is. 

##### Output type 

- 2D Scattering plane

- 1D curve: PSD monitor radial sum

- 1D curve: PSD monitor radial average


### Powder diffraction 

  * McStas: `ILL_D20.instr` or `PSI_DMC.instr` 

Regression for structural parameters: lattice parameters, occupancies, sizes or strain.

Phase classification from diffraction patterns.

We can also train a peak detection algorithm for the diffraction patterns, that give us the peak positions, widths, and intensities. 

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


##### Output type

### Imaging 

Segmentation: from the x-ray radiographies we could generate data for a U-Net, and segment (a bit time consuming). We could also train do detecto defects, or cracks, or pores, etc.

Binary Classification: presence and absense of something in the images. Detection*  


### Spectroscopy

regression problems 

Classification of samples, or elemental composition

Signal/background detection and estimation in spectra



