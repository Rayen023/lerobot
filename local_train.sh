
# DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/pick-place-red-block-all"
# DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/pick-place-red-block-3"
# DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/original_groot_combined" #compare these 2 for smoothness
DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/fluid_groot_combined"  #compare these 2 for smoothness

# screen -L ./local_train.sh

# /mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/smolvla_base_pick-place-red-block-all_bs96_chunk50_20251206_183222/checkpoints/020000/pretrained_model
# /mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/smolvla_base_pick-place-red-block-all_bs96_chunk15_20251126_150932/checkpoints/020000/pretrained_model

BATCH_SIZE=96
STEPS=20000
SAVE_FREQ=2000
CHUNK_SIZE=16
N_ACTION_STEPS=16

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
MODEL_NAME="smolvla_base"
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_chunk${CHUNK_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/${JOB_NAME}"
POLICY_PATH="lerobot/smolvla_base" #change this to finetune my checkpoint
# POLICY_PATH="/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/smolvla_base_pick-place-red-block-all_bs96_chunk15_20251126_150932/checkpoints/020000/pretrained_model"
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
  --policy.chunk_size=${CHUNK_SIZE} \
  --policy.n_action_steps=${N_ACTION_STEPS} \
  # --policy.empty_cameras=1



DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/original_groot_combined" #compare these 2 for smoothness

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_ROOT")
MODEL_NAME="smolvla_base"
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_chunk${CHUNK_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/${JOB_NAME}"
POLICY_PATH="lerobot/smolvla_base" #change this to finetune my checkpoint
# POLICY_PATH="/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/weights/smolvla_base_pick-place-red-block-all_bs96_chunk15_20251126_150932/checkpoints/020000/pretrained_model"
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
  --policy.chunk_size=${CHUNK_SIZE} \
  --policy.n_action_steps=${N_ACTION_STEPS} \
  # --policy.empty_cameras=1



