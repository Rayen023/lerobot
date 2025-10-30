#!/usr/bin/env python

import torch
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.cameras.configs import Cv2Rotation
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.utils import build_inference_frame, make_robot_action
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.cameras.configs import ColorMode, Cv2Rotation
from PIL import Image
import time

TASK_DESCRIPTION = "Put the red lego block in the black cup"
ROBOT_PORT = "/dev/ttyACM0"
ROBOT_ID = "my_calibrated_follower_arm8"
#MODEL_PATH = "outputs/train/combined_cleaned_smolvla_bs64_steps20000_20251028_085626/checkpoint_15000" failed miserably
MODEL_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/smolvla_models/combined_cleaned_smolvla_bs64_steps50000_20251028_172519/checkpoint_20000"
camera_config = {
    "wrist_view": OpenCVCameraConfig(
        index_or_path="/dev/video1",
        width=640,
        height=480,
        fps=30,
        color_mode=ColorMode.RGB,
        rotation=Cv2Rotation.ROTATE_180
    ),
    "up_view": OpenCVCameraConfig(
        index_or_path="/dev/video2",
        width=800,
        height=600,
        fps=20,
        color_mode=ColorMode.RGB,
        rotation=Cv2Rotation.NO_ROTATION
    )
}

robot_config = SO101FollowerConfig(port=ROBOT_PORT, id=ROBOT_ID, cameras=camera_config)
robot = SO101Follower(robot_config)
robot.connect()


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


policy = SmolVLAPolicy.from_pretrained(MODEL_PATH)
policy.to(device)
policy.eval()

preprocessor, postprocessor = make_pre_post_processors(
    policy.config,
    MODEL_PATH,
    preprocessor_overrides={"device_processor": {"device": str(device)}},
)


action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

try:
    while True:
        obs = robot.get_observation()
        # Image.fromarray(obs["wrist_view"]).save(f"outputs/last_observation/wrist_view.png")
        # Image.fromarray(obs["up_view"]).save(f"outputs/last_observation/up_view.png")

        
        obs_frame = build_inference_frame(
            observation=obs,
            ds_features=dataset_features,
            device=device,
            task=TASK_DESCRIPTION,
            robot_type=robot.name
        )
        obs = preprocessor(obs_frame)
        #action_chunk = policy._get_action_chunk(obs)
        
        # _, chunk_size, _ = action_chunk.shape
        # for i in range(chunk_size):
        #     single_action = action_chunk[:, i, :]
        #     action = postprocessor(single_action)
        #     action = make_robot_action(action, dataset_features)
        #     time.sleep(1/30)  
        #     robot.send_action(action)
        action = policy.select_action(obs)
        action = postprocessor(action)
        action = make_robot_action(action, dataset_features)
        #time.sleep(1/30)  
        robot.send_action(action)
        

except (KeyboardInterrupt, Exception) as e:
    print(f"\nStopping inference: {e if not isinstance(e, KeyboardInterrupt) else 'Keyboard interrupt'}")
finally:
    robot.disconnect()
    print("Robot disconnected safely.")


