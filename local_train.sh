
DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/pick-place-red-block-all"
# DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/pick-place-red-block-3"

BATCH_SIZE=96
STEPS=20000
SAVE_FREQ=2000

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
MODEL_NAME="smolvla_base"
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/${JOB_NAME}"
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
  --wandb.enable=true \
  --wandb.disable_artifact=true \
  --policy.push_to_hub=false \
  --save_freq=${SAVE_FREQ} \
  --policy.path="${POLICY_PATH}" \
  --rename_map="${RENAME_MAP}" \
  # --policy.empty_cameras=1


