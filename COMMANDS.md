### lerobot commands

```bash
# Recalibrate robot or teleoperator motors
# Args: --robot.type, --teleop.type
# Source: src/lerobot/scripts/lerobot_calibrate.py
uv run lerobot-calibrate
```

```bash
# List available cameras and capture test images
# Args: --output-dir, --record-time-s
# Source: src/lerobot/scripts/lerobot_find_cameras.py
uv run lerobot-find-cameras opencv
```

```bash
# Find USB port for MotorsBus by disconnecting/reconnecting
# Source: src/lerobot/scripts/lerobot_find_port.py
uv run lerobot-find-port
```

```bash
# Record a dataset using teleoperation or policy
# Args: --robot.type, --dataset.repo_id
# Source: src/lerobot/scripts/lerobot_record.py
uv run lerobot-record
```

```bash
# Replay recorded dataset on robot
# Args: --robot.type, --dataset.repo_id
# Source: src/lerobot/scripts/lerobot_replay.py
uv run lerobot-replay
```

```bash
# Configure motor IDs and baudrate
# Args: --robot.type, --teleop.type
# Source: src/lerobot/scripts/lerobot_setup_motors.py
uv run lerobot-setup-motors
```

```bash
# Control robot from teleoperator
# Args: --robot.type, --teleop.type
# Source: src/lerobot/scripts/lerobot_teleoperate.py
uv run lerobot-teleoperate
```

```bash
# Evaluate a trained policy on an environment
# Args: --policy.path, --env.type
# Source: src/lerobot/scripts/lerobot_eval.py
uv run lerobot-eval
```

```bash
# Train a policy on a dataset
# Args: --policy.type, --dataset.repo_id
# Source: src/lerobot/scripts/lerobot_train.py
uv run lerobot-train
```

```bash
# Visualize dataset episodes using Rerun
# Args: --repo-id, --episode-index
# Source: src/lerobot/scripts/lerobot_dataset_viz.py
uv run lerobot-dataset-viz
```

```bash
# Display system and package information
# Source: src/lerobot/scripts/lerobot_info.py
uv run lerobot-info
```

```bash
# Find joint and end-effector bounds via teleoperation
# Args: --robot.type, --teleop.type
# Source: src/lerobot/scripts/lerobot_find_joint_limits.py
uv run lerobot-find-joint-limits
```

```bash
# Visualize image transform effects
# Args: --repo_id, --image_transforms.enable
# Source: src/lerobot/scripts/lerobot_imgtransform_viz.py
uv run lerobot-imgtransform-viz
```

```bash
# Edit datasets (delete episodes, split, merge, remove features)
# Args: --repo_id, --operation.type
# Source: src/lerobot/scripts/lerobot_edit_dataset.py
uv run lerobot-edit-dataset
```

## Setup & Installation

### Flash Attention Setup
Add to `pyproject.toml`:
```toml
[tool.uv.extra-build-dependencies]
flash-attn = [{ requirement = "torch", match-runtime = true }]

[tool.uv.extra-build-variables]
flash-attn = { FLASH_ATTENTION_SKIP_CUDA_BUILD = "TRUE" }
```

Add to dependencies:
```toml
"flash-attn==2.8.3"
```

### Install Commands
```bash
# Sync dependencies
uv sync

# Sync with specific extras (for server)
uv sync --extra pi --extra groot --extra smolvla

# Install groot dependencies
uv pip install -e .[groot]
```

### Git Configuration
```bash
git config --global user.email "rayenghali02@gmail.com"
git config --global user.name "Rayen023"
```

## Dataset Operations

### Convert Dataset Version
```bash
uv run python -m lerobot.datasets.v30.convert_dataset_v21_to_v30 \
    --repo-id /home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/cleaning_db/datasets/original \
    --push-to-hub false
```

### Delete Episodes from Dataset
```bash
uv run python -m lerobot.scripts.lerobot_edit_dataset \
    --repo_id youliangtan-so101-table-cleanup_before_split \
    --root /home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/youliangtan-so101-table-cleanup_before_split \
    --new_repo_id youliangtan-so101-table-cleanup \
    --operation.type delete_episodes \
    --operation.episode_indices "[20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79]" \
    --push_to_hub false
```

### Merge Datasets
```bash
uv run lerobot-edit-dataset \
    --repo_id /home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/Backups/merged-sort-blocks-all \
    --operation.type merge \
    --operation.repo_ids "['/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/Backups/sort-blocks', '/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/Backups/sort-blocks-2']" \
    --push_to_hub false
```

### Augment Dataset with Quantile Stats
```bash
# Basic usage
uv run python src/lerobot/datasets/v30/augment_dataset_quantile_stats.py \
    --repo-id="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/merged-so101-table-cleanup" \
    --push-to-hub=false

# With screen (for long-running tasks)
screen -L uv run python src/lerobot/datasets/v30/augment_dataset_quantile_stats.py \
    --repo-id="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets/original_resized_rotated_cleaned" \
    --push-to-hub=false
```

## Remote Sync Commands (rsync)

### Sync Datasets
```bash
# To fir server
rsync -avz --progress datasets/ rayen@fir.alliancecan.ca:/home/rayen/scratch/lerobot/datasets

# From local server
rsync -avz --progress -e "ssh -o StrictHostKeyChecking=no" recherche-a@198.164.36.108:/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/datasets ./
```

### Sync Training Outputs
```bash
# From fir server (new weights, with screen)
screen -L rsync -avz --progress rayen@fir.alliancecan.ca:/home/rayen/scratch/lerobot/outputs/train/ /mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/

# To local server
rsync -avz --progress -e "ssh -o StrictHostKeyChecking=no" outputs/train/ recherche-a@198.164.36.108:/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new/
```

## Server Monitoring

### Monitor Job with tmux
```bash
srun --jobid 11308368 --pty tmux new-session -d 'htop -u $USER' \; split-window -h 'watch nvidia-smi' \; attach
srun --jobid 11308369 --pty tmux new-session -d 'htop -u $USER' \; split-window -h 'watch nvidia-smi' \; attach
srun --jobid 11394296 --pty tmux new-session -d 'htop -u $USER' \; split-window -h 'watch nvidia-smi' \; attach


```

scancel -u $USER