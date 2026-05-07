#!/bin/bash

export HF_HOME="/mnt/0a56cc8f-eb63-4f04-b727-0615646b8bdb/HF_HOME"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

DATASET_REPO_ID="Rayen023/eval_pick-place-red-block_${TIMESTAMP}"

POLICY_PATH="/mnt/0a56cc8f-eb63-4f04-b727-0615646b8bdb/vla/agent_weights/groot_pick-place-red-block-all_bs120_20251129_052218_020000/pretrained_model"

SINGLE_TASK="Put the red lego block in the black cup"

# RENAME_MAP='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}' # required for smolvla
#  --dataset.rename_map="$RENAME_MAP"

# Press Right Arrow (→): Early stop the current episode or reset time and move to the next.
# Press Left Arrow (←): Cancel the current episode and re-record it.
# Press Escape (ESC): Immediately stop the session, encode videos, and upload the dataset.


uv run lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM1 \
  --robot.id=my_calibrated_follower_arm8 \
  --robot.cameras='{
    "front": {
      "type": "opencv",
      "index_or_path": 2,
      "fps": 30,
      "width": 640,
      "height": 480,
    },
    "wrist": {
      "type": "opencv",
      "index_or_path": 0,
      "fps": 30,
      "width": 640,
      "height": 480,
    }
  }' \
  --policy.path="$POLICY_PATH" \
  --policy.device=cuda \
  --dataset.single_task="$SINGLE_TASK" \
  --dataset.fps=30 \
  --dataset.episode_time_s=6000 \
  --dataset.reset_time_s=6000 \
  --dataset.num_episodes=10 \
  --dataset.video=true \
  --dataset.push_to_hub=false \
  --play_sounds=true \
  --display_data=false \
  --dataset.repo_id="$DATASET_REPO_ID" \
  


