#!/usr/bin/env python
"""
Modern test bench script combining:
- Modern inference approach from inference.py (policy loading with preprocessor/postprocessor)
- All test bench features (CSV tracking, episode saving, YOLO detection, resume capability)
- Home base detection with 4-second timeout to automatically stop inference
"""

import torch
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.policies.factory import make_pre_post_processors, get_policy_class
from lerobot.configs.policies import PreTrainedConfig  
from lerobot.policies.utils import build_inference_frame, make_robot_action
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from PIL import Image
import time
import csv
from datetime import datetime
import os
import sys

# Add bench_test directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from view_saved_positions_matplotlib import view_position
except ImportError:
    print("Warning: view_saved_positions_matplotlib not found, using fallback")
    def view_position(pos_num):
        print(f"Displaying position {pos_num} (matplotlib view not available)")
        time.sleep(2)
import numpy as np
import json
import select
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO

# Initialize YOLO model for success detection
model = YOLO("bench_test/best.pt")

SEPARATOR = "\n" + "-"*50 + "\n"

# ============================================================================
# CONFIGURATION
# ============================================================================

# Model and policy configuration
TASK_DESCRIPTION = "Put the red lego block in the black cup"
MODEL_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_merged-pick-place-red-block-12_bs120_20251105_152519/checkpoints/002000/pretrained_model"

# Robot configuration
ROBOT_PORT = "/dev/ttyACM0"
ROBOT_ID = "my_calibrated_follower_arm8"

# Reset/home base position
RESET_POSITION = {
    "shoulder_pan.pos": -0.5882352941176521,
    "shoulder_lift.pos": -98.38983050847457,
    "elbow_flex.pos": 99.45627548708654,
    "wrist_flex.pos": 74.40347071583514,
    "wrist_roll.pos": 3.3943833943834107,
    "gripper.pos": 1.0575016523463316
}

# Inference parameters
SLEEP_BETWEEN_ACTIONS = 0.0  # 30 Hz = 1/30 seconds
HOME_BASE_TIMEOUT = 4.0  # Stop after 4 seconds in home base
HOME_BASE_THRESHOLD = 25.0  # Joint position threshold for home base detection

# Camera configuration
CAMERA_CONFIG = {
    "wrist": OpenCVCameraConfig(
        index_or_path="/dev/video2",
        width=640,
        height=480,
        fps=30,
        # color_mode=ColorMode.RGB
    ),
    "front": OpenCVCameraConfig(
        index_or_path="/dev/video0",
        width=640,
        height=480,
            fps=30,
            # color_mode=ColorMode.RGB
            )
        }

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_enter_pressed():
    """Check if Enter key has been pressed without blocking."""
    if select.select([sys.stdin], [], [], 0)[0]:
        sys.stdin.readline()
        return True
    return False


def is_in_home_base(position, threshold=HOME_BASE_THRESHOLD):
    """
    Check if robot is in home base position.
    
    Args:
        position: Dict of joint positions from observation
        threshold: Maximum deviation allowed for each joint
    
    Returns:
        True if all joints are within threshold of home position
    """
    for joint, pos in RESET_POSITION.items():
        if abs(position[joint] - pos) > threshold:
            return False
    return True


def save_args(args_file, model_path, task_description, sleep_between_actions, final_step):
    """Save current run arguments to JSON file for resume capability."""
    args = {
        "model_name": os.path.basename(model_path),
        "TASK_DESCRIPTION": task_description,
        "SLEEP_BETWEEN_ACTIONS": sleep_between_actions,
        "FINAL_STEP_OF_CURRENT_RUN": final_step
    }
    with open(args_file, 'w') as f:
        json.dump(args, f, indent=2)


def can_continue_run(args_file, model_path, task_description, sleep_between_actions, total_positions):
    """
    Check if we can continue from a previous run with matching parameters.
    
    Returns:
        tuple: (can_continue: bool, last_completed_step: int)
    """
    if not os.path.exists(args_file):
        return False, 0
    
    try:
        with open(args_file, 'r') as f:
            saved_args = json.load(f)
        
        # Check if all parameters match
        if (saved_args["model_name"] == os.path.basename(model_path) and
            saved_args["TASK_DESCRIPTION"] == task_description and
            saved_args["SLEEP_BETWEEN_ACTIONS"] == sleep_between_actions and
            saved_args["FINAL_STEP_OF_CURRENT_RUN"] < total_positions - 1):
            return True, saved_args["FINAL_STEP_OF_CURRENT_RUN"]
        else:
            return False, 0
    except Exception as e:
        print(f"Error reading args file: {e}")
        return False, 0


