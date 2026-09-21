![DIADEM banner](../images/toplogo-diadem.png)
# <img src="../images/panraid_small.png" alt="PaNRAID logo" align="middle"> PaNRAID Software <img src="../images/panraid_small.png" alt="PaNRAID logo" align="middle">

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
* For those of you on Windows, please follow the steps to install MSVC compilers [outlined at McStas/McXtrace GitHub](https://github.com/mccode-dev/McCode/tree/main/INSTALL-McStas/conda#note-for-use-on-windows)

-------
## Test run for McStas:
`mctest --ncount=1e6 --verbose --mpi=auto --compilemax=1200 --runmax=600 --instr=PSI_DMC`
## Test run for McXtrace:
`mxtest --ncount=1e6 --verbose --mpi=auto --compilemax=1200 --runmax=600 --instr=SOLEIL_LUCIA`
_______
## Optional:
#### Got an NVIDIA GPU (Linux or Windows only)?
After the above finishes, also run:

* `micromamba env update -n panraid -f panraid-cuda.yml`

### Got an NVIDIA GPU on Linux and want to run McCode with that?
* Manually install [NVHPC](https://developer.nvidia.com/hpc-sdk/downloads) from NVIDIA

_______

# B. PaNRAD on your MESONET account <img src="../images/hpc.png" alt="hpc" align="middle">

1. You should have received a participant invitation via email - keep this email handy!
2. Next step is to request an account at MesoNET via this documentation:<br> [<option value="FR">Français 🇫🇷</option>](https://www.mesonet.fr/documentation/user-documentation/acces/portail/) [<option value="GB">English 🇬🇧</option> (google translate)](https://www-mesonet-fr.translate.goog/documentation/user-documentation/acces/portail/?_x_tr_sl=fr&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp)
3. Once your account exists (needs to match the email registered with the PaNRAID secretariat), follow the link in the invitation-email. This should add your account to the relevant PaNRAID 'Project', see definitions at:<br> [<option value="FR">Français 🇫🇷</option>](https://www.mesonet.fr/documentation/user-documentation/acces/projet) [<option value="GB">English 🇬🇧</option> (google translate)](https://www-mesonet-fr.translate.goog/documentation/user-documentation/acces/projets/?_x_tr_sl=fr&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp)
4. Once you are on Project, add an `ssh` key to your account / Project via this documentation:<br> [<option value="FR">Français 🇫🇷</option>](https://www.mesonet.fr/documentation/user-documentation/acces/ssh) [<option value="GB">English 🇬🇧</option> (google translate)](https://www-mesonet-fr.translate.goog/documentation/user-documentation/acces/ssh/?_x_tr_sl=fr&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp) <br>(Our system of use is `juliet`, setting up a shorthand-config in your `.ssh/config` is recommended...)
5. Once `ssh` key(s) are added, there is a waiting time of ~1 hour
6. Log in to `juliet` and **nota bene:**

* [<option value="FR">Français 🇫🇷</option> Docs Juliet](https://www.mesonet.fr/documentation/user-documentation/code_form/juliet/)

```
Lors des connexions aux nœuds de Juliet, il peut s'écouler environ 30 sec avant que le prompt ne soit disponible.

Documentation de Juliet : https://www.mesonet.fr/documentation/user-documentation/code_form/juliet/
```
* [<option value="GB">English 🇬🇧</option> Docs for Juliet](https://www-mesonet-fr.translate.goog/documentation/user-documentation/code_form/juliet/?_x_tr_sl=fr&_x_tr_tl=en&_x_tr_hl=en-US&_x_tr_pto=wapp)

```
When connecting to Juliet nodes, it may take approximately 30 seconds for the prompt to become available.

Juliet documentation: https://www.mesonet.fr/documentation/user-documentation/code_form/juliet/
```

## Do you have a shell? Success! Then you should simply run
* `source /projects/m26216/INSTALL/panraid.sh`
* (The above script loads a central software deployment on our Project directory + GPU-related modules from MesoNET)
* Quick interactive session (1 GPU reserved for 30 minutes interactive)
<br>`srun -p mesonet --account=m26216 --tasks=1 --gres=gpu:1 --exclusive --time=0:30:0 --pty /bin/bash`
* Example slurm batch files: 
<br>(The `mctest`/`mxtest` used in the script are toolsthat runs a series of `McStas`/`McXtrace` instruments from `${MCSTAS}/examples` / `${MCXTRACE}/examples`. You should do some `mcrun/mxrun` instead)
* [mcstas-GPU-test.sh](mcstas-GPU-test.sh)
* [mcxtrace-GPU-test.sh](mcxtrace-GPU-test.sh)
_______

# C. Known issues + workarounds

**See [Issues-Workarounds](Issues-Workarounds/README.md)**
