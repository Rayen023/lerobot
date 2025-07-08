from lerobot.common.teleoperators import make_teleoperator_from_config, so101_leader

config = so101_leader(
    port="COM7",
    id="so101_leader",
)

leader = make_teleoperator_from_config(config)
leader.connect(calibrate=False)
leader.calibrate()
leader.disconnect()


"""
# First, run setup_motors to configure motor IDs (connect each motor individually):
python -m lerobot.setup_motors --teleop.type so101_leader --teleop.port COM7

# Then, run calibration after motors are properly configured:
python -m lerobot.calibrate --teleop.type so101_leader --teleop.port COM7 --teleop.id so101_leader_1

# Follower commands:
python -m lerobot.calibrate --robot.type so101_follower --robot.port COM8 --robot.id so101_follower_1
"""
#  C:\Users\rayen\.cache\huggingface\lerobot\calibration\teleoperators\so101_leader\so101_leader_1.json