def find_latest_test_dir():
    """Find the most recent test_results directory."""
    base_path = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/gr00t_evals"
    os.makedirs(base_path, exist_ok=True)
    test_dirs = [d for d in os.listdir(base_path) 
                 if d.startswith('test_results_') and 
                 os.path.isdir(os.path.join(base_path, d))]
    if not test_dirs:
        return None
    return os.path.join(base_path, sorted(test_dirs)[-1])


def process_step(observation_dict, action_dict, timestamp, frame_index, episode_index, 
                index, task_index, wrist_write_path, front_write_path):
    """
    Process a single step: extract data and prepare for saving.
    
    Returns:
        tuple: (data_dict, image_buffer) for later saving
    """
    wrist_image = observation_dict['wrist']
    front_image = observation_dict['front']
    
    # Store paths and arrays for later saving
    image_buffer = {
        'wrist': (wrist_image, wrist_write_path),
        'front': (front_image, front_write_path)
    }
    
    # Extract action values
    action = [
        float(action_dict['shoulder_pan.pos']),
        float(action_dict['shoulder_lift.pos']),
        float(action_dict['elbow_flex.pos']),
        float(action_dict['wrist_flex.pos']),
        float(action_dict['wrist_roll.pos']),
        float(action_dict['gripper.pos'])
    ]
    
    # Extract observation state
    observation_state = [
        float(observation_dict['shoulder_pan.pos']),
        float(observation_dict['shoulder_lift.pos']),
        float(observation_dict['elbow_flex.pos']),
        float(observation_dict['wrist_flex.pos']),
        float(observation_dict['wrist_roll.pos']),
        float(observation_dict['gripper.pos'])
    ]
    
    data_dict = {
        "action": action,
        "observation.state": observation_state,
        "timestamp": float(timestamp),
        "frame_index": int(frame_index),
        "episode_index": int(episode_index),
        "index": int(index),
        "task_index": int(task_index)
    }
    
    return data_dict, image_buffer


def save_images_background(images_list, episode_num):
    """
    Save images in background thread with parallel execution.
    
    Args:
        images_list: List of image buffers to save
        episode_num: Episode number for logging
    """
    save_start = time.time()
    
    def save_image_pair(image_buffer):
        wrist_array, wrist_path = image_buffer['wrist']
        front_array, front_path = image_buffer['front']
        Image.fromarray(wrist_array).save(wrist_path)
        Image.fromarray(front_array).save(front_path)
    
    # Save 8 images in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(save_image_pair, images_list)
    
    save_time = time.time() - save_start
    print(f"\n[Background] Episode {episode_num}: Saved {len(images_list)} images in {save_time:.2f}s")


# ============================================================================
# MAIN TEST BENCH
# ============================================================================

