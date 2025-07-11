curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
removed     "pynput>=1.7.7",

source .venv/bin/activate

# line below needed in linux but not in compute canada envs
sudo apt-get install cmake build-essential python3-dev pkg-config libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev pkg-config

# python lerobot/scripts/train.py --policy.type=pi0 --dataset.repo_id=lerobot/stanford_kuka_multimodal_dataset


If i edit the calibration files in .cache it asks me to recalibrate !!

In calibration i should make sure the initial position of the 2 grippers are closed !!

Also make sure to do full movement with each motor !!
And a similar starting position for both leader and follower