![DIADEM banner](../images/toplogo-diadem.png)
# <img src="../images/Under_Construction_small.png" alt="under construction" align="middle"> <img src="../images/brainhelmet_small.png" alt="Si-brain helmet construction" align="middle"> <img src="../images/panraid_small.png" alt="PaNRAID logo" align="middle"> PaNRAID Software <img src="../images/panraid_small.png" alt="PaNRAID logo" align="middle"> <img src="../images/brainhelmet_small.png" alt="Si-brain helmet construction" align="middle"> <img src="../images/Under_Construction_small.png" alt="under construction" align="middle">

### -—> Work in progress! Subject to change! <—- 

_Work and tutorials during PaNRAID is based on open source software + optional NVIDIA infrastructure_

# A. Installation for your participant laptop <img src="../images/laptop.png" alt="laptop" align="middle">
We provide:

* a base **[panraid.yml](panraid.yml)** for use with **`conda/mamba/micromamba`**
* (an optional **[panraid-cuda.yml](panraid-cuda.yml)** for machines with NVIDIA GPU)


### No `conda`-solver on your system?
* We recommend to install [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)

_______
## Required:
### Create your `panraid` environment:
* `micromamba env create -f panraid.yml`

_______
## Optional:
#### Got an NVIDIA GPU (Linux or Windows only)?
After the above finishes, also run:

* `micromamba env update -n panraid -f panraid-cuda.yml`

### Got an NVIDIA GPU on Linux and want to run McCode with that?
* Manually install [NVHPC](https://developer.nvidia.com/hpc-sdk/downloads) from NVIDIA
_______

# B. Installation for MESONET account <img src="../images/hpc.png" alt="hpc" align="middle"> <img src="../images/Under_Construction_small.png" alt="under construction" align="middle"> <img src="../images/brainhelmet_small.png" alt="Si-brain helmet construction" align="middle">


Description pending, but:
* The above `.yml` files should work
* `nvhpc` is probably available as a module

# Known issues + workarounds

**See [Issues-Workarounds](Issues-Workarounds/README.md)**
