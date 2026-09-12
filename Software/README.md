![DIADEM banner](../images/toplogo-diadem.png)
# ![PaNRAID logo](../images/panraid_small.png) PaNRAID Software ![PaNRAID logo](../images/panraid_small.png)

![Under construction](../images/Under_Construction_small.png)
![Brain helmet](../images/brainhelmet_small.png)

### Work in progress! Subject to change!

## Work and tutorials during PaNRAID is based on open source software:

We provide:

* a base **[panraid.yml](panraid.yml)** for use with **`conda/mamba/micromamba`
* (an optional **[panraid-cuda.yml](panraid-cuda.yml)** for machines with NVIDIA GPU)


### No `conda`-solver on your system?
* We recommend to install [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)

_______

### Create your `panraid` environment:
* `micromamba env create -f panraid.yml`

####Got an NVIDIA GPU (Linux or Windows only)?
After the above finishes, also run:

* `micromamba env update -n panraid -f panraid-cuda.yml`
_______

