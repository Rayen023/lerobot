from lerobot.common.robots import make_robot_from_config, so101_follower

config = so101_follower(
    port="COM8",
    id="so101_follower",
)

follower = make_robot_from_config(config)
follower.connect(calibrate=False)
follower.calibrate()
follower.disconnect()
