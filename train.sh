#!/bin/bash

# Hyperparameters - Edit these values as needed
MODEL_NAME="smolvla_base"
POLICY_PATH="lerobot/smolvla_base"
# Use absolute path for local dataset
DATASET_REPO_ID="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/youliangtan-so101-table-cleanup"
BATCH_SIZE=64
LEARNING_RATE=0.0003
STEPS=50000
DEVICE="cuda"
PUSH_TO_HUB=false
WANDB_ENABLE=true

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

DATASET_NAME=$(basename "$DATASET_REPO_ID")

JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_lr${LEARNING_RATE}_stps${STEPS}_${TIMESTAMP}"

OUTPUT_DIR="outputs/train/${JOB_NAME}"

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
  --policy.optimizer_lr=${LEARNING_RATE} \
  --rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}' \
  --policy.empty_cameras=1
