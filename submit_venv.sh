#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1       # Request GPU "generic resources"
#SBATCH --mem=80G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-00:30
#SBATCH --output=output/%N-%j.out

module load cuda

./train_groot.sh