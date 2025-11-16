TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# DATASET_REPO_ID="Rayen023/sort-blocks-3_${TIMESTAMP}"
# DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/${DATASET_REPO_ID}"

DATASET_REPO_ID="Rayen023/sort-blocks-3_20251114_191052"
DATASET_ROOT="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/Rayen023/sort-blocks-3_20251114_191052"

SINGLE_TASK="Sort the blocks by color move all blue ones in the blue container and the green ones in the white container"

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
  --dataset.episode_time_s=600 \
  --dataset.reset_time_s=600 \
  --dataset.num_episodes=20 \
  --dataset.video=true \
  --dataset.push_to_hub=false \
  --play_sounds=true \
  --display_data=false \
  --resume=true