def main():
    with open("bench_test/object_positions.csv", 'r') as f:
        total_positions = len(list(csv.DictReader(f)))
    
    base_path = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/gr00t_evals"
    os.makedirs(base_path, exist_ok=True)
    latest_dir = find_latest_test_dir()
    start_episode = 0
    continuing_run = False
    
    if latest_dir:
        args_file = f"{latest_dir}/args.json"
        can_continue, last_step = can_continue_run(
            args_file, MODEL_PATH, TASK_DESCRIPTION, 
            SLEEP_BETWEEN_ACTIONS, total_positions
        )
        
        if can_continue:
            print(f"Found previous run in {latest_dir}")
            print(f"Last completed episode: {last_step}")
            response = input("Continue from previous run? (y/n): ").strip().lower()
            
            if response == 'y':
                eval_dir = latest_dir
                start_episode = last_step + 1
                continuing_run = True
                print(f"Continuing from episode {start_episode}")
            else:
                eval_dir = os.path.join(base_path, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                print(f"Starting new run in {eval_dir}")
        else:
            eval_dir = os.path.join(base_path, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    else:
        eval_dir = os.path.join(base_path, f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    # Create directories
    os.makedirs(eval_dir, exist_ok=True)
    images_dir = f"{eval_dir}/images/"
    os.makedirs(images_dir, exist_ok=True)
    data_dir = f"{eval_dir}/data/"
    os.makedirs(data_dir, exist_ok=True)
    
    results_file = f"{eval_dir}/results.csv"
    args_file = f"{eval_dir}/args.json"
    
    # Initialize results file if new run
    if not continuing_run:
        with open(results_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['position_num', 'success', 'inference_time', 'comment', 
                           'yolo_predicted_class', 'yolo_confidence', 'stopped_by_home_base'])
        # Save initial args
        save_args(args_file, MODEL_PATH, TASK_DESCRIPTION, 
                 SLEEP_BETWEEN_ACTIONS, -1)
    
    print(f"Starting test bench with {total_positions} positions (starting from {start_episode})")
    print(f"Results will be saved to: {results_file}")
    print(SEPARATOR)
    
    # ============================================================================
    # INITIALIZE POLICY (Modern approach from inference.py)
    # ============================================================================
    
    print("Initializing policy...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load policy configuration
    policy_config = PreTrainedConfig.from_pretrained(MODEL_PATH)
    policy_config.device = str(device)
    
    # Load policy
    policy_cls = get_policy_class(policy_config.type)
    policy = policy_cls.from_pretrained(MODEL_PATH, config=policy_config)
    policy.to(device)
    policy.eval()
    
    # Create preprocessor and postprocessor
    preprocessor, postprocessor = make_pre_post_processors(
        policy.config,
        MODEL_PATH,
        preprocessor_overrides={"device_processor": {"device": str(device)}},
    )
    
    print("Policy initialized successfully!")
    
    # List to track background save threads
    save_threads = []
    
    # Global index counter across all episodes
    index = -1
    is_connected = False
    
    try:
        for episode_index in range(start_episode, total_positions):
            
            # Create directories for wrist and front camera images
            os.makedirs(f"{images_dir}/observation.images.wrist_view/episode_{episode_index:06d}", exist_ok=True)
            os.makedirs(f"{images_dir}/observation.images.front_view/episode_{episode_index:06d}", exist_ok=True)
            
            # Initialize list to store all frames for this episode
            episode_data = []
            # Initialize buffer for images to save later
            images_to_save = []
            
            print(f"\nTest {episode_index}/{total_positions}")
            print("Showing target position. Press 'q', 'escape', or 'Enter' to continue...")
            
            # Show the target position to user
            view_position(episode_index + 1)
            
            # ============================================================================
            # CREATE ROBOT (Fresh connection for each episode)
            # ============================================================================
            
            robot_config = SO101FollowerConfig(
                port=ROBOT_PORT,
                id=ROBOT_ID,
                cameras=CAMERA_CONFIG
            )
            
            robot = SO101Follower(robot_config)
            
            print("Connecting to robot...")
            robot.connect()
            is_connected = True
            
            # Build dataset features for this robot
            action_features = hw_to_dataset_features(robot.action_features, "action")
            obs_features = hw_to_dataset_features(robot.observation_features, "observation")
            dataset_features = {**action_features, **obs_features}
            
            print("Starting inference. Press Enter to stop manually...")
            start_time = time.time()
            
            # Home base detection variables
            home_base_start_time = None
            stopped_by_home_base = False
            
            try:
                frame_index = -1
                stop_inference = False
                
                while not stop_inference:
                    # Get observation
                    obs = robot.get_observation()
                    
                    # ============================================================================
                    # HOME BASE DETECTION (from inference.py)
                    # ============================================================================
                    
                    in_home = is_in_home_base(obs)
                    
                    if in_home:
                        if home_base_start_time is None:
                            home_base_start_time = time.time()
                            print("Robot entered home base, starting timer...")
                        else:
                            elapsed_time = time.time() - home_base_start_time
                            print(f"Time in home base: {elapsed_time:.1f}s / {HOME_BASE_TIMEOUT}s", end='\r')
                            
                            # Stop if robot has been in home base for timeout duration
                            if elapsed_time >= HOME_BASE_TIMEOUT:
                                print(f"\nRobot has been in home base for {HOME_BASE_TIMEOUT} seconds. Task completed!")
                                stopped_by_home_base = True
                                stop_inference = True
                                break
                    else:
                        # Reset timer if robot leaves home base
                        if home_base_start_time is not None:
                            print("\nRobot left home base, resetting timer.")
                        home_base_start_time = None
                    
                    # ============================================================================
                    # POLICY INFERENCE (Modern approach from inference.py)
                    # ============================================================================
                    
                    # Build observation frame with task description
                    obs_frame = build_inference_frame(
                        observation=obs,
                        ds_features=dataset_features,
                        device=device,
                        task=TASK_DESCRIPTION,
                        robot_type=robot.name
                    )
                    
                    # Preprocess observation
                    obs_preprocessed = preprocessor(obs_frame)
                    
                    # Get action from policy
                    action = policy.select_action(obs_preprocessed)
                    
                    # Postprocess action
                    action = postprocessor(action)
                    
                    # Convert to robot action format
                    action_dict = make_robot_action(action, dataset_features)
                    
                    # Send action to robot
                    robot.send_action(action_dict)
                    time.sleep(SLEEP_BETWEEN_ACTIONS)
                    
                    # Get observation after action
                    obs = robot.get_observation()
                    frame_index += 1
                    index += 1
                    
                    # ============================================================================
                    # PROCESS AND STORE DATA
                    # ============================================================================
                    
                    data_dict, image_buffer = process_step(
                        observation_dict=obs,
                        action_dict=action_dict,
                        timestamp=time.time() - start_time,
                        frame_index=frame_index,
                        episode_index=episode_index,
                        index=index,
                        task_index=0,
                        wrist_write_path=f"{images_dir}/observation.images.wrist_view/episode_{episode_index:06d}/frame_{frame_index:06d}.png",
                        front_write_path=f"{images_dir}/observation.images.front_view/episode_{episode_index:06d}/frame_{frame_index:06d}.png"
                    )
                    episode_data.append(data_dict)
                    images_to_save.append(image_buffer)
                    
                    # Check if Enter was pressed for manual stop
                    if is_enter_pressed():
                        print("\nStopping inference manually...")
                        stop_inference = True
                        break
            
            except KeyboardInterrupt:
                print("\nInterrupted by user during inference...")
            
            inference_time = time.time() - start_time
            print(f"Inference completed in {inference_time:.2f}s")
            
            # ============================================================================
            # CLEANUP ROBOT
            # ============================================================================
            
            print("Stopping robot...")
            try:
                robot.send_action(RESET_POSITION)
                time.sleep(1)
                robot.disconnect()
                # Destroy robot instance to free resources
                del robot
                time.sleep(1)
                
                is_connected = False
            except Exception as e:
                print(f"Error stopping robot or disconnecting: {e}")
            
            # ============================================================================
            # SAVE DATA IN BACKGROUND
            # ============================================================================
            
            print(f"Queueing {len(images_to_save)} frames for background saving...")
            
            # Start background thread for image saving
            save_thread = threading.Thread(
                target=save_images_background, 
                args=(images_to_save.copy(), episode_index),
                daemon=False
            )
            save_thread.start()
            save_threads.append(save_thread)
            
            print(f"Images queued for saving, continuing...")
            
            # Save all episode data to a single JSON file
            episode_file = f"{data_dir}/episode_{episode_index:06d}.json"
            try:
                with open(episode_file, 'w') as f:
                    json.dump(episode_data, f, indent=2)
                print(f"Saved episode data to {episode_file} ({len(episode_data)} frames)")
            except Exception as e:
                print(f"Error saving episode data: {e}")
            
            # ============================================================================
            # YOLO DETECTION
            # ============================================================================
            
            # Run YOLO inference on the last front view frame
            predicted_class = -1
            confidence = 0.0
            if 'obs' in locals() and 'front' in obs:
                last_front_frame = obs['front']
                yolo_result = model(last_front_frame, verbose=False)[0]
                predicted_class = yolo_result.probs.top1
                confidence = yolo_result.probs.top1conf.item()
                print(f"YOLO Predicted class: {predicted_class}, Confidence: {confidence:.4f}")
            
            # ============================================================================
            # USER INPUT AND SAVE RESULTS
            # ============================================================================
            
            result = input("Result (s=success, f=failure): ").strip().lower()
            success = 1 if result == 's' else 0
            
            comment = input("Comment: ").strip()
            
            # Save results to CSV
            with open(results_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([episode_index, success, f"{inference_time:.2f}", comment, 
                               predicted_class, f"{confidence:.4f}", stopped_by_home_base])
            
            # Update args.json with the latest completed episode
            save_args(args_file, MODEL_PATH, TASK_DESCRIPTION, 
                     SLEEP_BETWEEN_ACTIONS, episode_index)
            
            print(f"Recorded: Success={success}, Time={inference_time:.2f}s, " +
                  f"Home base stop={stopped_by_home_base}")
            
        # ============================================================================
        # FINAL SUMMARY
        # ============================================================================
        
        print(SEPARATOR)
        print("Test bench complete!")
        print(f"Results saved to: {results_file}")
        
        with open(results_file, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            successes = sum(1 for r in results if r['success'] == '1')
            home_base_stops = sum(1 for r in results if r['stopped_by_home_base'] == 'True')
            total_time = sum(float(r['inference_time']) for r in results)
            avg_time = total_time / len(results) if results else 0
        
        print(f"\nSummary:")
        print(f"Success Rate: {successes}/{len(results)} ({successes/len(results)*100:.1f}%)")
        print(f"Average Inference Time: {avg_time:.2f}s")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Stopped by home base: {home_base_stops}/{len(results)}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user, stopping test bench...")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Stopping test bench...")
    finally:
        print("Cleaning up...")
        
        # Wait for all background save operations to complete
        if save_threads:
            print(f"Waiting for {len(save_threads)} background save operations to complete...")
            for i, thread in enumerate(save_threads, 1):
                thread.join()
                print(f"  Completed {i}/{len(save_threads)} save operations")
        
        # Cleanup robot if still connected
        if is_connected:
            try:
                print("Resetting robot position...")
                if 'robot' in locals():
                    robot.send_action(RESET_POSITION)
                    time.sleep(1)
            except Exception as e:
                print(f"Error resetting robot: {e}")
            try:
                print("Disconnecting from robot...")
                if 'robot' in locals():
                    robot.disconnect()
            except Exception as e:
                print(f"Error disconnecting: {e}")
        
        print("Test bench exited.")


if __name__ == "__main__":
    main()
