# Running a Jupyter notebook on a cluster GPU node using VS Code

This can be of help if you are used to training models within jupyter notebooks, or if you want to run the jupyter notebook examples in the cluster. 

By using [Remote-SSH extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh), VS Code connects initially to the cluster’s login node, and we do not want to train models there (nor will we have GPU access there). The steps to execute a notebook on a GPU compute node on mesonet will be:

1. Request a compute node through Slurm.
2. Start Jupyter on that node.
3. Forward a port from the login node to the compute node.
4. Connect VS Code to that Jupyter server.

Let's see them in more detail.

## 1. Choose your assigned port

Since we **will not** be using exclusive nodes, we might have a port forwarding conflict. Therefore, choose any port between 8800 and 8900 (or be creative) that you'll use for the connection. If you get that it is occupied, try another one. 

Each student must use a different port.

For example:

| Student | Port |
| ------: | ---: |
|       1 | 8801 |
|       2 | 8802 |
|       3 | 8803 |
|       … |    … |
|      15 | 8815 |

In the commands below, replace `8801` with your assigned port. 

## 2. Request an interactive compute node

Open a terminal in the Remote-SSH VS Code window and run:

```bash
srun \
  --partition=mesonet \
  --account=m26216 \
  --ntasks=1 \
  --gres=gpu:1 \
  --time=00:30:00 \
  --pty /bin/bash
```

Once the allocation starts, record the compute-node name using:

```bash
hostname
```

For example:

```text
juliet3
```

Keep this terminal open.

## 3. Activate your Python environment

Inside the compute node, activate your environment:

```bash
source /projects/m26216/INSTALL/panraid.sh
```

## 4. Start Jupyter on the compute node

Use your assigned port:

```bash
jupyter lab \
  --no-browser \
  --ip=127.0.0.1 \
  --port=8801
```

Jupyter will print a URL containing a security token, similar to:

```text
http://localhost:8801/lab?token=abc123...
```

Keep Jupyter running and do not close this terminal.

## 5. Create the SSH tunnel

Open a second terminal in the same VS Code Remote-SSH window. This terminal should start on the login node.

Forward your assigned login-node port to the same port on your compute node:

```bash
ssh -N -L 8801:127.0.0.1:8801 juliet3
```

Replace:

* `8801` with your assigned port.
* `juliet3` with the hostname obtained in step 2.

The command normally produces no output. Leave this terminal open while using the notebook.

## 6. Connect VS Code to Jupyter

Open the notebook in VS Code and:

1. Click the kernel selector in the upper-right corner.
2. Select **Select Another Kernel**.
3. Select **Existing Jupyter Server**.
4. Enter the URL printed by Jupyter, replacing `localhost` with `127.0.0.1` if needed:

```text
http://127.0.0.1:8801/?token=abc123...
```

Use your own assigned port and actual token.

## 7. Verify the connection

Run the following notebook cell:

```python
import socket
import sys

print("Compute node:", socket.gethostname())
print("Python:", sys.executable)
```

For PyTorch and CUDA:

```python
import torch

print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
```

The hostname should correspond to the assigned compute node, and the Python path should belong to your activated environment.

## When you finish

Shut down the Jupyter server with `Ctrl+C`, close the tunnel with `Ctrl+C`, and exit the allocation:

```bash
exit
```

Do not leave idle GPU allocations running.
