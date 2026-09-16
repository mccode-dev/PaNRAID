# Day 2 — Tuesday 22 September (Morning): Sources, Detectors & Optics

## Topic

Modelling of neutron and X-ray sources and detectors, and of the optical components (guides, monochromators) that sit between them — combined into a single morning session.

*Note: this session was originally scheduled as two separate half-days (Sources & Detectors in the morning, Optics in the afternoon); a scheduling change combined both into this single 09:00–12:00 morning block, so both the lecture slides and the hands-on exercises below are split into two shorter, focused sets rather than one merged set. The Tuesday afternoon is currently open.*

## Content

- How neutron and X-ray sources are characterised and modelled in McStas/McXtrace
- Detector simulation: types, response functions, and noise models
- Overview of optical elements — guides, mirrors, monochromators, collimators — and their role in shaping and conditioning a beam
- Understanding how sources, detectors and optics together influence the quality of experimental data
- Integrating source, detector and optical components into virtual setups to generate realistic datasets

## Learning Outcomes

By the end of this session, participants should be able to:

- Set up a basic virtual source in McStas or McXtrace
- Configure a detector component and interpret its output, including telling apart a genuine physical change from Monte Carlo noise, a binning choice, and a normalisation convention
- Assemble a simple optical element (a neutron guide, or an X-ray Bragg-crystal monochromator) and explain its effect on the beam
- Understand how source, detector and optical choices influence the quality — and potential biases — of simulated data intended for AI training

## Resources

**Sources and Monitors**
- [`McStas_McXtrace_Sources_and_Monitors.pptx`](./Sources_Monitors/McStas_McXtrace_Sources_and_Monitors.pptx) — lecture slides
- [`Exercises_Sources_and_Monitors.md`](./Sources_Monitors/Exercises_Sources_and_Monitors.md) — parallel McStas/McXtrace hands-on exercises for beginners

**Optics**
- [`McStas_McXtrace_Optics.pptx`](./Optics/McStas_McXtrace_Optics.pptx) — lecture slides [(PDF here)](./Optics/McStas_McXtrace_Optics.pdf)
- [`Exercises_Optics.md`](./Optics/Exercises_Optics.md) — McStas guide/gravity and McXtrace monochromator hands-on exercises
