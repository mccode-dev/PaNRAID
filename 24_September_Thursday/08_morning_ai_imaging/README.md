# Day 3 — Thursday 24 September (Morning): AI Image processing

*PaNRAID School, Day 4 morning — deconvolution, denoising, segmentation*

In this exercise, we aim to process some "measurement" data.

AI Processing: `Measurement` -> [ AI ] -> better `Measurement`

We process the simulated images from a simple SAXS mosdel to:
- deconvolve the instrument response by learning the difference between low and high resolution datasets.
- denoise detector images by learning how the noise evolves.
- segment areas in the detector image.

## Baseline

We here use a simple SAXS beam-line. the idea is to generate some detector images and learn some data processing methodologies. We use the `Test_SAXS` model. A similar neutron instrument exists. 

A single SAXS simulation step can be launched with e.g.:
```
mxrun --mpi=auto Test_SAXS.instr SAMPLE=0 Lambda=1.5 DLambda=0.01
```

The detector image is produced in `PSDMonitor.dat` which has a content such as:
```
# Format: McCode with text headers
# URL: http://www.mccode.org
# Creator: McXtrace 3.8.4 - Sep. 11, 2026
# Instrument: Test_SAXS.instr
# Ncount: 125000
# Trace: no
# Gravitation: no
# Seed: 1789562422628984
# Directory: Test_SAXS_20260916_144019
# Nodes: 8
# Param: DistanceFromSourceToFirstPinhole=0.05
# Param: DistanceFromSourceToSecondPinhole=0.7
# Param: DistanceFromSecondPinholeToSample=0.6
# Param: DistanceFromSampleToDetector=0.48
# Param: RadiusOfDetector=0.1
# Param: Lambda=1.5
# Param: DLambda=0.01
# Param: SAMPLE=0
# Param: Ncount=0
# Date: Wed Sep 16 14:40:32 2026 (1789562432)
# type: array_2d(20, 20)
# Source: Test_SAXS (Test_SAXS.instr)
# component: PSDMonitor
# position: 0 0 1.66
# title: PSD monitor
# Ncount: 1000000
# filename: PSDMonitor.dat
# statistics: X0=-1.30828e-05; dX=0.00496516; Y0=0.000113048; dY=0.00494267;
# signal: Min=3.09547e-20; Max=6.62394e-15; Mean=6.92573e-17;
# values: 2.77029e-14 5.95116e-16 294301
# xvar: X 
# yvar: Y 
# xlabel: X position [m]
# ylabel: Y position [m]
# zvar: I
# zlabel: Signal per bin
# xylimits: -0.0707107 0.0707107 -0.0707107 0.0707107
# variables: I I_err N
# Data [PSDMonitor/PSDMonitor.dat] I:
... an array ...
# Errors [PSDMonitor/PSDMonitor.dat] I_err:
... an array ...
# Events [PSDMonitor/PSDMonitor.dat] N:
... an array ...
```

What is useful for the AI is to get the detector image, as `Data [...] I:`.

You may extract such data with script:
```python
def load_psd_file(filepath):
    """Load a PSDMonitor.dat file and return as a 2D numpy array."""
    with open(filepath, 'r') as f:
        content = f.read()
    data_start = content.find('# Data [') + len('# Data [')
    data_start = content.find('] I:', data_start) + len('] I:')
    data_end = content.find('# Errors [')
    data_str = content[data_start:data_end].strip()
    data = np.fromstring(data_str, sep=' ')
    return data.reshape((200, 200))  # Assuming 200x200
    
# Example usage:
data = load_psd_file("PSDMonitor.dat")
```

--------------------------------------------------------------------------------
## A: Deconvolution (Super-Resolution)

Aim: Train a model to convert low-resolution SAXS images (default config) → high-resolution (improved config). We use a Supervised U-Net trained on pairs.

