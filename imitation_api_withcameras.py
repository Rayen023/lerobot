import cv2
import numpy as np

from lerobot.cameras.configs import CameraConfig, ColorMode, Cv2Rotation
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

camera_config = {
    "wrist_view": OpenCVCameraConfig(
        index_or_path="/dev/video0",
        fps=30,
        width=640,
        height=480,
        color_mode=ColorMode.BGR,
        rotation=Cv2Rotation.NO_ROTATION,
    ),
    "up_view": OpenCVCameraConfig(
        index_or_path="/dev/video2",
        fps=20,
        width=640,
        height=480,
        color_mode=ColorMode.BGR,
        rotation=Cv2Rotation.NO_ROTATION,
    ),
}


teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM0",
    id="my_leader_arm_1",
)

robot_config = SO101FollowerConfig(
    port="/dev/ttyACM1",
    id="my_follower_arm_1",
    cameras=camera_config,
)


robot = SO101Follower(robot_config)
teleop_device = SO101Leader(teleop_config)
robot.connect()
teleop_device.connect()

observation = robot.get_observation()
for key, value in observation.items():
    if isinstance(value, list):
        print(f"{key}: {len(value)} items")
    else:
        print(f"{key}: {value}")

print(observation["wrist_view"].shape)  # (480, 640, 3)
print(observation["up_view"].shape)  # (480, 640, 3)

while True:
    observation = robot.get_observation()

    # Get camera images (already processed with correct colors and rotation)
    wrist_view = observation["wrist_view"]
    up_view = observation["up_view"]

    # Display the images
    cv2.imshow("Wrist View", wrist_view)
    cv2.imshow("Up View", up_view)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    action = teleop_device.get_action()
    robot.send_action(action)

# Clean up
cv2.destroyAllWindows()
