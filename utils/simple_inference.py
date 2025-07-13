#!/usr/bin/env python3
"""
Simple inference script that runs the lerobot.record command with specified parameters.
"""

import subprocess
import sys
import os
import uuid

# camera_config = {
#     "wrist_view": OpenCVCameraConfig(
#         index_or_path="/dev/video0",
#         fps=30,
#         width=640,
#         height=480,
#         color_mode=ColorMode.BGR,
#         rotation=Cv2Rotation.NO_ROTATION,
#     ),
#     "up_view": OpenCVCameraConfig(
#         index_or_path="/dev/video2",
#         fps=30,
#         width=640,
#         height=480,
#         color_mode=ColorMode.BGR,
#         rotation=Cv2Rotation.NO_ROTATION,
#     ),
# }


# teleop_config = SO101LeaderConfig(
#     port="/dev/ttyACM0",
#     id="my_leader_arm_1",
# )

# robot_config = SO101FollowerConfig(
#     port="/dev/ttyACM1",
#     id="my_follower_arm_1",
#     cameras=camera_config,
# )
def run_inference():
    # Generate unique identifier for this run
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
    
    TASK_DESCRIPTION = "Put the candy in the black cup"
    ROBOT_PORT = "/dev/ttyACM1"
    ROBOT_ID = "my_follower_arm_1"
    POLICY_PATH = "outputs/train/so101_follower_put_the_candy_in_the_black_cup_b570d9_smolvla/checkpoints/003333/pretrained_model"
    
    # Camera configuration as a JSON string
    camera_config = '{"wrist_view": {"type": "opencv", "index_or_path": "/dev/video0", "width": 640, "height": 480, "fps": 30}, "up_view": {"type": "opencv", "index_or_path": "/dev/video2", "width": 640, "height": 480, "fps": 30}}'
    
    # Build the command
    cmd = [
        "python", "-m", "lerobot.record",
        "--robot.type=so101_follower",
        f"--robot.port={ROBOT_PORT}",
        f"--robot.id={ROBOT_ID}",
        f"--robot.cameras={camera_config}",
        f"--dataset.single_task={TASK_DESCRIPTION}",
        "--dataset.episode_time_s=10",
        "--dataset.num_episodes=1",
        "--dataset.push_to_hub=False",  # Prevent pushing to HuggingFace Hub
        f"--policy.path={POLICY_PATH}",
        f"--dataset.repo_id=Rayen023_evals/eval_candy_cup_task_test_{unique_id}",  # Add unique ID to repo name
    ]
    
    print("Running inference command:")
    print(" ".join(cmd))
    print(f"Unique run ID: {unique_id}")
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