First generate a low-resolution set of detector images, and a high resolution set with e.g.
```
# Default config (low resolution)
mxrun -d low-res --mpi=auto Test_SAXS.instr -L SAMPLE=0,1,2,3,4,5,6,9,10,11 Lambda=1.5 DLambda=0.01 

# Improved config (high resolution, e.g., 2x distances)
mxrun -d high-res --mpi=auto Test_SAXS.instr -L SAMPLE=0,1,2,3,4,5,6,9,10,11 Lambda=1.5 DLambda=0.01 DistanceFromSourceToFirstPinhole=0.1 DistanceFromSourceToSecondPinhole=1.4 DistanceFromSecondPinholeToSample=1.2 DistanceFromSampleToDetector=0.96 -d high-res
```

Then we can grab the results and generate the `X`and `Y` datasets, e.g. 
- Load all `PSDMonitor.dat` files from `low-res/` and `high-res/`.
- Pair them by subdirectory index (e.g., `low-res/0/PSDMonitor.dat` ↔ `high-res/0/PSDMonitor.dat`).
- Convert them into normalized 2D numpy arrays for training.

Ask an AI to write such a data pre-processing script. It should actually extract:
```python
X_train, y_train = load_paired_data()
```

Then ask the AI to train a **U-Net** model with pytorch. 
The U-Net Architecture is an Encoder-decoder with skip connections.
It should define a class `class UNet(nn.Module)` with an `__init__` and `forward` methods. The data must be normalised to be properly handled.
Train the U-Net, and save the model, e.g.
```
model = UNet()
for epoch in range(100):
    model.train()
    ...
```

Now generate a new data set, e.g. with a different wavelength, model, wavelength spread... and deconvolve it with the model, e.g.:
```
deconvolved = deconvolve_psd("new_low_res/PSDMonitor.dat")
```

The deconvolution may be improved when converting the image to log-scale (before normalisation). 
This is also a way to retain small signals.
To get a model less dependant on the beam-line parameters, an image in Q-space is preferred.

--------------------------------------------------------------------------------
## B: Denoising (Noise2Noise)

We may use the **noise2noise** method to train the same U-Net to remove simulation noise. 
This is an unsupervised method that does not require clean data.

First, run the SAXS model with varying `ncount` and `seed`:
```
# Generate 100 noisy versions of SAMPLE=0 with varying NCOUNT and SEED
for i in {1..100}; do
  NCOUNT=$((10000 + i * 100))  # Vary NCOUNT
  SEED=$((1000 + i))           # Vary SEED
  mxrun --ncount $NCOUNT -s $SEED -d low-res/seed_${SEED}_ncount_${NCOUNT} --mpi=auto Test_SAXS.instr -L SAMPLE=0 Lambda=1.5 DLambda=0.01
done
```

The noise2noise method requires to _pair_ `PSDMonitor.dat` files from different NCOUNT/SEED dirs (noisy data) in order to infer the noise shape. 

Request an AI to import `PSDmonitor.dat` files from directory pairs, for all directories. 
Normaize the data.
Ask the AI to reuse the previous U-Net but train it to map moisy pairs.
Then use it th denoise data.

The denoising may be improved when converting the image to log-scale. 
This is also a way to retain small signals.
To get a model less dependant on the beam-line parameters, an image in Q-space is preferred.

This methodology is less efficient that the supervised deconvolution seen in section A, but it works even when no reference/clean data is available.

--------------------------------------------------------------------------------
## C: Segmentation

Segmentation is a method which identifies some areas in an image or volume.
OpenCV and Scikit-learn are two libraries of great use for this purpose.

Request an AI to produce a segmentation algorithm using log-scale intensity, and the Otsu thresholding to remove the lower background.

The methodology is basically a Log-scale adaptive thresholding + morphology analysis:
- Convert to log10 scale (compress dynamic range).
- Apply Otsu’s thresholding (or fixed threshold in log space).
- Clean with morphological operations (opening/closing shapes).
- Optional: Refine edges with Canny or watershed.

