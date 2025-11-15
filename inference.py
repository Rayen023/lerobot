#!/usr/bin/env python

import torch
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import Cv2Rotation
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.policies.factory import make_pre_post_processors, get_policy_class
from lerobot.configs.policies import PreTrainedConfig  
from lerobot.policies.utils import build_inference_frame, make_robot_action
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
from PIL import Image
import time

# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_merged-so101-table-cleanup_bs120_20251103_204808/checkpoints/021000/pretrained_model" #good
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks_bs120_20251103_204808/checkpoints/021000/pretrained_model"
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/smolvla_base_merged-so101-table-cleanup_bs192_20251103_205130/checkpoints/009000/pretrained_model"
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_original_resized_rotated_cleaned_bs120_20251103_204808/checkpoints/003000/pretrained_model"
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/smolvla_base_sort-blocks_bs192_20251103_205623/checkpoints/009000/pretrained_model"

# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251109_135733/checkpoints/008000/pretrained_model" #good at picking up blocks but made errors on which container to put in
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251109_135733/checkpoints/004000/pretrained_model" #can pick up but cant make decisions and slow
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251109_135733/checkpoints/012000/pretrained_model" # works but slow and makes errors
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251109_135733/checkpoints/040000/pretrained_model" #works made 1 error and needed a bit of help
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251109_135733/checkpoints/028000/pretrained_model" #meeh
POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251109_135733/checkpoints/034000/pretrained_model" #good good works made 1 error and needed a bit of help 

# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks_bs120_20251109_135718/checkpoints/008000/pretrained_model" #awfull
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_merged-sort-blocks-123_bs120_20251105_215209/checkpoints/012000/pretrained_model" #awfull
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_merged-sort-blocks-123_bs120_20251105_222024/checkpoints/024000/pretrained_model"  #awfull
# POLICY_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/groot_n1.5_sort-blocks-2_bs120_20251106_174101/checkpoints/010000/pretrained_model" #good at sorting but not as good in picking up the blocks

# Task description mapping
TASK_DESCRIPTIONS = {
    "blocks": "Sort the blocks by color move all blue ones in the blue container and the green ones in the white container",
    "table": "Grab pens and place into pen holder",
    "pens": "Grab pens and place into pen holder",
    "red": "Put the red lego block in the black cup",
    "lego": "Put the red lego block in the black cup",
    "original": "Put the red lego block in the black cup"
}

TASK_DESCRIPTION = next((desc for keyword, desc in TASK_DESCRIPTIONS.items() if keyword in POLICY_PATH), "")
print(f"Using task description: {TASK_DESCRIPTION}")

ROBOT_PORT = "/dev/ttyACM0"
ROBOT_ID = "my_calibrated_follower_arm8"

camera_config = {
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

RESET_POSITION = {"shoulder_pan.pos": -0.5882352941176521,
"shoulder_lift.pos": -98.38983050847457,
"elbow_flex.pos": 99.45627548708654,
"wrist_flex.pos": 74.40347071583514,
"wrist_roll.pos": 3.3943833943834107,
"gripper.pos": 1.0575016523463316}

def is_in_home_base(position, threshold=25.0):
    for joint, pos in RESET_POSITION.items():
        if abs(position[joint] - pos) > threshold:
            # print("-"*20)
            return False
    # print("Robot is in home base")
    return True

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

policy_config = PreTrainedConfig.from_pretrained(POLICY_PATH)
policy_config.device = str(device)

policy_cls = get_policy_class(policy_config.type)

policy = policy_cls.from_pretrained(POLICY_PATH, config=policy_config)
policy.to(device)
policy.eval()

preprocessor, postprocessor = make_pre_post_processors(
    policy.config,
    POLICY_PATH,
    preprocessor_overrides={"device_processor": {"device": str(device)}},
)

try:
    robot_config = SO101FollowerConfig(port=ROBOT_PORT, id=ROBOT_ID, cameras=camera_config)
    robot = SO101Follower(robot_config)
    robot.connect()

    
    action_features = hw_to_dataset_features(robot.action_features, "action")
    obs_features = hw_to_dataset_features(robot.observation_features, "observation")
    dataset_features = {**action_features, **obs_features}

    home_base_start_time = None
    HOME_BASE_TIMEOUT = 4.0  
    obs = robot.get_observation()
    Image.fromarray(obs["wrist"]).save(f"outputs/captured_images_during_inference/wrist_camera.jpg")
    Image.fromarray(obs["front"]).save(f"outputs/captured_images_during_inference/front_camera.jpg")

    while True:
        obs = robot.get_observation()
        in_home = is_in_home_base(obs)
        
        if in_home:
            if home_base_start_time is None:
                home_base_start_time = time.time()
                # print("Robot entered home base, starting timer...")
            else:
                elapsed_time = time.time() - home_base_start_time
                # print(f"Time in home base: {elapsed_time:.1f}s / {HOME_BASE_TIMEOUT}s")
                # if elapsed_time >= HOME_BASE_TIMEOUT:
                    # print(f"Robot has been in home base for {HOME_BASE_TIMEOUT} seconds. Task completed!")
                    #break
        else:
            if home_base_start_time is not None:
                print("Robot left home base, resetting timer.")
            home_base_start_time = None

        obs_frame = build_inference_frame(
            observation=obs,
            ds_features=dataset_features,
            device=device,
            task=TASK_DESCRIPTION,
            robot_type=robot.name
        )
        obs = preprocessor(obs_frame)
        
        
        
        action = policy.select_action(obs)
        action = postprocessor(action)
        action = make_robot_action(action, dataset_features)
        robot.send_action(action)
        time.sleep(1/30)
        
        

except (KeyboardInterrupt, Exception) as e:
    print(f"\nStopping inference: {e if not isinstance(e, KeyboardInterrupt) else 'Keyboard interrupt'}")
finally:
    if robot.is_connected:
        robot.send_action(RESET_POSITION)
        time.sleep(1)
        robot.disconnect()
        print("Robot disconnected safely.")


