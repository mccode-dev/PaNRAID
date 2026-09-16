# Day 3 — Thursday 24 September (Morning): AI Image processing (solution)

*PaNRAID School, Day 4 morning — deconvolution, denoising, segmentation*

In this exercise, we use the `Test_SAXS` model. A similar neutron instrument exists. 
We process the simulated images to:
- deconvolve the instrument response by learning the difference between low and high resolution datasets.
- denoise detector images by learning how the noise evolves.
- segment areas in the detector image.

--------------------------------------------------------------------------------
# A: Deconvolution (Super-Resolution)

Train a model to convert low-resolution SAXS images (default config) → high-resolution (improved config).

## A1: Run reference data

We first need to generate some low and high resolution datasets. We suggest to simply extend the distances before the sample, so that the beam is more focused, which improves spatial resolution.

Run the simulations with e.g. (adapt the high res distances at will).

```
# Default config (low resolution)
mxrun -d low-res --mpi=auto Test_SAXS.instr -L SAMPLE=0,1,2,3,4,5,6,9,10,11 Lambda=1.5 DLambda=0.01 

# Improved config (high resolution, e.g., 2x distances)
mxrun -d high-res --mpi=auto Test_SAXS.instr -L SAMPLE=0,1,2,3,4,5,6,9,10,11 Lambda=1.5 DLambda=0.001 DistanceFromSourceToFirstPinhole=0.1 DistanceFromSourceToSecondPinhole=1.4 DistanceFromSecondPinholeToSample=1.2 DistanceFromSampleToDetector=0.96 -d high-res
```

You may as well vary the wavelength `Lambda` and `DLambda` with e.g. the `-M -L` options: 
```
mxrun -M -L SAMPLE=0,1,2,3,4,5,6,9,10,11 Lambda=0.5,0.7,0.9,1.1,1.3,1.5,1.7,1.9
```

## A2: Extract low-res and high-res data

This `load_paired_data` script:
- Loads all PSDMonitor.dat files from low-res/ and high-res/.
- Pairs them by subdirectory index (e.g., low-res/0/PSDMonitor.dat ↔ high-res/0/PSDMonitor.dat).
- Converts them into normalized 2D numpy arrays for training.


```python
import numpy as np
import glob
import os

def load_psd_file(filepath):
    """Load a PSDMonitor.dat file and return as a 2D numpy array."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Extract data section (filename-independent)
    data_start = content.find('# Data [') + len('# Data [')
    data_start = content.find('] I:', data_start) + len('] I:')
    data_end = content.find('# Errors [')
    data_str = content[data_start:data_end].strip()
    data = np.fromstring(data_str, sep=' ')

    # Reshape into 2D array (200x200 as per your example)
    nx = 200
    ny = 200
    return data.reshape((ny, nx))

def load_paired_data(low_res_dir="low-res", high_res_dir="high-res"):
    """Load all paired low-res and high-res PSDMonitor.dat files."""
    # Get all subdirectories in low-res and high-res
    low_res_subdirs = sorted([d for d in os.listdir(low_res_dir) if os.path.isdir(os.path.join(low_res_dir, d))])
    high_res_subdirs = sorted([d for d in os.listdir(high_res_dir) if os.path.isdir(os.path.join(high_res_dir, d))])

    # Ensure the subdirectories match
    assert low_res_subdirs == high_res_subdirs, "Subdirectories in low-res and high-res do not match!"

    X_train = []
    y_train = []

    for subdir in low_res_subdirs:
        # Load low-res file
        low_res_file = os.path.join(low_res_dir, subdir, "PSDMonitor.dat")
        low_res_data = load_psd_file(low_res_file)

        # Load high-res file
        high_res_file = os.path.join(high_res_dir, subdir, "PSDMonitor.dat")
        high_res_data = load_psd_file(high_res_file)

        X_train.append(low_res_data)
        y_train.append(high_res_data)

    # Convert to numpy arrays
    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Normalize to [0, 1]
    X_train = (X_train - X_train.min()) / (X_train.max() - X_train.min() + 1e-8)
    y_train = (y_train - y_train.min()) / (y_train.max() - y_train.min() + 1e-8)

    return X_train, y_train

# Example usage:
X_train, y_train = load_paired_data()
print(f"Loaded {len(X_train)} pairs. Shape: {X_train.shape}")
```


## A3: U-Net model training

This UNet class/script:
- Defines a U-Net for super-resolution.
- Trains it on the paired data.
- Saves the model for later use.

