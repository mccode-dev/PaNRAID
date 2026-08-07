# Overview of AI methods

## Vector type Monitor

We here assume we generate 1D vectors out of some parameters. The monitor data should be e.g. in reciprocal space for anything that produces structural data (diffraction) as it gets less sensitive to instrument configuration (e.g. wavelength).

**Input**: N experimental vectors V (size SV​) and N parameter sets P (size SP​).

**Goal**: Train an ML model to map V→P (inverse problem).

**Task**: Infer P given a new V.

This task is an Inverse Problem: you are mapping a high-dimensional observation space (V) back to a lower-dimensional latent parameter space (P).

Because the mapping V→P is often ill-posed (multiple parameter sets might produce similar vectors), the choice of model depends heavily on the size of your dataset (NN) and the nature of the relationship (linear vs. highly non-linear).

#### Methodology Comparison Table

Methodology |	Model Type |	Dev Complexity |	Training Complexity |	Performance Expectation |	Best Use Case
---|---|---|---|---|---
scikit-learn (Linear/Kernel) |	Ridge, Lasso, SVR |	Low 	| Low 	| Low/Medium | 	Small N; baseline; when P has a linear relationship with V.
scikit-learn / XGBoost |	Random Forest, Gradient Boosting |	Medium |	Medium |	Medium/High |	Medium N; non-linear relationships; when V is "tabular-like" (no spatial correlation).
TabNet |	Attentive Tabular Network |	High |	High |	High |	Medium-to-Large N; when you need feature selection/interpretability within a DL framework.
PyTorch / TF (MLP) |	Multi-Layer Perceptron |	High |	High |	High |	Large N; complex, deep non-linearities; when you need custom loss functions.
PyTorch / TF (CNN/1D-CNN) |	Convolutional Neural Net |	High |	High |	Very High |	Large N; when V has local correlations (e.g., a signal or spectrum where adjacent points matter).

#### Implementation examples

To implement these, we first need a synthetic dataset. In these examples, we generate a signal (V) where the parameters (P) control the amplitude and frequency of a sine wave.

We use numpy for data, sklearn for splitting, xgboost for trees, pytorch-tabnet for TabNet, and torch for the deep learning models.


