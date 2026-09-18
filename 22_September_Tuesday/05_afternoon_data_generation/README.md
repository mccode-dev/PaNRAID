# Day 2 — Tuesday 22 September (Afternoon): Dataset Generation - SANS

*PaNRAID School, Day 3 afternoon — SANS data gereration*

## Aim

Think about the scientific purpose first, then plan and generate a large simulation dataset for another McStas instrument of your choice or for your own instrument. Use the provided HPC resources when the required coverage or neutron count makes local generation impractical.

Your project should justify the AI task, inputs, targets, nuisance variables, parameter bounds, sampling design, class balance, fidelity, storage estimate, validation rules, leakage-safe splits, and success criteria.

Begin with a small smoke test, benchmark representative simulations, estimate CPU-hours and storage, and only then submit the full campaign.

Preserve the instrument source, manifest, seeds, environment information, SLURM scripts, logs, validation reports, and dataset version so another student/person can reproduce the result.

## Here you go

To start the exercise, refer to:

- [01_dataset_generation.ipynb](./01_dataset_generation.ipynb)
- [02_PyTorch_training.ipynb](./02_PyTorch_training.ipynb)

which uses the following McStas instruments and components:

- [kws_core_shell.instr](./kws_core_shell.instr)
- [kws_linear_pearls.instr](./kws_linear_pearls.instr)
- [kws_sphere.instr](./kws_sphere.instr)
- [Tslit.comp](./Tslit.comp)
- [TBeamstop.comp](./TBeamstop.comp)


