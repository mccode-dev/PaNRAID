# Starting point for imaging-exercise:

## Li-ion battery assemblies for Neutron and X-ray simulations

### Tasks:
* *McStas*: 
  * Pick either of `Tomorgrapy.instr` or `PSI_ICON.instr` from your
    `${MCSTAS}/examples` and build in the battery as a sample using `%include`. 
  * Perform a radiography in absorption contrast
  * Adapt the model to illustrate some aspect of charge/discharge
    using NCrystal `cfg` strings
  * Consider options for Bragg-edge imaging
  * Perform a CT
* *McXtrace*:
  * Build a tomography instrument from scratch or adapt the
    `Airport_scanner.instr`'
  * Build in the battery as a sample using `%include`. 
  * Perform radiography and CT
