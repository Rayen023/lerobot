#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=80G
#SBATCH --time=1-17:00
#SBATCH --output=output/%N-%j.out

module load cuda

MODEL_NAME="smolvla"
DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/pick-place-red-block-all"

POLICY_PATH="lerobot/smolvla_base"
BATCH_SIZE=192
STEPS=30000
SAVE_FREQ=2000
CHUNK_SIZE=50
N_ACTION_STEPS=50
RENAME_MAP='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_cs${CHUNK_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

echo "JOB_NAME: $JOB_NAME"

uv run lerobot-train \
  --policy.path="${POLICY_PATH}" \
  --rename_map="${RENAME_MAP}" \
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
