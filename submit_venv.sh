#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1       # Request GPU "generic resources"
#SBATCH --mem=80G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-00:30
#SBATCH --output=output/%N-%j.out

module load python/3.11

echo "Activating virtual environment..."
source .venv/bin/activate


python lerobot/scripts/train.py --policy.type=pi0 --dataset.repo_id=lerobot/stanford_kuka_multimodal_dataset