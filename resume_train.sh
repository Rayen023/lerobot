#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=80G
#SBATCH --time=10:00:00
#SBATCH --output=output/%N-%j.out

module load cuda

export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"
export WANDB_CACHE_DIR="/home/rayen/scratch/lerobot/.cache/wandb"
export WANDB_DIR="/home/rayen/scratch/lerobot/.cache/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/lerobot/.cache/wandb"

# Hardcoded resume parameters
OUTPUT_DIR="/home/rayen/scratch/lerobot/outputs/train/pi05_merged-pick-place-red-block-12_bs64_20251115_094542"
JOB_NAME="pi05_merged-pick-place-red-block-12_bs64_20251115_094542"
DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/merged-pick-place-red-block-12"
DATASET_NAME="merged-pick-place-red-block-12"

# Pi05 parameters
POLICY_PATH="lerobot/pi05_base"
POLICY_TYPE="pi05"
BATCH_SIZE=64
STEPS=30000
SAVE_FREQ=4000
COMPILE_MODEL=true
GRADIENT_CHECKPOINTING=true
DTYPE=bfloat16
SCHEDULER_DECAY_STEPS=3000

echo "RESUMING JOB: $JOB_NAME from $OUTPUT_DIR"

uv run lerobot-train \
  --policy.type=${POLICY_TYPE} \
  --policy.pretrained_path=${POLICY_PATH} \
  --policy.compile_model=${COMPILE_MODEL} \
  --policy.gradient_checkpointing=${GRADIENT_CHECKPOINTING} \
  --policy.dtype=${DTYPE} \
  --policy.scheduler_decay_steps=${SCHEDULER_DECAY_STEPS} \
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
  --save_freq=${SAVE_FREQ} \
  --resume=true
