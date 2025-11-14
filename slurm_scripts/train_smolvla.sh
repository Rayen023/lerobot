#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1 
#SBATCH --mem=80G
#SBATCH --time=0-23:00
#SBATCH --output=output/%N-%j.out

module load cuda

DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/merged-sort-blocks-123"

export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"

export WANDB_CACHE_DIR="/home/rayen/scratch/wandb"
export WANDB_DIR="/home/rayen/scratch/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/wandb"

MODEL_NAME="smolvla_base"
POLICY_PATH="lerobot/smolvla_base"

BATCH_SIZE=192
STEPS=50000
SAVE_FREQ=2000
RENAME_MAP='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

uv run lerobot-train \
  --policy.path="${POLICY_PATH}" \
  --dataset.repo_id="${DATASET_NAME}" \
  --dataset.root="${DATASET_ROOT}" \
  --dataset.revision=main \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --policy.device=cuda \
  --wandb.enable=true \
  --wandb.disable_artifact=true \
  --policy.push_to_hub=false \
  --rename_map="${RENAME_MAP}" \
  --save_freq=${SAVE_FREQ}