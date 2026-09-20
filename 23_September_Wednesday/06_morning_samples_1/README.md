# Day 3 — Wednesday 23 September (Morning): Diffraction, Imaging, and SANS Samples

## Topic

Numerical modelling of neutron and X-ray samples for diffraction, imaging, and small-angle scattering applications.

## Content

- Introduction to numerical models of crystalline and polycrystalline samples
- Incorporating physical properties of materials (crystal structure, texture, strain) into simulations
- Simulation of diffraction experiments to generate realistic, labelled datasets
- Neutron and X-ray radiography of a Li-ion battery model
- Classification of simulated SANS form-factor data with a convolutional neural network

## Learning Outcomes

By the end of this session, participants should be able to:

- Build a basic sample model for powder or single-crystal diffraction in McStas/McXtrace
- Run a full virtual diffraction experiment from source to detector
- Compare neutron and X-ray contrast in a virtual imaging experiment
- Use generated NeXus data in a supervised-learning workflow

## Resources

- [`../McStas_McXtrace_Sample_Components.pptx`](../McStas_McXtrace_Sample_Components.pptx) — lecture slides (shared with the afternoon session) [(PDF here)](../McStas_McXtrace_Sample_Components.pdf)
- [`Exercises_PowderN.md`](./Exercises_PowderN.md) — McStas/McXtrace PowderN hands-on exercises (Debye-Scherrer rings, classic tables vs. NCrystal/CIF)
- [`hints`](./hints) — optional starter instruments for the PowderN exercises
- [`Batteries/README.md`](./Batteries/README.md) — McStas/McXtrace Li-ion battery imaging exercise (Union + NCrystal/xraylib, neutron vs. X-ray contrast, radiography and CT)
- [`SANS_inverse_problem/02_PyTorch_training.ipynb`](./SANS_inverse_problem/02_PyTorch_training.ipynb) — CNN classification of generated SANS form-factor NeXus data
- [`Facilitator_Notes.md`](./Facilitator_Notes.md) — setup and delivery notes for instructors
