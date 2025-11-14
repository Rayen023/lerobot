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

MODEL_NAME="pi05"
POLICY_PATH="lerobot/pi05_base"
POLICY_TYPE="pi05"

BATCH_SIZE=64
STEPS=60000
SAVE_FREQ=2000
COMPILE_MODEL=true
GRADIENT_CHECKPOINTING=true
DTYPE=bfloat16
SCHEDULER_DECAY_STEPS=3000

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

uv run lerobot-train \
  --policy.type="${POLICY_TYPE}" \
  --policy.pretrained_path="${POLICY_PATH}" \
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
  --policy.compile_model=${COMPILE_MODEL} \
  --policy.gradient_checkpointing=${GRADIENT_CHECKPOINTING} \
  --policy.dtype=${DTYPE} \
  --policy.scheduler_decay_steps=${SCHEDULER_DECAY_STEPS} \
  --save_freq=${SAVE_FREQ}
