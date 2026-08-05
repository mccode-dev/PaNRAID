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


### Instrument Parameters: 


### 
## Powder diffraction 

Regression for structural parameters: lattice parameters, occupancies, sizes or strain.

Phase classification from diffraction patterns.

We can also train a peak detection algorithm for the diffraction patterns, that give us the peak positions, widths, and intensities. 


## Imaging 

Segmentation: from the x-ray radiographies we could generate data for a U-Net, and segment (a bit time consuming). We could also train do detecto defects, or cracks, or pores, etc.

Binary Classification: presence and absense of something in the images. Detection*  


## Spectroscopy

regression problems 

Classification of samples, or elemental composition

Signal/background detection and estimation in spectra



