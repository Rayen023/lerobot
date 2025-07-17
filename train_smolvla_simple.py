"""
python lerobot/scripts/train.py --policy.path=lerobot/smolvla_base --dataset.repo_id=lerobot/svla_so101_pickplace --batch_size=64 --steps=20000 --output_dir=outputs/train/my_smolvla --job_name=my_smolvla_training --policy.device=cuda --wandb.enable=true
python lerobot/scripts/train.py --policy.path=lerobot/smolvla_base --dataset.repo_id=lerobot/stanford_kuka_multimodal_dataset --batch_size=64 --steps=20000 --output_dir=outputs/train/kuka_smolvla --job_name=kukasmolvla_training --policy.device=cuda --wandb.enable=true
"""

# !huggingface-cli login
import subprocess
import os
from datetime import datetime
import glob
import re

# Configuration
root = "/home/recherche-a/.cache/huggingface/lerobot/"
#repo_id = "Rayen023/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90" # 50 episodes on small block task, 5 fixed locations
#repo_id = "Rayen023/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250715_123150" # 100 episodes on small block task, different locations
#repo_id = "Rayen023/so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30_20250716_113612" # 100 episodes on large block task, different locations
repo_id = "Rayen023/combined_so101_follower_put_the_red_lego_block_in_the_black_cup_eps100_fps30"
# Generate timestamp for unique naming
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
dataset_name = repo_id.split('/')[-1]
steps = int(8000)
batch_size = 82  # 96 bs uses 24GB of GPU memory, 64 bs uses 16GB of GPU memory

# Create informative output directory with timestamp, batch size, and steps
output_dir = f"outputs/train/{dataset_name}_smolvla_bs{batch_size}_steps{steps}_{timestamp}"
#POLICY_PATH_64BS_12k_steps = "outputs/train/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90_smolvla_bs64_steps12000_20250714_185931/checkpoints/last/pretrained_model" 
#POLICY_PATH = POLICY_PATH_64BS_12k_steps  # Use the path to the pre-trained model

POLICY_PATH = "lerobot/smolvla_base"

def manage_screenlog_files():
    """
    Check for existing screenlog files and rename screenlog.0 to the next available number in logs folder
    """
    # Ensure logs directory exists
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

def run_training():
    """Run the SmolVLA training with local dataset"""
    
    # Manage screenlog files before stlarting training
    manage_screenlog_files()
    
    # Construct the dataset root path
    dataset_root = os.path.join(root, repo_id)
    
    # Build the command
    cmd = [
        "python", "src/lerobot/scripts/train.py",
        f"--policy.path={POLICY_PATH}", #lerobot/smolvla_base",
        "--policy.push_to_hub=false",  # Disable pushing to hub
        f"--dataset.repo_id={repo_id}",
        f"--dataset.root={dataset_root}",
        f"--batch_size={batch_size}",
        f"--steps={steps}",
        f"--output_dir={output_dir}",
        f"--job_name={dataset_name}_smolvla_bs{batch_size}_steps{steps}_{timestamp}",
        "--policy.device=cuda",
        "--policy.chunk_size=15",
        "--policy.n_action_steps=15",
        #"--dataset.image_transforms.enable=True",
        # "--wandb.enable=true"
    ]
    
    print("Starting SmolVLA training with the following configuration:")
    print(f"Dataset: {repo_id}")
    print(f"Dataset root: {dataset_root}")
    print(f"Output directory: {output_dir}")
    print(f"Steps: {steps}")
    print(f"Batch size: {batch_size}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 80)
    
    # Check if dataset exists
    if not os.path.exists(dataset_root):
        print(f"Warning: Dataset directory does not exist: {dataset_root}")
        print("Make sure your dataset is downloaded or specify the correct path.")
        return
    
    try:
        # Run the training command
        result = subprocess.run(cmd, check=True, cwd="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/lerobot")
        print("Training completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Training failed with error code {e.returncode}")
        print("Check the output above for error details.")
    except FileNotFoundError:
        print("Error: Could not find the training script. Make sure you're in the correct directory.")

if __name__ == "__main__":
    run_training()

