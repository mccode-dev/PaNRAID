# Day 4 — Wednesday 24 September (Morning): AI Surrogate (approximator) - solution

| **Component** | **Details** |
| --- | --- |
| **Input** | Parameters from `Param:` lines (e.g., distances, wavelength, sample type). |
| **Output** | 2D SAXS image (200×200). |
| **Model Architecture** | Fully Connected Network (FCN) or CNN-based. |
| **Training Data** | Pairs of `(parameters, SAXS image)` from McXtrace simulations. |
| **Normalization** | Parameters scaled to `[0, 1]`. |
| **Loss Function** | Mean Squared Error (MSE) between predicted and true images. |
| **Use Case** | Fast approximation of SAXS images for given parameters. |

The surrogate model is only as good as the training data. Extrapolation outside the training range may be inaccurate.

## Generate Training Data

Run McXtrace simulations with diverse parameter combinations to cover the input space. Example:

```
# Example: Generate 1000 simulations with random parameters
for i in {1..1000}; do
  DistanceFromSourceToFirstPinhole=$(python -c "import random; print(random.uniform(0.05, 0.2))")
  Lambda=$(python -c "import random; print(random.uniform(1.0, 2.0))")
  SAMPLE=$(python -c "import random; print(random.randint(0, 11))")
  mxrun -d surrogate_data/sim_$i --mpi=auto Test_SAXS.instr SAMPLE=$SAMPLE Lambda=$Lambda DistanceFromSourceToFirstPinhole=$DistanceFromSourceToFirstPinhole 
done
```

## Extract Parameters and Images

Use the following script to extract:
- Parameters from Param: lines.
- SAXS images from Data [...] I: blocks.

Then we may:
- Convert the parameter dictionary into a fixed-length numerical vector for the model input.
- Normalize the encoded parameters to [0, 1] for better training stability.

Convert and normalize the parameter dictionary into a fixed-length numerical vector for the model input.

```python
import numpy as np
import os
import glob
import re
import torch
from sklearn.preprocessing import MinMaxScaler

# --- Constants ---
IMAGE_SHAPE = (200, 200)
# Adapt to select only the parameters which have been scanned above
PARAM_KEYS = [
    "DistanceFromSourceToFirstPinhole",
    "DistanceFromSourceToSecondPinhole",
    "DistanceFromSecondPinholeToSample",
    "DistanceFromSampleToDetector",
    "RadiusOfDetector",
    "Lambda",
    "DLambda",
    "SAMPLE"
]

# --- Data Loading ---
def load_simulation(directory):
    """Load parameters and SAXS image from a simulation directory."""
    psd_file = glob.glob(os.path.join(directory, "*PSD*monitor*.dat"))[0]
    with open(psd_file, 'r') as f:
        content = f.read()

    # Extract parameters
    params = dict(re.findall(r'# Param: (\w+)=([^\s]+)', content))
    params = {k: float(v) for k, v in params.items() if k in PARAM_KEYS}

    # Extract image
    data_start = content.find('# Data [') + len('# Data [')
    data_start = content.find('] I:', data_start) + len('] I:')
    data_end = content.find('# Errors [')
    image = np.fromstring(content[data_start:data_end].strip(), sep=' ').reshape(IMAGE_SHAPE)

    return params, image

def load_dataset(data_dir="surrogate_data", num_samples=None):
    """Load all simulations from a directory."""
    sim_dirs = sorted(glob.glob(os.path.join(data_dir, "sim_*")))
    if num_samples:
        sim_dirs = sim_dirs[:num_samples]

    X_params = []
    y_images = []
    for sim_dir in sim_dirs:
        try:
            params, image = load_simulation(sim_dir)
            X_params.append(params)
            y_images.append(image)
        except Exception as e:
            print(f"Skipping {sim_dir}: {e}")

    # Convert to numpy arrays
    y_images = np.array(y_images)  # Shape: (N, 200, 200)
    return X_params, y_images
    
# --- Encoding ---
def encode_params(params_list, param_keys=PARAM_KEYS):
    """Convert list of params dicts to a 2D numpy array."""
    return np.array([[params[key] for key in param_keys] for params in params_list])

# --- Normalization ---
def normalize_params(X_encoded):
    """Normalize parameters to [0, 1]."""
    scaler = MinMaxScaler()
    return scaler.fit_transform(X_encoded), scaler


# Load all simulations
X_params, y_images = load_dataset(data_dir="surrogate_data", num_samples=1000)
# Encode and normalize parameters
X_encoded = encode_params(X_params)
X_normalized, scaler = normalize_params(X_encoded)
```

## Build the Surrogate Model

Use a neural network to predict the SAXS image from the parameters. We use a fully connected network (Perceptron) which flattens the image and predict pixel values directly.

Prepare Data for PyTorch and set Training Loop.

```python
import torch
import torch.nn as nn
import torch.optim as optim

class SAXSSurrogate(nn.Module):
    def __init__(self, input_dim, output_dim=200*200):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 1024)
        self.fc2 = nn.Linear(1024, 4096)
        self.fc3 = nn.Linear(4096, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

# Initialize model
input_dim = len(selected_params)
model = SAXSSurrogate(input_dim)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)
```

## Train the Surrogate Model

```python
# --- Training ---
def train_model(X_train, y_train, epochs=100, batch_size=32, lr=1e-3):
    """Train the surrogate model."""
    # Flatten images
    y_train_flat = y_train.reshape(y_train.shape[0], -1)

    # Convert to PyTorch tensors
    X_tensor = torch.from_numpy(X_train).float()
    y_tensor = torch.from_numpy(y_train_flat).float()

    # DataLoader
    dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Initialize model
    input_dim = X_train.shape[1]
    model = SAXSSurrogate(input_dim)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Training loop
    for epoch in range(epochs):
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
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {running_loss / len(dataloader):.4f}")

    return model
    
model = train_model(X_normalized, y_images, epochs=100)
torch.save(model.state_dict(), "saxs_surrogate.pth")
```

## Inference

Use the Surrogate Model for Prediction.

```
# --- Inference ---
def predict_image(params, model, scaler, param_keys=PARAM_KEYS):
    """Predict SAXS image from parameters."""
    # Encode and normalize
    encoded = np.array([[params[key] for key in param_keys]])
    normalized = scaler.transform(encoded)
    tensor = torch.from_numpy(normalized).float().to(next(model.parameters()).device)

    # Predict
    model.eval()
    with torch.no_grad():
        predicted_flat = model(tensor).cpu().numpy().reshape(IMAGE_SHAPE)

    return predicted_flat

# Load trained model
model = SAXSSurrogateFCN(len(selected_params))
model.load_state_dict(torch.load("saxs_surrogate_model.pth"))
# Predict image for new parameters
params = {"DistanceFromSourceToFirstPinhole": 0.1, "Lambda": 1.54, ...}
predicted_image = predict_image(params, model, scaler, selected_params)
```

