#!/bin/bash
#SBATCH --job-name=generate_dataset_%j
#SBATCH --error=generate_dataset_%j.err
#SBATCH --output=generate_dataset_%j.out
#SBATCH --nodes 1
#SBATCH --partition=mesonet
#SBATCH --reservation=formation_panraid
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --time 02:00:00
#SBATCH --account m26216
set -euo pipefail

source /projects/m26216/INSTALL/panraid.sh


#mkdir -p test_dataset
mcrun -c -n0 --openacc kws_sphere.instr

./kws_sphere.out --ncount=10000000 --dir=sphere_000000 radius=84.7831243713 pd_radius=0.0669506928876

python train_nn.py
