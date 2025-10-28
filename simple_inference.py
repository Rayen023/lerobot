#!/usr/bin/env python3
"""
Simple inference script that runs the lerobot.record command with specified parameters.
"""

import subprocess
import sys
from datetime import datetime

# POLICY_PATH_32BS_20k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla/checkpoints/last/pretrained_model" # failed 1/5
#POLICY_PATH_64BS_20k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_f009f8d1/checkpoints/last/pretrained_model" # failed 0/5
#POLICY_PATH_32BS_10k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs32_steps10000_20250714_153755/checkpoints/last/pretrained_model" # failed 0/5
POLICY_PATH_64BS_12k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs64_steps12000_20250714_185931/checkpoints/last/pretrained_model" # failed 0/5
#POLICY_PATH_64BS_40k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs64_steps40000_20250714_232250/checkpoints/last/pretrained_model"
POLICY_PATH_4_ACTIONS_25CHUNKS_AUGMENTED = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs64_steps15000_20250715_121250/checkpoints/last/pretrained_model" # failed 5/5
POLICY_100EPS = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250715_123150_smolvla_bs64_steps20000_20250715_150957/checkpoints/last/pretrained_model" # failed 0/5
POLICY_100EPS_PRETRAINED = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250715_123150_smolvla_bs64_steps20000_20250715_190951/checkpoints/last/pretrained_model"
POLICY_LARGER_BLOCK_PRETAINED = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250716_113612_smolvla_bs64_steps20000_20250716_122951/checkpoints/last/pretrained_model"
POLICY_100EPS_LARGER_BLOCK = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250716_113612_smolvla_bs64_steps12000_20250716_162552/checkpoints/last/pretrained_model"
POLICY_100EPS_2k_32_LARGER_BLOCK = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250716_113612_smolvla_bs64_steps2000_20250716_192154/checkpoints/last/pretrained_model"
COMBINED_POLICY = "outputs/train/combined_so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_smolvla_bs64_steps12000_20250716_213706/checkpoints/last/pretrained_model"
COMBINED_POLICY_82BS_8k_Steps = "outputs/train/combined_so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_smolvla_bs82_steps8000_20250717_105752/checkpoints/008000/pretrained_model"
# python src/lerobot/processor/migrate_policy_normalization.py --pretrained-path outputs/train/combined_so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_smolvla_bs64_steps12000_20250716_213706/checkpoints/last/pretrained_model
def run_inference():
    # Generate timestamp-based identifier for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    TASK_DESCRIPTION = "Put the red lego block in the black cup"
    ROBOT_PORT = "/dev/ttyACM0"
    ROBOT_ID = "my_calibrated_follower_arm8"
    
    #POLICY_PATH = COMBINED_POLICY
    POLICY_PATH = "outputs/train/combined_so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_smolvla_bs64_steps12000_20250716_213706/checkpoints/last/pretrained_model_migrated"
    EPISODE_TIME_SEC = 1000  
    NUM_EPISODES = 5
    
    # Create informative dataset repo ID with timestamp
    task_name = TASK_DESCRIPTION.replace(' ', '_').lower()
    DATASET_REPO_ID = f"Rayen023_evals/eval_{task_name}_{timestamp}_{NUM_EPISODES}eps_{ROBOT_ID}_{ROBOT_PORT.split('/')[-1]}_POLICY{POLICY_PATH.split('/')[2]}"
    # Camera configuration as a JSON string
    camera_config = '{"wrist_view": {"type": "opencv", "index_or_path": "/dev/video1", "width": 640, "height": 480, "fps": 30, "rotation": ROTATE_180}, "up_view": {"type": "opencv", "index_or_path": "/dev/video2", "width": 800, "height": 600, "fps": 20, "rotation": NO_ROTATION}}'
    # Build the command
    
    cmd = [
        "lerobot-record",
        "--robot.type=so101_follower",
        f"--robot.port={ROBOT_PORT}",
        f"--robot.id={ROBOT_ID}",
        f"--robot.cameras={camera_config}",
        f"--dataset.single_task={TASK_DESCRIPTION}",
        f"--dataset.episode_time_s={EPISODE_TIME_SEC}",
        f"--dataset.num_episodes={NUM_EPISODES}",
        "--dataset.push_to_hub=False",  # Prevent pushing to HuggingFace Hub
        f"--policy.path={POLICY_PATH}",
        f"--dataset.repo_id={DATASET_REPO_ID}",  # Add unique ID to repo name
        "--dataset.reset_time_s=10",  # Reset time between episodes
        "--display_data=True",  # Enable data display
        "--robot.calibration_dir=/home/recherche-a/.cache/huggingface/lerobot/calibration/robots/so101_follower",
        #"--teleop.port=/dev/ttyACM0",  # Teleoperator port
        #"--teleop.id=my_leader_arm_1",  # Teleoperator ID
        #"--teleop.type=so101_leader",  # Teleoperator type
    ]
    # TODO : No policy or teleoperator provided, skipping action generation.This is likely to happen when resetting the environment without a teleop device.The robot won't be at its rest position at the start of the next episode.
    print("Running inference command:")
    print(" ".join(cmd))
    print(f"Timestamp: {timestamp}")
    print(f"Task: {TASK_DESCRIPTION}")
    print("\n" + "="*50 + "\n")
    
    try:
        # Run the command
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\nInference completed successfully with return code: {result.returncode}")
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"Error running inference: {e}")
        print(f"Return code: {e.returncode}")
        return e.returncode
        
    except KeyboardInterrupt:
        print("\nInference interrupted by user")
        return 1
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    print("Starting LeRobot inference...")
    print(f"Task: Put the candy in the grey black cup")
    print(f"Robot Port: /dev/ttyACM1")
    print(f"Teleop Port: /dev/ttyACM0")
    print(f"Cameras: wrist_view (/dev/video0), up_view (/dev/video2)")
    print(f"Policy: outputs/train/so101_follower_put_the_candy_in_the_black_cup_b570d9_smolvla/checkpoints/last/pretrained_model")
    print("-" * 50)
        
    exit_code = run_inference()
    sys.exit(exit_code)
