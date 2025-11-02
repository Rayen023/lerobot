DATASET_REPO_ID=""


# You can record one task at a time by commenting out the others
# TASKS=(
#   "Grab pens and place into pen holder"
#   "Grab markers and place into pen holder"
#   "Grab tapes and place into pen holder"
#   "Grab scissor and place into pen holder"
# )

# # Select which task to record (0-3)
# TASK_INDEX=1
# SINGLE_TASK="${TASKS[$TASK_INDEX]}"
SINGLE_TASK="Sort the blocks by color: move all blue ones in the blue container and the green ones in the white container"

DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/Rayen023/sort-blocks"
DATASET_REPO_ID="Rayen023/sort-blocks"

echo "Recording task: $SINGLE_TASK"

# Camera configuration (matching the dataset)
# Adjust the camera indices (/dev/video0, /dev/video2, etc.) to match your setup
# Note: Camera keys should be simple names (e.g., "front", "wrist"), not full paths
uv run lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_calibrated_follower_arm8 \
  --robot.cameras='{
    "front": {
      "type": "opencv",
      "index_or_path": 2,
      "fps": 30,
      "width": 640,
      "height": 480,
      "rotation": 0
    },
    "wrist": {
      "type": "opencv",
      "index_or_path": 0,
      "fps": 30,
      "width": 640,
      "height": 480,
      "rotation": 0
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
  --dataset.reset_time_s=60 \
  --dataset.num_episodes=30 \
  --dataset.video=true \
  --dataset.push_to_hub=false \
  --play_sounds=true \
  --display_data=false \
  --resume=true

echo "Recording completed for task: $SINGLE_TASK"
