# Seeking for AI: Realistic Datasets for Photons and Neutrons

*PaNRAID School · Supported by PEPR DIADEM*

**Objective**:
Explore how AI can leverage simulated photon and neutron datasets to solve inverse problems, optimize experiments, and train surrogate models.

---

## Why "Photons and Neutrons"?

### Shared Physics and Simulation Capabilities
- **Similar Interaction Processes**:
  - **Absorption**: Energy transfer to the material (e.g., photoelectric effect for X-rays, neutron capture).
  - **Scattering**:
    - *Elastic*: Structure analysis (e.g., Bragg diffraction for X-rays, neutron diffraction).
    - *Inelastic*: Dynamics analysis (e.g., Raman scattering for X-rays, neutron inelastic scattering).
  - **Decay**: Time-resolved studies (e.g., fluorescence, neutron activation).

- **Simulation Tools**:
  - **McStas**: Monte Carlo simulator for neutron scattering instruments.
  - **McXtrace**: Monte Carlo simulator for X-ray instruments.
  - Both enable realistic modeling of beamlines, detectors, and sample interactions.

- **Why Simulations Matter**:
  - **Realism**: Capture complex instrument geometries and material responses.
  - **Flexibility**: Test hypothetical setups or extreme conditions (e.g., high pressures, temperatures).
  - **Cost-Effective**: Avoid expensive trial-and-error on real instruments.

---

## Why Realistic AI Datasets?

### The Problem with Experimental Data
- **Lack of Annotations**:
  - Raw data often lacks metadata (e.g., sample composition, instrument settings).
  - Manual annotation is time-consuming and error-prone.
- **Publications as Implicit Annotations**:
  - Papers describe experimental conditions, but formats vary widely.
  - Not machine-readable or standardized for AI training.

### The Power of Simulated Data
- **Controlled Parameters**:
  - Every input (e.g., sample thickness, detector angle) is known and adjustable.
  - Outputs (e.g., scattering patterns, spectra) are directly linked to inputs.

- **Pipeline Workflow**:
  - Parameters → [Simulation (McStas/McXtrace)] → Virtual "Measurement"
  
  Example: Simulate a neutron scattering experiment with varying sample temperatures.

- **Inverse Problem**:
- **Goal**: Reconstruct input parameters from measured data.
- **AI Approach**:
  ```
  Measurement → [AI Algorithm (e.g., CNN, Bayesian Optimization)] → Parameters
  ```
- Example: Predict sample composition from a scattering pattern.

- **Surrogate Models**:
- **Purpose**: Replace slow simulations with fast AI models.
- **Pipeline**:
  ```
  Parameters → [AI Model (e.g., Neural Network)] → Virtual "Measurement" (1000x faster)
  ```
- **Use Case**: Real-time optimization of beamline configurations.

---

## General AI Methodology

### AI as a Universal Function Approximator
- **Black Box Concept**:
- Input (e.g., scattering pattern) → [AI Model] → Output (e.g., sample density).
- **Universal Approximation Theorem**: A neural network can approximate any continuous function given sufficient data and complexity.

- **General Behavior**:
- All AI methods (CNNs, RNNs, SVMs) follow the same principle: **map inputs to outputs via learned weights**.
- Differences lie in architecture, training efficiency, and interpretability.

### Training: The Core Process
- **Objective**: Minimize the **loss function** (e.g., Mean Squared Error, Cross-Entropy).
- **Loss Function**: Measures the difference between predicted and actual outputs.
- **Steps**:
1. **Forward Pass**: Compute predictions for a batch of training data.
2. **Loss Calculation**: Evaluate how far predictions are from true values.
3. **Backpropagation**: Compute gradients of the loss with respect to weights.
4. **Optimization**: Update weights using an optimizer (e.g., Adam, SGD).
- **Key Factors for Success**:
- **Data Quality**: High-fidelity simulations with diverse parameters.
- **Model Architecture**: Match complexity to the problem (e.g., CNNs for images, Transformers for sequences).
- **Hyperparameters**: Learning rate, batch size, number of epochs.

---

## What You Will Learn and Practice

### Hands-On Skills
1. **Setting Up Simulations**:
 - Configure beamlines/instruments in **McStas** (neutrons) and **McXtrace** (X-rays).
 - Define sample properties (e.g., crystal structure, composition).

2. **Characterizing Models**:
 - Analyze geometry (e.g., detector positions, slit sizes).
 - Extract parameters (e.g., resolution, flux) and results (e.g., spectra, diffraction patterns).

3. **Generating Datasets**:
 - Automate simulations across parameter ranges (e.g., vary temperature, pressure).
 - Output: Labeled datasets of `(input_parameters, virtual_measurements)`.

4. **Surrogate Modeling**:
 - Train AI models (e.g., neural networks) to mimic simulations.
 - **Example**: Replace a 1-hour simulation with a 1-second AI prediction.

5. **Solving Inverse Problems**:
 - Use AI to predict parameters from virtual/real measurements.
 - **Example**: Given a scattering pattern, estimate sample thickness and composition.

6. **Experimenting with Algorithms**:
 - Compare methods:
   - **Neural Networks**: High accuracy, requires large data.
   - **Gaussian Processes**: Uncertainty quantification, slower for large datasets.
   - **Random Forests**: Interpretable, robust to noise.

---

## What You Will Use (Resources)

### Tools and Infrastructure
- **Your Laptop**:
- Local development and testing.
- Run lightweight simulations (e.g., small McStas/McXtrace models).

- **Local Mini-Server**:
- Host datasets and share results with collaborators.
- Example: JupyterHub for interactive analysis.

- **Remote Computing Service**:
- **High-Performance Computing (HPC)**: Run large-scale simulations (e.g., clusters, cloud).
- **GPU Nodes**: Train deep learning models efficiently.

- **Your Brain**:
- Design experiments, debug models, and interpret results.
- Collaborate with peers to tackle complex problems.

---

## Summary and Next Steps

### Key Takeaways
- **AI + Simulations = Powerful Combination**:
- Simulations provide **realistic, labeled data** for training AI.
- AI enables **fast predictions** and **inverse problem-solving**.
- **Applications**:
- Optimize beamline designs.
- Accelerate material discovery (e.g., predict properties from scattering data).
- Reduce reliance on expensive experimental time.

### Next Steps for You
1. **Start Small**: Simulate a simple experiment (e.g., neutron diffraction from a known crystal).
2. **Generate Data**: Create a dataset with 100–1000 parameter combinations.
3. **Train a Model**: Use a neural network to predict parameters from simulated outputs.
4. **Validate**: Test the model on real experimental data (if available).
5. **Iterate**: Refine the model and expand to more complex problems.

---
## Thank You!

*Questions?*

**Contact**: Emmanuel Farhi · [Your Affiliation/Email]

*Supported by PEPR DIADEM and Partner Organizations*
