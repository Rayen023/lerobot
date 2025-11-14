#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1 
#SBATCH --mem=80G
#SBATCH --time=0-02:00
#SBATCH --output=output/%N-%j.out

module load cuda

MODEL_NAME="${1:-pi05}"

# MODEL_NAME = "groot"

export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"
export WANDB_CACHE_DIR="/home/rayen/scratch/lerobot/.cache/wandb"
export WANDB_DIR="/home/rayen/scratch/lerobot/.cache/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/lerobot/.cache/wandb"

case "$MODEL_NAME" in
  groot)
    POLICY_TYPE="groot"
    POLICY_PATH="nvidia/GR00T-N1.5-3B"
    DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/Backups/sort-blocks-2"
    BATCH_SIZE=64
    STEPS=10000
    SAVE_FREQ=2000
    EXTRA_ARGS="--policy.type=${POLICY_TYPE} --policy.base_model_path=${POLICY_PATH} --policy.repo_id=\${OUTPUT_DIR}"
    ;;
  pi05)
    POLICY_PATH="lerobot/pi05_base"
    POLICY_TYPE="pi05"
    DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/merged-sort-blocks-123"
    BATCH_SIZE=64
    STEPS=60000
    SAVE_FREQ=2000
    COMPILE_MODEL=true
    GRADIENT_CHECKPOINTING=true
    DTYPE=bfloat16
    SCHEDULER_DECAY_STEPS=3000
    EXTRA_ARGS="--policy.type=${POLICY_TYPE} --policy.pretrained_path=${POLICY_PATH} --policy.compile_model=${COMPILE_MODEL} --policy.gradient_checkpointing=${GRADIENT_CHECKPOINTING} --policy.dtype=${DTYPE} --policy.scheduler_decay_steps=${SCHEDULER_DECAY_STEPS}"
    ;;
  smolvla)
    POLICY_PATH="lerobot/smolvla_base"
    DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/merged-sort-blocks-123"
    BATCH_SIZE=192
    STEPS=50000
    SAVE_FREQ=2000
    RENAME_MAP='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'
    EXTRA_ARGS="--policy.path=${POLICY_PATH} --rename_map=${RENAME_MAP}"
    ;;
  *)
    echo "Unknown model: $MODEL_NAME. Use: groot, pi05, or smolvla"
    exit 1
    ;;
esac

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

eval uv run lerobot-train \
  ${EXTRA_ARGS} \
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
  --save_freq=${SAVE_FREQ}
