from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.utils import hw_to_dataset_features
from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig
from lerobot.teleoperators.so101_leader import SO101Leader, SO101LeaderConfig
from lerobot.teleoperators.so100_leader.config_so100_leader import SO100LeaderConfig
from lerobot.teleoperators.so100_leader.so100_leader import SO100Leader
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say
from lerobot.utils.visualization_utils import _init_rerun
from lerobot.record import record_loop
from lerobot.cameras.configs import CameraConfig, ColorMode, Cv2Rotation
from datetime import datetime


EPISODES_PER_TASK = 50
FPS = 30
EPISODE_TIME_SEC = 30
RESET_TIME_SEC = 10

# Define 4 tasks for cup and lego block combinations (mismatched colors)
TASKS = [
    "Put the red lego block in the white cup",
    "Put the red lego block in the black cup", 
    "Put the yellow lego block in the white cup",
    "Put the yellow lego block in the black cup"
]

# Total episodes will be EPISODES_PER_TASK * number of tasks
TOTAL_EPISODES = EPISODES_PER_TASK * len(TASKS)

# Create the robot and teleoperator configurations
camera_config = {
    "wrist_view": OpenCVCameraConfig(
        index_or_path="/dev/video0",
        fps=30,
        width=640,
        height=480,
        color_mode=ColorMode.RGB,
        rotation=Cv2Rotation.NO_ROTATION,
    ),
    "up_view": OpenCVCameraConfig(
        index_or_path="/dev/video2",
        fps=30,
        width=640,
        height=640,
        color_mode=ColorMode.RGB,
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


# Initialize the robot and teleoperator
robot = SO101Follower(robot_config)
teleop = SO101Leader(teleop_config)

# Configure the dataset features
action_features = hw_to_dataset_features(robot.action_features, "action")
obs_features = hw_to_dataset_features(robot.observation_features, "observation")
dataset_features = {**action_features, **obs_features}

# Generate timestamp-based repo ID with informative naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Use "multitask" in the repo name since we have multiple tasks
repo_id = f"Rayen023/{robot.name.lower()}_multitask_eps{TOTAL_EPISODES}_fps{FPS}_{timestamp}"

print(f"Robot: {robot.name.lower()}")
print(f"Tasks to record: {TASKS}")
print(f"Episodes per task: {EPISODES_PER_TASK}")
print(f"Total episodes: {TOTAL_EPISODES}, FPS: {FPS}")
print(f"Repo ID: {repo_id}")
print(f"Timestamp: {timestamp}")

print(f"\n=== Recording Schedule ===")
for i, task in enumerate(TASKS):
    start_ep = i * EPISODES_PER_TASK + 1
    end_ep = (i + 1) * EPISODES_PER_TASK
    print(f"Episodes {start_ep:3d}-{end_ep:3d}: {task}")
print("=" * 50)

# Create the dataset
dataset = LeRobotDataset.create(
    repo_id=repo_id,
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
)

# Initialize the keyboard listener and rerun visualization
_, events = init_keyboard_listener()
_init_rerun(session_name="recording")

# Connect the robot and teleoperator
robot.connect()
teleop.connect()

episode_idx = 0
while episode_idx < TOTAL_EPISODES and not events["stop_recording"]:
    # Determine which task we're currently recording based on episode blocks
    current_task_index = episode_idx // EPISODES_PER_TASK
    current_task = TASKS[current_task_index]
    
    # Calculate episode number within the current task block
    episode_in_task = (episode_idx % EPISODES_PER_TASK) + 1
    
    log_say(f"Recording episode {episode_idx + 1} of {TOTAL_EPISODES}")
    log_say(f"Task {current_task_index + 1}/{len(TASKS)}: {current_task}")
    log_say(f"Episode {episode_in_task}/{EPISODES_PER_TASK} for this task")

    # Episode recording phase starts
    log_say(f"EPISODE RECORDING START - {EPISODE_TIME_SEC} seconds")
    record_loop(
        robot=robot,
        events=events,
        fps=FPS,
        teleop=teleop,
        dataset=dataset,
        control_time_s=EPISODE_TIME_SEC,
        single_task=current_task,
        display_data=True,
    )
    log_say(f"EPISODE RECORDING END - Episode {episode_idx + 1} completed")

    # Reset the environment if not stopping or re-recording
    if not events["stop_recording"] and (episode_idx < TOTAL_EPISODES - 1 or events["rerecord_episode"]):
        log_say("Reset the environment")
        
        # Reset phase starts
        log_say(f"RESET PHASE START - {RESET_TIME_SEC} seconds")
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop=teleop,
            control_time_s=RESET_TIME_SEC,
            single_task="Reset environment to initial state",  # Generic reset task
            display_data=True,
        )
        log_say(f"RESET PHASE END - Reset completed")

    if events["rerecord_episode"]:
        log_say("Re-recording episode")
        events["rerecord_episode"] = False
        events["exit_early"] = False
        dataset.clear_episode_buffer()
        continue

    dataset.save_episode()
    episode_idx += 1

# Clean up
log_say("Stop recording")
robot.disconnect()
teleop.disconnect()
#dataset.push_to_hub()