# Training Scripts Documentation

```bash
sbatch slurm_scripts/train.sh groot
sbatch slurm_scripts/train.sh pi05
sbatch slurm_scripts/train.sh smolvla
```

## Available Datasets

The following datasets are available for training:
- `/home/rayen/scratch/lerobot/datasets/merged-pick-place-red-block-12`
- `/home/rayen/scratch/lerobot/datasets/merged-pick-place-red-block-all`
- `/home/rayen/scratch/lerobot/datasets/merged-sort-blocks-123`
- `/home/rayen/scratch/lerobot/datasets/merged-so101-table-cleanup`
- `/home/rayen/scratch/lerobot/datasets/Backups/sort-blocks-2`

## Performance Notes

### Batch Size and VRAM Usage
- **SmolVLA**: `BATCH_SIZE=64` uses 16GB VRAM
- **Pi05**: `BATCH_SIZE=32` uses 40GB VRAM
- **GR00T**: `BATCH_SIZE=64` uses standard VRAM, `BATCH_SIZE=160` uses 80GB VRAM

## All Available Policy Types

- `act` - Action Chunking Transformers
- `diffusion` - Diffusion Policy
- `groot` - GR00T N1.5 
- `pi0` - Physical Intelligence Pi0
- `pi05` - Physical Intelligence Pi0.5
- `smolvla` - SmolVLA Vision-Language-Action
- `tdmpc` - Temporal Difference MPC
- `vqbet` - VQ-BeT
- `sac` - Soft Actor-Critic (RL)

## All Available Embodiment Tags

| Tag | ID | Description |
|-----|----|----|
| `new_embodiment` | 31 | Default for new/custom robots |
| `gr1` | 24 | NVIDIA GR1 humanoid robot |
| `so100` | 2 | SO-100 robot arm |
| `unitree_g1` | 3 | Unitree G1 humanoid |
| `oxe_droid` | 17 | OXE DROID robot |
| `agibot_genie1` | 26 | Agibot Genie1 robot |

## Policy-Specific Notes

### GR00T (train_groot.sh)
- Uses embodiment tags for robot-specific training
- Default embodiment tag: `so101`

### Pi05 (train_pi05.sh)
- Supports model compilation and gradient checkpointing
- Uses bfloat16 dtype for training
- Has configurable scheduler decay steps

### SmolVLA (train_smolvla.sh)
- **IMPORTANT**: Requires `rename_map` argument to map camera names:
  ```
  --rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'
  ```

## Commented Out GR00T Parameters

The following parameters are available but commented out in the GR00T script:

```bash
LEARNING_RATE=0.0003
WARMUP_RATIO=0.05
USE_BF16=true
TUNE_LLM=false
TUNE_VISUAL=false
TUNE_PROJECTOR=true
TUNE_DIFFUSION_MODEL=true
LORA_RANK=0
LORA_ALPHA=16
LORA_DROPOUT=0.1
MAX_STATE_DIM=64
MAX_ACTION_DIM=32
CHUNK_SIZE=50
N_ACTION_STEPS=50
N_OBS_STEPS=1
IMAGE_SIZE=224
```

Corresponding command arguments:
```bash
--policy.optimizer_lr=${LEARNING_RATE}
--policy.warmup_ratio=${WARMUP_RATIO}
--policy.use_bf16=${USE_BF16}
--policy.tune_llm=${TUNE_LLM}
--policy.tune_visual=${TUNE_VISUAL}
--policy.tune_projector=${TUNE_PROJECTOR}
--policy.tune_diffusion_model=${TUNE_DIFFUSION_MODEL}
--policy.lora_rank=${LORA_RANK}
--policy.lora_alpha=${LORA_ALPHA}
--policy.lora_dropout=${LORA_DROPOUT}
--policy.max_state_dim=${MAX_STATE_DIM}
--policy.max_action_dim=${MAX_ACTION_DIM}
--policy.chunk_size=${CHUNK_SIZE}
--policy.n_action_steps=${N_ACTION_STEPS}
--policy.n_obs_steps=${N_OBS_STEPS}
--policy.image_size="[${IMAGE_SIZE}, ${IMAGE_SIZE}]"
--policy.embodiment_tag="${EMBODIMENT_TAG}"
--rename_map='{"observation.images.front": "observation.images.camera1", "observation.images.wrist": "observation.images.camera2"}'
```

## WANDB Configuration

All scripts disable artifact uploads to the wandb server using:
- `export WANDB_MODE="online"` - Keep online for graphs/logs
- `--wandb.disable_artifact=true` - Disable artifacts via config
