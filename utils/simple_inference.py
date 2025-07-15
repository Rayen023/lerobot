#!/usr/bin/env python3
"""
Simple inference script that runs the lerobot.record command with specified parameters.
"""

import subprocess
import sys
import os
from datetime import datetime
import cv2
import threading

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
def show_camera_feed():
    """
    Display camera feeds from both cameras and wait for user to press 'q' to continue.
    This helps verify camera functionality before starting inference.
    """
    print("Opening camera feeds...")
    print("Press 'q' in any camera window to continue with inference")
    print("Press 'ESC' to exit without running inference")
    print("-" * 50)
    
    # Camera indices
    camera_indices = [0, 2]  # /dev/video0 and /dev/video2
    camera_names = ["wrist_view", "up_view"]
    
    # Try to open cameras
    caps = []
    for i, idx in enumerate(camera_indices):
        cap = cv2.VideoCapture(idx)
        if not cap.isOpened():
            print(f"Warning: Could not open camera {idx} ({camera_names[i]})")
            caps.append(None)
        else:
            print(f"Camera {idx} ({camera_names[i]}) opened successfully")
            caps.append(cap)
    
    # Check if at least one camera is working
    if all(cap is None for cap in caps):
        print("Error: No cameras could be opened!")
        return False
    
    try:
        while True:
            frames = []
            valid_cameras = []
            
            # Read frames from available cameras
            for i, cap in enumerate(caps):
                if cap is not None:
                    ret, frame = cap.read()
                    if ret:
                        # Resize frame for display
                        frame = cv2.resize(frame, (640, 480))
                        # Add camera label
                        cv2.putText(frame, f"{camera_names[i]} (/dev/video{camera_indices[i]})", 
                                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        frames.append(frame)
                        valid_cameras.append(i)
            
            # Display frames
            for i, frame in enumerate(frames):
                cv2.imshow(f"Camera {camera_indices[valid_cameras[i]]} - {camera_names[valid_cameras[i]]}", frame)
            
            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("User pressed 'q' - continuing with inference...")
                break
            elif key == 27:  # ESC key
                print("User pressed ESC - exiting...")
                return False
                
    except KeyboardInterrupt:
        print("\nCamera feed interrupted by user")
        return False
    finally:
        # Clean up
        for cap in caps:
            if cap is not None:
                cap.release()
        cv2.destroyAllWindows()
    
    return True

# POLICY_PATH_32BS_20k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla/checkpoints/last/pretrained_model" # failed 1/5
#POLICY_PATH_64BS_20k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_f009f8d1/checkpoints/last/pretrained_model" # failed 0/5
#POLICY_PATH_32BS_10k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs32_steps10000_20250714_153755/checkpoints/last/pretrained_model" # failed 0/5
POLICY_PATH_64BS_12k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs64_steps12000_20250714_185931/checkpoints/last/pretrained_model" # failed 0/5
#POLICY_PATH_64BS_40k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs64_steps40000_20250714_232250/checkpoints/last/pretrained_model"

def run_inference():
    # Generate timestamp-based identifier for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    TASK_DESCRIPTION = "Put the red lego block in the black cup"
    ROBOT_PORT = "/dev/ttyACM1"
    ROBOT_ID = "my_follower_arm_1"
    
    POLICY_PATH = POLICY_PATH_64BS_12k_steps
    EPISODE_TIME_SEC = 50  
    NUM_EPISODES = 5
    
    # Create informative dataset repo ID with timestamp
    task_name = TASK_DESCRIPTION.replace(' ', '_').lower()
    DATASET_REPO_ID = f"Rayen023_evals/eval_{task_name}_{timestamp}_{NUM_EPISODES}eps_{ROBOT_ID}_{ROBOT_PORT.split('/')[-1]}_POLICY{POLICY_PATH.split('/')[2]}"
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
        f"--dataset.episode_time_s={EPISODE_TIME_SEC}",
        f"--dataset.num_episodes={NUM_EPISODES}",
        "--dataset.push_to_hub=False",  # Prevent pushing to HuggingFace Hub
        f"--policy.path={POLICY_PATH}",
        f"--dataset.repo_id={DATASET_REPO_ID}",  # Add unique ID to repo name
        "--dataset.reset_time_s=10",  # Reset time between episodes
        "--display_data=True",  # Enable data display
        "--robot.calibration_dir=/home/recherche-a/.cache/huggingface/lerobot/calibration/robots/so101_follower",
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
    
    # Show camera feed before running inference
    if not show_camera_feed():
        sys.exit(1)
    
    exit_code = run_inference()
    sys.exit(exit_code)
