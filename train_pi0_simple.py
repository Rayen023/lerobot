import subprocess
import os
from datetime import datetime
import glob
import re

root = "/home/recherche-a/.cache/huggingface/lerobot/"
repo_id = "Rayen023/combined_so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
dataset_name = repo_id.split('/')[-1]
steps = int(12000)
batch_size = 1  
n_action_steps = 50  # Number of action steps to take in each chunk
chunk_size = 50  # Number of chunks to process in each training step
POLICY_PATH = "lerobot/pi0" # pi0fast_base #lerobot/smolvla_base

output_dir = f"outputs/train/{dataset_name}__policy{POLICY_PATH}_bs{batch_size}_steps{steps}_action{n_action_steps}_chunk{chunk_size}_{timestamp}"
dataset_root = os.path.join(root, repo_id)


def run_training():

    cmd = [
        "python", "src/lerobot/scripts/train.py",
        f"--policy.path={POLICY_PATH}", 
        "--policy.push_to_hub=false", 
        f"--dataset.repo_id={repo_id}",
        f"--dataset.root={dataset_root}",
        f"--batch_size={batch_size}",
        f"--steps={steps}",
        f"--output_dir={output_dir}",
        f"--job_name={dataset_name}_pi0_bs{batch_size}_steps{steps}_{timestamp}",
        f"--policy.device=cuda",
        f"--policy.chunk_size={chunk_size}",
        f"--policy.n_action_steps={n_action_steps}",
        #"--dataset.image_transforms.enable=True",
        # "--wandb.enable=true"
    ]
    result = subprocess.run(cmd, check=True)


def manage_screenlog_files():
    os.makedirs("logs", exist_ok=True)
    
    # Get all screenlog files in logs directory
    screenlog_files = glob.glob("logs/screenlog.*")
    
    # Extract numbers from screenlog files
    numbers = []
    for file in screenlog_files:
        match = re.match(r'logs/screenlog\.(\d+)', file)
        if match:
            numbers.append(int(match.group(1)))
    
    # Check if screenlog.0 exists in current directory
    if os.path.exists("screenlog.0"):
        # Find the next available number
        if numbers:
            next_num = max(numbers) + 1
        else:
            next_num = 1
        
        # Format with zero padding to match existing pattern
        new_filename = f"logs/screenlog.{next_num:02d}"
        
        print(f"Moving screenlog.0 to {new_filename}")
        os.rename("screenlog.0", new_filename)


if __name__ == "__main__":
    manage_screenlog_files()
    run_training()

