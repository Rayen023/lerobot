"""
python lerobot/scripts/train.py --policy.path=lerobot/smolvla_base --dataset.repo_id=lerobot/svla_so101_pickplace --batch_size=64 --steps=20000 --output_dir=outputs/train/my_smolvla --job_name=my_smolvla_training --policy.device=cuda --wandb.enable=true
python lerobot/scripts/train.py --policy.path=lerobot/smolvla_base --dataset.repo_id=lerobot/stanford_kuka_multimodal_dataset --batch_size=64 --steps=20000 --output_dir=outputs/train/kuka_smolvla --job_name=kukasmolvla_training --policy.device=cuda --wandb.enable=true
"""

# !huggingface-cli login
import subprocess
import os
import uuid

# Configuration
root = "/home/recherche-a/.cache/huggingface/lerobot/"
repo_id = "Rayen023/so101_follower_put_the_red_lego_block_in_the_black_cup_bf1e90" 
output_dir = f"outputs/train/{repo_id.split('/')[-1]}_smolvla_{str(uuid.uuid4())[:8]}"  # Unique output directory
steps = int(20000)
batch_size = 32  # 96 bs uses 24GB of GPU memory, 64 bs uses 16GB of GPU memory

def run_training():
    """Run the SmolVLA training with local dataset"""
    
    # Construct the dataset root path
    dataset_root = os.path.join(root, repo_id)
    
    # Build the command
    cmd = [
        "python", "src/lerobot/scripts/train.py",
        "--policy.path=lerobot/smolvla_base",
        "--policy.push_to_hub=false",  # Disable pushing to hub
        f"--dataset.repo_id={repo_id}",
        f"--dataset.root={dataset_root}",
        f"--batch_size={batch_size}",
        f"--steps={steps}",
        f"--output_dir={output_dir}",
        f"--job_name={repo_id.split('/')[-1]}_training",
        "--policy.device=cuda",
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

