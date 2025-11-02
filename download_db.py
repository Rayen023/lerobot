from lerobot.datasets.lerobot_dataset import LeRobotDataset
    
dataset = LeRobotDataset("youliangtan/so101-table-cleanup", root="so101-table-cleanup-local")

#uv run python -m lerobot.datasets.v30.convert_dataset_v21_to_v30 --repo-id=youliangtan/so101-table-cleanup --root=so101-table-cleanup-local --push-to-hub=false