```
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Define U-Net
class UNet(nn.Module):
    def __init__(self):
        super().__init__()
        # Encoder
        self.encoder1 = nn.Sequential(
            nn.Conv2d(1, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
        )
        self.pool1 = nn.MaxPool2d(2)

        self.encoder2 = nn.Sequential(
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU(),
        )
        self.pool2 = nn.MaxPool2d(2)

        # Bottleneck
        self.bottleneck = nn.Sequential(
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.ReLU(),
        )

        # Decoder
        self.upconv2 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.decoder2 = nn.Sequential(
            nn.Conv2d(256, 128, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU(),
        )

        self.upconv1 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.decoder1 = nn.Sequential(
            nn.Conv2d(128, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(),
        )

        # Final layer
        self.final = nn.Conv2d(64, 1, 1)

    def forward(self, x):
        # Encoder
        e1 = self.encoder1(x)
        p1 = self.pool1(e1)
        e2 = self.encoder2(p1)
        p2 = self.pool2(e2)

        # Bottleneck
        b = self.bottleneck(p2)

        # Decoder
        d2 = self.upconv2(b)
        d2 = torch.cat([d2, e2], dim=1)
        d2 = self.decoder2(d2)

        d1 = self.upconv1(d2)
        d1 = torch.cat([d1, e1], dim=1)
        d1 = self.decoder1(d1)

        out = self.final(d1)
        return out

# Convert numpy to PyTorch tensors
X_tensor = torch.from_numpy(X_train).float().unsqueeze(1)  # Add channel dim
y_tensor = torch.from_numpy(y_train).float().unsqueeze(1)

dataset = TensorDataset(X_tensor, y_tensor)
dataloader = DataLoader(dataset, batch_size=8, shuffle=True)

# Train
model = UNet()
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

for epoch in range(100):
    model.train()
    running_loss = 0.0
    for x_batch, y_batch in dataloader:
        x_batch, y_batch = x_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        y_pred = model(x_batch)
        loss = criterion(y_pred, y_batch)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    print(f"Epoch {epoch + 1}, Loss: {running_loss / len(dataloader)}")

# Save model
torch.save(model.state_dict(), "saxs_unet_model.pth")
```

## A4: U-Net model inference

This script:
- Loads a new low-res PSDMonitor.dat file.
- Uses the trained U-Net to predict the high-res version.


```
def deconvolve_psd(low_res_file, model_path="saxs_unet_model.pth", output_file="deconvolved_psd.npy"):
    """Deconvolve a low-res PSDMonitor.dat file using the trained U-Net."""
    # Load model
    model = UNet()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    model.to(device)

    # Load and preprocess input
    low_res = load_psd_file(low_res_file)
    low_res = (low_res - low_res.min()) / (low_res.max() - low_res.min() + 1e-8)
    low_res_tensor = torch.from_numpy(low_res).float().unsqueeze(0).unsqueeze(0).to(device)

    # Predict
    with torch.no_grad():
        high_res_tensor = model(low_res_tensor)

    # Convert back to numpy
    high_res = high_res_tensor.squeeze().cpu().numpy()

    # Save or return
    np.save(output_file, high_res)
    return high_res

# Example usage:
deconvolved = deconvolve_psd("new_low_res/PSDMonitor.dat")
print(f"Deconvolved shape: {deconvolved.shape}")
```

--------------------------------------------------------------------------------

# B: Denoising (noise2noise)

## B1: Generate noisy data

Need to generate similar data in various noisy configurations.
```
# Generate 100 noisy versions of SAMPLE=0 with varying NCOUNT and SEED
for i in {1..100}; do
  NCOUNT=$((10000 + i * 100))  # Vary NCOUNT
  SEED=$((1000 + i))            # Vary SEED
  mxrun --ncount $NCOUNT -s $SEED -d low-res/seed_${SEED}_ncount_${NCOUNT} --mpi=auto Test_SAXS.instr -L SAMPLE=0 Lambda=1.5 DLambda=0.01
done
```

## B2: Preprocess Data

Pair up the noisy images (e.g., seed_1001_ncount_10100 ↔ seed_1002_ncount_10200) and load them as numpy arrays.

