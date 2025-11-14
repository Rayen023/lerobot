#!/bin/bash
#SBATCH --account=def-selouani
#SBATCH --gres=gpu:h100:1       # Request GPU "generic resources"
#SBATCH --mem=80G       # Memory proportional to GPUs: 32000 Cedar, 64000 Graham.
#SBATCH --time=0-23:00
#SBATCH --output=output/%N-%j.out

module load cuda

# Set Hugging Face cache to scratch to avoid home directory quota issues
export HF_HOME="/home/rayen/scratch/lerobot/.cache/huggingface"
export TRANSFORMERS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/transformers"
export HF_DATASETS_CACHE="/home/rayen/scratch/lerobot/.cache/huggingface/datasets"

# Set WandB cache directory to scratch space instead of home directory
export WANDB_CACHE_DIR="/home/rayen/scratch/wandb"
export WANDB_DIR="/home/rayen/scratch/wandb"
export WANDB_DATA_DIR="/home/rayen/scratch/wandb"

# GR00T N1.5 Training Script
# Configuration for NVIDIA's GR00T N1.5 foundation model
# Model: nvidia/GR00T-N1.5-3B

# =============================================================================
# Hyperparameters - Edit these values as needed
# =============================================================================

# Model Configuration
MODEL_NAME="groot_n1.5"
POLICY_PATH="nvidia/GR00T-N1.5-3B"  # Base pretrained model
POLICY_TYPE="groot"
EMBODIMENT_TAG="so101"  # Change to match your robot embodiment

# Dataset Configuration
# Use absolute path for local dataset
# DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/original_resized_rotated_cleaned"
# DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/sort-blocks"
DATASET_REPO_ID="/home/rayen/scratch/lerobot/datasets/merged-so101-table-cleanup"

# Training Hyperparameters
BATCH_SIZE=120 #160 uses 80GB VRAM
STEPS=50000
# LEARNING_RATE=0.0003
# WARMUP_RATIO=0.05

# DEVICE="cuda"
# USE_BF16=true

# TUNE_LLM=false
# TUNE_VISUAL=false
# TUNE_PROJECTOR=true
# TUNE_DIFFUSION_MODEL=true

# LORA_RANK=0
# LORA_ALPHA=16
# LORA_DROPOUT=0.1

# MAX_STATE_DIM=64
# MAX_ACTION_DIM=32
# CHUNK_SIZE=50
# N_ACTION_STEPS=50
# N_OBS_STEPS=1

# IMAGE_SIZE=224

# PUSH_TO_HUB=false
# WANDB_ENABLE=true
# SAVE_FREQ=5000

# =============================================================================
# Auto-generated Configuration
# =============================================================================

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_REPO_ID")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

# =============================================================================
# Training Command
# =============================================================================

uv run lerobot-train \
  --policy.type="${POLICY_TYPE}" \
  --policy.base_model_path="${POLICY_PATH}" \
  --dataset.repo_id="${DATASET_REPO_ID}" \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --policy.repo_id="${OUTPUT_DIR}" \
  --policy.device="cuda" \
  --wandb.enable=true \
  --save_freq=3000 \
  --policy.push_to_hub=false \
#   --policy.optimizer_lr=${LEARNING_RATE} \
#   --policy.warmup_ratio=${WARMUP_RATIO} \
#   --policy.use_bf16=${USE_BF16} \
#   --policy.tune_llm=${TUNE_LLM} \
#   --policy.tune_visual=${TUNE_VISUAL} \
#   --policy.tune_projector=${TUNE_PROJECTOR} \
#   --policy.tune_diffusion_model=${TUNE_DIFFUSION_MODEL} \
#   --policy.lora_rank=${LORA_RANK} \
#   --policy.lora_alpha=${LORA_ALPHA} \
#   --policy.lora_dropout=${LORA_DROPOUT} \
#   --policy.max_state_dim=${MAX_STATE_DIM} \
#   --policy.max_action_dim=${MAX_ACTION_DIM} \
#   --policy.chunk_size=${CHUNK_SIZE} \
#   --policy.n_action_steps=${N_ACTION_STEPS} \
#   --policy.n_obs_steps=${N_OBS_STEPS} \
#   --policy.image_size="[${IMAGE_SIZE}, ${IMAGE_SIZE}]" \
#   --save_freq=${SAVE_FREQ}
#   --policy.embodiment_tag="${EMBODIMENT_TAG}" \
#   --rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'

# All Available Policy Types:

# act - Action Chunking Transformers
# diffusion - Diffusion Policy
# groot - GR00T N1.5 ✅
# pi0 - Physical Intelligence Pi0
# pi05 - Physical Intelligence Pi0.5
# smolvla - SmolVLA Vision-Language-Action
# tdmpc - Temporal Difference MPC
# vqbet - VQ-BeT
# sac - Soft Actor-Critic (RL)


# All Available Embodiment Tags:

# Tag	ID	Description
# "new_embodiment"	31	Default for new/custom robots
# "gr1"	24	NVIDIA GR1 humanoid robot
# "so100"	2	SO-100 robot arm
# "unitree_g1"	3	Unitree G1 humanoid
# "oxe_droid"	17	OXE DROID robot
# "agibot_genie1"	26	Agibot Genie1 robot
