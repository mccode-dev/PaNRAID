"""Simple PyTorch classifier for the two-moons dataset.

Requires: torch, scikit-learn
Run on a GPU node: python train_nn.py
"""

import torch
from torch import nn
from sklearn.datasets import make_moons


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using {device}")
if device.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Two input coordinates and a class label (0 or 1) per sample.
X, y = make_moons(n_samples=1000, noise=0.2, random_state=42)
X = torch.tensor(X, dtype=torch.float32).to(device)
y = torch.tensor(y, dtype=torch.long).to(device)

# Two inputs -> 16 hidden neurons -> two class scores (logits).
model = nn.Sequential(
    nn.Linear(2, 16),
    nn.ReLU(),
    nn.Linear(16, 2),
).to(device)

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(1, 101):
    model.train()
    logits = model(X)  # Forward pass
    loss = loss_fn(logits, y)

    optimizer.zero_grad()  # Clear gradients from the previous step
    loss.backward()        # Compute gradients
    optimizer.step()       # Update model parameters

    if epoch % 10 == 0:
        model.eval()
        with torch.no_grad():
            predictions = model(X).argmax(dim=1)
            accuracy = (predictions == y).float().mean().item()
        print(f"Epoch {epoch:3d} | loss: {loss.item():.4f} | accuracy: {accuracy:.1%}")
