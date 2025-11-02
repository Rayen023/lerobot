#!/bin/bash

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
DATASET_REPO_ID="/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/lerobot/datasets/youliangtan-so101-table-cleanup"

# Training Hyperparameters
BATCH_SIZE=32          # Default: 32, adjust based on GPU memory
LEARNING_RATE=0.0001   # Default: 1e-4
STEPS=10000            # Default: 10000, increase for better convergence
WARMUP_RATIO=0.05      # 5% warmup steps

# Device Configuration
DEVICE="cuda"
USE_BF16=true          # Use bfloat16 for memory efficiency

# Fine-tuning Control (what parts of the model to train)
TUNE_LLM=false              # Fine-tune the language model backbone
TUNE_VISUAL=false           # Fine-tune the vision tower
TUNE_PROJECTOR=true         # Fine-tune the projector (recommended)
TUNE_DIFFUSION_MODEL=true   # Fine-tune the diffusion model (recommended)

# LoRA Configuration (optional, set lora_rank > 0 to enable)
LORA_RANK=0            # 0 = disabled, 8-64 = enabled with rank
LORA_ALPHA=16
LORA_DROPOUT=0.1

# Model Dimensions
MAX_STATE_DIM=64       # Maximum state dimension (zero-padded if smaller)
MAX_ACTION_DIM=32      # Maximum action dimension (zero-padded if smaller)
CHUNK_SIZE=50          # Action chunk size
N_ACTION_STEPS=50      # Number of action steps to predict
N_OBS_STEPS=1          # Number of observation steps

# Image Configuration
IMAGE_SIZE=224         # Image size for GR00T (224x224)

# Embodiment Tag

# Output and Logging
PUSH_TO_HUB=false
WANDB_ENABLE=true
SAVE_FREQ=5000         # Save checkpoint every N steps

# =============================================================================
# Auto-generated Configuration
# =============================================================================

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATASET_NAME=$(basename "$DATASET_REPO_ID")
JOB_NAME="${MODEL_NAME}_${DATASET_NAME}_bs${BATCH_SIZE}_lr${LEARNING_RATE}_${TIMESTAMP}"
OUTPUT_DIR="outputs/train/${JOB_NAME}"

# =============================================================================
# Training Command
# =============================================================================

echo "=================================================="
echo "GR00T N1.5 Training Configuration"
echo "=================================================="
echo "Model: ${POLICY_PATH}"
echo "Dataset: ${DATASET_REPO_ID}"
echo "Batch Size: ${BATCH_SIZE}"
echo "Learning Rate: ${LEARNING_RATE}"
echo "Steps: ${STEPS}"
echo "Output: ${OUTPUT_DIR}"
echo "Embodiment: ${EMBODIMENT_TAG}"
echo "=================================================="
echo ""

uv run lerobot-train \
  --policy.type="${POLICY_TYPE}" \
  --policy.base_model_path="${POLICY_PATH}" \
  --dataset.repo_id="${DATASET_REPO_ID}" \
  --batch_size=${BATCH_SIZE} \
  --steps=${STEPS} \
  --output_dir="${OUTPUT_DIR}" \
  --job_name="${JOB_NAME}" \
  --policy.device=${DEVICE} \
  --wandb.enable=${WANDB_ENABLE} \
  --policy.push_to_hub=${PUSH_TO_HUB} \
  --policy.optimizer_lr=${LEARNING_RATE} \
  --policy.warmup_ratio=${WARMUP_RATIO} \
  --policy.use_bf16=${USE_BF16} \
  --policy.tune_llm=${TUNE_LLM} \
  --policy.tune_visual=${TUNE_VISUAL} \
  --policy.tune_projector=${TUNE_PROJECTOR} \
  --policy.tune_diffusion_model=${TUNE_DIFFUSION_MODEL} \
  --policy.lora_rank=${LORA_RANK} \
  --policy.lora_alpha=${LORA_ALPHA} \
  --policy.lora_dropout=${LORA_DROPOUT} \
  --policy.max_state_dim=${MAX_STATE_DIM} \
  --policy.max_action_dim=${MAX_ACTION_DIM} \
  --policy.chunk_size=${CHUNK_SIZE} \
  --policy.n_action_steps=${N_ACTION_STEPS} \
  --policy.n_obs_steps=${N_OBS_STEPS} \
  --policy.image_size=${IMAGE_SIZE} ${IMAGE_SIZE} \
#   --policy.embodiment_tag="${EMBODIMENT_TAG}" \
  --save_freq=${SAVE_FREQ} \
#   --rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'

echo ""
echo "=================================================="
echo "Training completed!"
echo "Output saved to: ${OUTPUT_DIR}"
echo "=================================================="

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
