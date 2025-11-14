TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

SINGLE_TASK="Put the red lego block in the black cup"
DATASET_NAME="red-block-1_${TIMESTAMP}"

DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/Rayen023/${DATASET_NAME}"
DATASET_REPO_ID="Rayen023/${DATASET_NAME}"

echo "Recording task: $SINGLE_TASK"
echo "Dataset: $DATASET_NAME"

uv run lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_calibrated_follower_arm8 \
  --robot.cameras='{
    "front": {
      "type": "opencv",
      "index_or_path": 0,
      "fps": 30,
      "width": 640,
      "height": 480,
    },
    "wrist": {
      "type": "opencv",
      "index_or_path": 2,
      "fps": 30,
      "width": 640,
      "height": 480,
    }
  }' \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=my_leader_arm_1 \
  --dataset.repo_id="$DATASET_REPO_ID" \
  --dataset.root="$DATASET_ROOT" \
  --dataset.single_task="$SINGLE_TASK" \
  --dataset.fps=30 \
  --dataset.episode_time_s=60 \
  --dataset.reset_time_s=600 \
  --dataset.num_episodes=150 \
  --dataset.video=true \
  --dataset.push_to_hub=false \
  --play_sounds=true \
  --display_data=false \
  # --resume=true

echo "Recording completed for task: $SINGLE_TASK"
