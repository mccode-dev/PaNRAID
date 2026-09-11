![DIADEM banner](../images/toplogo-diadem.png)
# ![PaNRAID logo](../images/panraid_small.png) PaNRAID Software ![PaNRAID logo](../images/panraid_small.png)

![Under construction](../images/Under_Construction_small.png)
![Brain helmet](../images/brainhelmet_small.png)

## Work in progress! Subject to change!

### Work and tutorials during PaNRAID is based on open source software:

* We provide the **[panraid-environment.yml](panraid-environment.yml)** environment file for use with **`conda/mamba/micromamba`**

Please uncomment these lines of the env file if you have access to an NVIDIA GPU:

```
  # - cuda-toolkit
  # - pytorch-gpu
```


_______
###**!! Please install the PaNRAID environment prior to arrival in La Rochelle / Ile d'Oleron !!**
_______

### No `conda`-solver on your system?
* We recommend to install [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)

_______

### Create your environment:
* `micromamba env create -f panraid-environment.yml`

_______


### Update your environment:
* `mamba env update -f panraid-environment.yml --prune`

_______