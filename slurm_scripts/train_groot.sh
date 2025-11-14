#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1 
#SBATCH --mem=80G
#SBATCH --time=0-23:00
#SBATCH --output=output/%N-%j.out

module load cuda

DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/Backups/sort-blocks-2"

export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"

export WANDB_CACHE_DIR="/home/rayen/scratch/wandb"
export WANDB_DIR="/home/rayen/scratch/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/wandb"

MODEL_NAME="groot_n1.5"
POLICY_PATH="nvidia/GR00T-N1.5-3B"
POLICY_TYPE="groot"
EMBODIMENT_TAG="so101"

BATCH_SIZE=64
STEPS=10000
SAVE_FREQ=2000

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

uv run lerobot-train \
  --policy.type="${POLICY_TYPE}" \
  --policy.base_model_path="${POLICY_PATH}" \
  --dataset.repo_id="${DATASET_NAME}" \
  --dataset.root="${DATASET_ROOT}" \
  --dataset.revision=main \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --policy.repo_id="${OUTPUT_DIR}" \
  --policy.device=cuda \
  --wandb.enable=true \
  --wandb.disable_artifact=true \
  --policy.push_to_hub=false \
  --save_freq=${SAVE_FREQ}
