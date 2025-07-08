# import os
# import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# print(os.path.join(os.path.dirname(__file__), "src"))

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig

teleop_config = SO101LeaderConfig(
    port="/dev/ttyACM0",
    id="my_leader_arm2",
)

robot_config = SO101FollowerConfig(
    port="/dev/ttyACM1",
    id="my_follower_arm",
)


robot = SO101Follower(robot_config)
teleop_device = SO101Leader(teleop_config)
robot.connect()
teleop_device.connect()

while True:
    action = teleop_device.get_action()
    robot.send_action(action)
