![DIADEM banner](../images/toplogo-diadem.png)
# ![Under construction](../images/Under_Construction_small.png) ![Si-brain helmet](../images/brainhelmet_small.png) ![PaNRAID logo](../images/panraid_small.png) PaNRAID Software ![PaNRAID logo](../images/panraid_small.png) ![Si-brain helmet](../images/brainhelmet_small.png) ![Under construction](../images/Under_Construction_small.png)

### -—> Work in progress! Subject to change! <—- 

_Work and tutorials during PaNRAID is based on open source software + optional NVIDIA infrastructure_

# A. Installation for your participant laptop ![laptop](../images/laptop.png)

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

# B. Installation for MESONET account ![hpc](../images/hpc.png)

![Under construction](../images/Under_Construction_small.png) ![Si-brain helmet](../images/brainhelmet_small.png) 

Description pending, but:
* The above `.yml` files should work
* `nvhpc` is probably available as a module