```python
import numpy as np
import os
import glob
import random

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

def load_noisy_pairs(data_dir="low-res", num_pairs=50):
    """Load pairs of noisy PSDMonitor.dat files with different NCOUNT/SEED."""
    noisy_dirs = sorted(glob.glob(os.path.join(data_dir, "*")))
    random.shuffle(noisy_dirs)  # Shuffle to randomize pairs

    X = []
    y = []

    for i in range(0, min(num_pairs * 2, len(noisy_dirs)), 2):
        if i + 1 >= len(noisy_dirs):
            break
        # Load pair of noisy images
        noisy1 = load_psd_file(os.path.join(noisy_dirs[i], "PSDMonitor.dat"))
        noisy2 = load_psd_file(os.path.join(noisy_dirs[i + 1], "PSDMonitor.dat"))

        X.append(noisy1)
        y.append(noisy2)

    X = np.array(X)
    y = np.array(y)

    # Normalize to [0, 1]
    X = (X - X.min()) / (X.max() - X.min() + 1e-8)
    y = (y - y.min()) / (y.max() - y.min() + 1e-8)

    return X, y

# Example usage:
X_train, y_train = load_noisy_pairs(num_pairs=50)
print(f"Loaded {len(X_train)} pairs. Shape: {X_train.shape}")
```

## B3: Train the Noise2Noise U-Net

We use the same U-Net as in A3.

## B4: Inference

```python
def denoise_psd(noisy_file, model_path="saxs_n2n_unet.pth", output_file="denoised_psd.npy"):
    """Denoise a noisy PSDMonitor.dat file using the trained Noise2Noise U-Net."""
    # Load model
    model = UNet()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    model.to(device)

    # Load and preprocess noisy input
    noisy = load_psd_file(noisy_file)
    noisy = (noisy - noisy.min()) / (noisy.max() - noisy.min() + 1e-8)
    noisy_tensor = torch.from_numpy(noisy).float().unsqueeze(0).unsqueeze(0).to(device)

    # Denoise
    with torch.no_grad():
        denoised_tensor = model(noisy_tensor)

    denoised = denoised_tensor.squeeze().cpu().numpy()
    np.save(output_file, denoised)
    return denoised

# Example usage:
denoised = denoise_psd("new_noisy/PSDMonitor.dat")
print(f"Denoised shape: {denoised.shape}")
```

--------------------------------------------------------------------------------
# C: segmentation

```python
import numpy as np
from skimage import filters, morphology

def segment_saxs_image(image, log_clip_min=1e-20, log_clip_max=1e-10, min_region_size=10):
    """
    Segment a SAXS image using log-scale adaptive thresholding.

    Args:
        image (np.ndarray): Input SAXS image (2D array).
        log_clip_min (float): Minimum intensity for log clipping (avoid log(0)).
        log_clip_max (float): Maximum intensity for log clipping.
        min_region_size (int): Minimum size for a region to be considered signal.

    Returns:
        np.ndarray: Binary segmentation mask (1 = signal, 0 = noise).
    """
    # Step 1: Convert to log scale
    image_clipped = np.clip(image, log_clip_min, log_clip_max)
    log_image = np.log10(image_clipped)

    # Step 2: Normalize log image to [0, 1] for thresholding
    log_image_normalized = (log_image - log_image.min()) / (log_image.max() - log_image.min() + 1e-8)

    # Step 3: Adaptive thresholding (Otsu's method)
    threshold = filters.threshold_otsu(log_image_normalized)
    binary_mask = log_image_normalized > threshold

    # Step 4: Morphological cleaning
    # Remove small noise regions (opening)
    binary_mask = morphology.remove_small_objects(binary_mask, min_size=min_region_size)
    # Fill small holes (closing)
    binary_mask = morphology.closing(binary_mask, morphology.disk(1))

    # Optional: Edge refinement (Canny)
    edges = filters.sobel(log_image_normalized)
    binary_mask = binary_mask | (edges > 0.1 * edges.max())  # Combine with edges

    return binary_mask.astype(np.uint8)

# Example usage:
# Load a SAXS image (e.g., from PSDMonitor.dat)
saxs_image = np.load("PSDMonitor.npy")  # Assume shape (200, 200)
segmentation_mask = segment_saxs_image(saxs_image)

# Visualize
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.imshow(saxs_image, norm="log", cmap="viridis")
plt.title("Original SAXS Image (Log Scale)")
plt.subplot(1, 2, 2)
plt.imshow(segmentation_mask, cmap="binary")
plt.title("Segmentation Mask")
plt.show()
```

| Step | Purpose | SAXS-Specific Consideration |
| --- | --- | --- |
| **Log Scale** | Compresses dynamic range | SAXS intensities span **10+ orders of magnitude** (e.g., `1e-20` to `1e-10`). |
| **Otsu’s Thresholding** | Separates signal from noise | Works well in log space where noise and signal are more distinguishable. |
| **Morphological Cleaning** | Removes small noise regions | SAXS images often have **speckle noise** or detector artifacts. |
| **Edge Refinement** | Sharpens boundaries | Useful for **ring-like structures** (e.g., from lipids or proteins). |
