#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1       # Request GPU "generic resources"
#SBATCH --mem=80G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-23:00
#SBATCH --output=output/%N-%j.out

module load cuda

# Set Hugging Face cache to scratch to avoid home directory quota issues
export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"

# Set WandB cache directory to scratch space instead of home directory
export WANDB_CACHE_DIR="/home/rayen/scratch/wandb"
export WANDB_DIR="/home/rayen/scratch/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/wandb"

MODEL_NAME="pi05"
POLICY_PATH="lerobot/pi05_base"
POLICY_TYPE="pi05"

# DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/original_resized_rotated_cleaned"
# DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/sort-blocks"
DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/merged-so101-table-cleanup"

BATCH_SIZE=64 #32 uses 40 gb vram
STEPS=60000


TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_REPO_ID")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"


uv run lerobot-train \
  --dataset.repo_id="${DATASET_REPO_ID}" \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --wandb.enable=true \
  --policy.device="cuda" \
  --policy.type="${POLICY_TYPE}" \
  --policy.pretrained_path="${POLICY_PATH}" \
  --policy.push_to_hub=false \
  --policy.compile_model=true \
  --policy.gradient_checkpointing=true \
  --policy.dtype=bfloat16 \
  --policy.scheduler_decay_steps=3000 \
  --save_freq=3000