```
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from pytorch_tabnet.tab_model import TabNetRegressor

# 1. SETUP SYNTHETIC DATA
N = 1000
S_V = 100  # Vector size
S_P = 2    # Number of parameters (e.g., Amplitude, Frequency)

def generate_data(n, sv, sp):
    # P: Random parameters between 0.1 and 5.0
    P = np.random.uniform(0.1, 5.0, (n, sp))
    # V: Create a sine wave based on P
    t = np.linspace(0, 1, sv)
    V = np.zeros((n, sv))
    for i in range(n):
        V[i, :] = P[i, 0] * np.sin(2 * np.pi * P[i, 1] * t)
    return V.astype(np.float32), P.astype(np.float32)

X, y = generate_data(N, S_V, S_P)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# --- METHOD 1: XGBOOST (Multi-Output) ---
# XGBoost is natively single-output, so we wrap it in MultiOutputRegressor
print("Training XGBoost...")
xgb = MultiOutputRegressor(XGBRegressor(n_estimators=100, learning_rate=0.1))
xgb.fit(X_train, y_train)
xgb_preds = xgb.predict(X_test)

# --- METHOD 2: TABNET ---
print("Training TabNet...")
tabnet_reg = TabNetRegressor()
tabnet_reg.fit(
    X_train=X_train, y_train=y_train,
    eval_set=[(X_test, y_test)],
    patience=10, max_epochs=100
)
tabnet_preds = tabnet_reg.predict(X_test)

# --- METHOD 3: PYTORCH MLP (Dense Network) ---
print("Training PyTorch MLP...")
class MLP(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    def forward(self, x): return self.net(x)

X_t = torch.FloatTensor(X_train)
y_t = torch.FloatTensor(y_train)
dataset = TensorDataset(X_t, y_t)
loader = DataLoader(dataset, batch_size=32, shuffle=True)

mlp = MLP(S_V, S_P)
optimizer = optim.Adam(mlp.parameters(), lr=0.001)
criterion = nn.MSELoss()

for epoch in range(50):
    for batch_x, batch_y in loader:
        optimizer.zero_grad()
        loss = criterion(mlp(batch_x), batch_y)
        loss.backward()
        optimizer.step()

mlp.eval()
with torch.no_grad():
    mlp_preds = mlp(torch.FloatTensor(X_test)).numpy()

# --- METHOD 4: PYTORCH 1D-CNN (Convolutional) ---
print("Training PyTorch CNN...")
class CNN1D(nn.Module):
    def __init__(self, output_dim):
        super().__init__()
        self.conv = nn.Sequential(
            # Input shape: (Batch, 1, S_V)
            nn.Conv1d(1, 16, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(8) # Reduces to fixed size
        )
        self.fc = nn.Sequential(
            nn.Linear(32 * 8, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    def forward(self, x):
        x = x.unsqueeze(1) # Add channel dimension: (Batch, 1, S_V)
        x = self.conv(x)
        x = x.view(x.size(0), -1) # Flatten
        return self.fc(x)

X_t_cnn = torch.FloatTensor(X_train)
y_t_cnn = torch.FloatTensor(y_train)
dataset_cnn = TensorDataset(X_t_cnn, y_t_cnn)
loader_cnn = DataLoader(dataset_cnn, batch_size=32, shuffle=True)

cnn = CNN1D(S_P)
optimizer_cnn = optim.Adam(cnn.parameters(), lr=0.001)
criterion_cnn = nn.MSELoss()

for epoch in range(50):
    for batch_x, batch_y in loader_cnn:
        optimizer_cnn.zero_grad()
        loss = criterion_cnn(cnn(batch_x), batch_y)
        loss.backward()
        optimizer_cnn.step()

cnn.eval()
with torch.no_grad():
    cnn_preds = cnn(torch.FloatTensor(X_test)).numpy()

# --- EVALUATION ---
from sklearn.metrics import mean_squared_error
print("\n--- MSE Results (Lower is better) ---")
print(f"XGBoost: {mean_squared_error(y_test, xgb_preds):.6f}")
print(f"TabNet:  {mean_squared_error(y_test, tabnet_preds):.6f}")
print(f"MLP:     {mean_squared_error(y_test, mlp_preds):.6f}")
print(f"CNN:     {mean_squared_error(y_test, cnn_preds):.6f}")
```

**Notes:**

- XGBoost (MultiOutputRegressor): Standard XGBoost is designed for a single target variable. To predict multiple parameters at once, we wrap it in scikit-learn's MultiOutputRegressor, which fits one regressor per parameter.
- TabNet (pytorch-tabnet): This is a specialized library. It is highly effective for "tabular" data but works well for vectors too. It includes built-in support for multi-target regression.
- MLP Shape: The MLP takes the vector V as a flat feature list. It assumes every index in V is a feature.
- CNN Shape (unsqueeze(1)): This is the most common error in PyTorch CNNs. A Conv1d layer expects input in the shape (Batch, Channels, Length). Since the V is 1D, we must treat it as having 1 channel (like a grayscale image).
- CNN AdaptiveAvgPool1d: We used this instead of standard MaxPool1d at the end. This ensures that regardless of the input vector size SV​, the output passed to the fully connected layer is always the same size, making the model flexible to changes in SV​.

## 2D type Monitor

We could envisage:

1- imaging: segmentation for imaging instr, e.g. tomography

2- diffraction: could be e.g. phase and texture estimates. I(x,y) must be in Q space not to depend much on instrument parameters. Can use a U-Net.

3- de-noising: can apply to any 2D data set.

