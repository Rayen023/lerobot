#!/bin/bash

# Configuration variables
SINGLE_TASK="Grab pens and place into pen holder"
POLICY_PATH="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/outputs/train/smolvla_base_youliangtan-so101-table-cleanup_bs64_lr0.0003_stps50000_20251101_163556/checkpoints/050000/pretrained_model"

# Extract model name from policy path (e.g., smolvla_base -> smolvla)
MODEL_NAME=$(basename $(dirname $(dirname ${POLICY_PATH})) | cut -d'_' -f1)

# Extract checkpoint number from policy path
CHECKPOINT=$(basename $(dirname ${POLICY_PATH}))

# Extract task from single_task description and create slug
# Convert to lowercase, take first few words, replace spaces with hyphens
TASK=$(echo "${SINGLE_TASK}" | awk '{print tolower($1"-"$2"-"$3)}' | sed 's/://g')

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
USERNAME="Rayen023"

# Generate dynamic dataset repo_id
DATASET_REPO_ID="${USERNAME}/eval_${MODEL_NAME}_${TASK}_ckpt${CHECKPOINT}_${TIMESTAMP}"

echo "Dataset will be saved to: ${DATASET_REPO_ID}"

uv run lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_calibrated_follower_arm8 \
  --robot.cameras="{wrist: {type: opencv, index_or_path: /dev/video0, width: 640, height: 480, fps: 30, color_mode: RGB}, front: {type: opencv, index_or_path: /dev/video2, width: 640, height: 480, fps: 30, color_mode: RGB}}" \
  --dataset.single_task="${SINGLE_TASK}" \
  --dataset.episode_time_s=100 \
  --dataset.num_episodes=1 \
  --dataset.push_to_hub=False \
  --policy.path=${POLICY_PATH} \
  --dataset.repo_id=${DATASET_REPO_ID} \
  --display_data=False \
  --dataset.rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}' \
  --policy.empty_cameras=1

