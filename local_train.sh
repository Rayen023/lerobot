#!/bin/bash

export HF_HOME="/mnt/0a56cc8f-eb63-4f04-b727-0615646b8bdb/HF_HOME"

DATASET_ROOT="/home/recherche-a/rayen/VLA/datasets/merged-all-datasets"

BATCH_SIZE=72
STEPS=20000
SAVE_FREQ=2000
CHUNK_SIZE=16
N_ACTION_STEPS=16

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
MODEL_NAME="smolvla_base"
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_chunk${CHUNK_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/${JOB_NAME}"
POLICY_PATH="lerobot/smolvla_base"
RENAME_MAP='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'

uv run lerobot-train \
  --dataset.repo_id="${DATASET_NAME}" \
  --dataset.root="${DATASET_ROOT}" \
  --dataset.revision=main \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --policy.device=cuda \
  --wandb.enable=false \
  --wandb.disable_artifact=true \
  --policy.push_to_hub=false \
  --save_freq=${SAVE_FREQ} \
  --policy.path="${POLICY_PATH}" \
  --rename_map="${RENAME_MAP}" \
  --policy.chunk_size=${CHUNK_SIZE} \
  --policy.n_action_steps=${N_ACTION_STEPS}
