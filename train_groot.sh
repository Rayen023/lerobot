#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=80G
#SBATCH --time=1-17:00
#SBATCH --output=output/%N-%j.out

module load cuda

MODEL_NAME="groot"
DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/pick-place-red-block-all"

POLICY_TYPE="groot"
POLICY_PATH="nvidia/GR00T-N1.5-3B"
BATCH_SIZE=120
STEPS=30000
SAVE_FREQ=2000
CHUNK_SIZE=20
N_ACTION_STEPS=20

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_cs${CHUNK_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

echo "JOB_NAME: $JOB_NAME"

uv run lerobot-train \
  --policy.type=${POLICY_TYPE} \
  --policy.base_model_path=${POLICY_PATH} \
  --policy.repo_id="${OUTPUT_DIR}" \
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
  --policy.chunk_size=${CHUNK_SIZE} \
  --policy.n_action_steps=${N_ACTION_STEPS}
