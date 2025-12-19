#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=80G
#SBATCH --time=1-17:00
#SBATCH --output=output/%N-%j.out

module load cuda

: '
sbatch train.sh groot
sbatch train.sh smolvla
sbatch train.sh pi05

MAKE SURE TO COMMENT OR UNCOMMENT THE COMMON HYPERPARAMS
 '

export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"
export WANDB_CACHE_DIR="/home/rayen/scratch/lerobot/.cache/wandb"
export WANDB_DIR="/home/rayen/scratch/lerobot/.cache/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/lerobot/.cache/wandb"

MODEL_NAME="${1:-groot}"
# MODEL_NAME = "groot"
# DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/merged-pick-place-red-block-12"
# DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/sort-blocks-all"
# DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/cleanup-table-all"
DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/pick-place-red-block-all"
# DATASET_ROOT="/home/rayen/scratch/lerobot/datasets/pick-place-red-block-3"

case "$MODEL_NAME" in
  groot)
    POLICY_TYPE="groot"
    POLICY_PATH="nvidia/GR00T-N1.5-3B"
    BATCH_SIZE=120
    STEPS=30000
    SAVE_FREQ=2000
    CHUNK_SIZE=20
    N_ACTION_STEPS=20
    EXTRA_ARGS="--policy.type=${POLICY_TYPE} --policy.base_model_path=${POLICY_PATH} --policy.repo_id=\${OUTPUT_DIR}"
    ;;
  pi05)
    POLICY_PATH="lerobot/pi05_base"
    POLICY_TYPE="pi05"
    BATCH_SIZE=64
    STEPS=60000
    SAVE_FREQ=2000
    CHUNK_SIZE=50
    N_ACTION_STEPS=50
    COMPILE_MODEL=true
    GRADIENT_CHECKPOINTING=true
    DTYPE=bfloat16
    SCHEDULER_DECAY_STEPS=3000
    EXTRA_ARGS="--policy.type=${POLICY_TYPE} --policy.pretrained_path=${POLICY_PATH} --policy.compile_model=${COMPILE_MODEL} --policy.gradient_checkpointing=${GRADIENT_CHECKPOINTING} --policy.dtype=${DTYPE} --policy.scheduler_decay_steps=${SCHEDULER_DECAY_STEPS}"
    ;;
  smolvla)
    POLICY_PATH="lerobot/smolvla_base"
    BATCH_SIZE=192
    STEPS=30000
    SAVE_FREQ=2000
    CHUNK_SIZE=50
    N_ACTION_STEPS=50
    RENAME_MAP='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'
    EXTRA_ARGS="--policy.path=${POLICY_PATH} --rename_map='${RENAME_MAP}'"
    ;;
  *)
    echo "Unknown model: $MODEL_NAME. Use: groot, pi05, or smolvla"
    exit 1
    ;;
esac

# can save at 2k but delete checkpoints before sending

# BATCH_SIZE=64
# STEPS=30000
# SAVE_FREQ=2000
# CHUNK_SIZE=50
# N_ACTION_STEPS=50

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_cs${CHUNK_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

echo "JOB_NAME: $JOB_NAME"


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
  --save_freq=${SAVE_FREQ} \
  --policy.chunk_size=${CHUNK_SIZE} \
  --policy.n_action_steps=${N_ACTION_STEPS}
