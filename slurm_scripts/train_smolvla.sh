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

# =============================================================================
# SmolVLA Training Script with SLURM
# Configuration for SmolVLA Vision-Language-Action model
# =============================================================================

# =============================================================================
# Hyperparameters - Edit these values as needed
# =============================================================================

MODEL_NAME="smolvla_base"
POLICY_PATH="lerobot/smolvla_base"

# Dataset Configuration
# Use absolute path for local dataset
# DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/original_resized_rotated_cleaned"
# DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/sort-blocks"
DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/merged-so101-table-cleanup"
# Training Hyperparameters 
BATCH_SIZE=192 # 64 uses 16 gb VRAM
STEPS=50000

# Device Configuration
DEVICE="cuda"

# Output and Logging
PUSH_TO_HUB=false
WANDB_ENABLE=true

# =============================================================================
# Auto-generated Configuration
# =============================================================================

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_REPO_ID")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

# =============================================================================
# Training Command
# =============================================================================

uv run lerobot-train \
  --policy.path="${POLICY_PATH}" \
  --dataset.repo_id="${DATASET_REPO_ID}" \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --policy.device=${DEVICE} \
  --wandb.enable=${WANDB_ENABLE} \
  --policy.push_to_hub=${PUSH_TO_HUB} \
  --rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}' \
  --save_freq=3000 \