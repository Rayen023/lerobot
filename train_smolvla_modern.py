#!/usr/bin/env python

import os
import logging
from datetime import datetime
from pathlib import Path

import torch
from torch.optim.lr_scheduler import LinearLR, SequentialLR

from lerobot.configs.types import FeatureType
from lerobot.datasets.lerobot_dataset import LeRobotDataset, LeRobotDatasetMetadata
from lerobot.datasets.utils import dataset_to_policy_features, cycle
from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.utils.logging_utils import AverageMeter, MetricsTracker


def manage_screenlog_files():
    import glob
    import re
    
    os.makedirs("logs", exist_ok=True)
    
    screenlog_files = glob.glob("logs/screenlog.*")
    
    numbers = []
    for file in screenlog_files:
        match = re.match(r'logs/screenlog\.(\d+)', file)
        if match:
            numbers.append(int(match.group(1)))
    
    if os.path.exists("screenlog.0"):
        if numbers:
            next_num = max(numbers) + 1
        else:
            next_num = 1
        
        new_filename = f"logs/screenlog.{next_num:02d}"
        
        os.rename("screenlog.0", new_filename)


def main():
    dataset_path = "/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/cleaning_db/combined_cleaned"
    
    batch_size = 64
    training_steps = 20000
    learning_rate = 1e-4
    
    log_freq = 100
    save_freq = 1000
    use_wandb = False
    wandb_project = "lerobot-smolvla"
    wandb_run_name = None
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dataset_name = Path(dataset_path).name
    output_dir = Path(f"outputs/train/{dataset_name}_smolvla_bs{batch_size}_steps{training_steps}_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    manage_screenlog_files()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(output_dir / "training.log"),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=" * 80)
    logging.info("SmolVLA Training Configuration")
    logging.info("=" * 80)
    logging.info(f"Dataset: {dataset_path}")
    logging.info(f"Output directory: {output_dir}")
    logging.info(f"Batch size: {batch_size}")
    logging.info(f"Training steps: {training_steps}")
    logging.info(f"Learning rate: {learning_rate}")
    logging.info(f"Device: {device}")
    logging.info(f"Log frequency: {log_freq}")
    logging.info(f"Save frequency: {save_freq}")
    logging.info(f"WandB enabled: {use_wandb}")
    logging.info("=" * 80)
    
    wandb_logger = None
    if use_wandb:
        try:
            import wandb
            run_name = wandb_run_name or f"smolvla_{dataset_name}_{timestamp}"
            wandb.init(
                project=wandb_project,
                name=run_name,
                config={
                    "batch_size": batch_size,
                    "learning_rate": learning_rate,
                    "training_steps": training_steps,
                    "dataset": dataset_path,
                    "policy": "smolvla_base",
                },
            )
            logging.info(f"WandB initialized: {wandb_project}/{run_name}")
        except ImportError:
            logging.warning("WandB not installed. Install with: pip install wandb")
            use_wandb = False
    
    dataset_metadata = LeRobotDatasetMetadata(dataset_path)
    
    features = dataset_to_policy_features(dataset_metadata.features)
    output_features = {key: ft for key, ft in features.items() if ft.type is FeatureType.ACTION}
    input_features = {key: ft for key, ft in features.items() if key not in output_features}
    
    logging.info(f"Input features: {list(input_features.keys())}")
    logging.info(f"Output features: {list(output_features.keys())}")
    
    policy_config = SmolVLAConfig(
        input_features=input_features,
        output_features=output_features,
        freeze_vision_encoder=True,
        train_expert_only=True,
        train_state_proj=True,
        optimizer_lr=learning_rate,
        optimizer_weight_decay=1e-10,
        optimizer_grad_clip_norm=10.0,
    )
    
    logging.info("Loading pre-trained SmolVLA model...")
    policy = SmolVLAPolicy.from_pretrained("lerobot/smolvla_base")
    
    for key, value in policy_config.__dict__.items():
        if not key.startswith('_'):
            setattr(policy.config, key, value)
    
    policy.to(device)
    
    preprocessor, postprocessor = make_pre_post_processors(
        policy.config, 
        dataset_stats=dataset_metadata.stats
    )
    
    logging.info(f"Policy configuration:")
    logging.info(f"  - chunk_size: {policy.config.chunk_size}")
    logging.info(f"  - n_action_steps: {policy.config.n_action_steps}")
    
    delta_timestamps = {}
    
    for key in input_features.keys():
        if "observation" in key:
            delta_timestamps[key] = [
                i / dataset_metadata.fps 
                for i in policy.config.observation_delta_indices
            ]
    
    for key in output_features.keys():
        delta_timestamps[key] = [
            i / dataset_metadata.fps 
            for i in policy.config.action_delta_indices
        ]
    
    logging.info("Loading dataset...")
    dataset = LeRobotDataset(
        dataset_path,
        delta_timestamps=delta_timestamps
    )
    
    logging.info(f"Dataset loaded: {dataset.num_frames} frames, {dataset.num_episodes} episodes")
    
    if hasattr(policy, 'get_optim_params'):
        params = policy.get_optim_params()
    else:
        params = policy.parameters()
    
    optimizer = torch.optim.AdamW(
        params,
        lr=policy.config.optimizer_lr,
        betas=policy.config.optimizer_betas,
        eps=policy.config.optimizer_eps,
        weight_decay=policy.config.optimizer_weight_decay,
    )
    
    warmup_scheduler = LinearLR(
        optimizer,
        start_factor=0.01,
        end_factor=1.0,
        total_iters=policy.config.scheduler_warmup_steps
    )
    
    decay_scheduler = LinearLR(
        optimizer,
        start_factor=1.0,
        end_factor=policy.config.scheduler_decay_lr / policy.config.optimizer_lr,
        total_iters=policy.config.scheduler_decay_steps
    )
    
    lr_scheduler = SequentialLR(
        optimizer,
        schedulers=[warmup_scheduler, decay_scheduler],
        milestones=[policy.config.scheduler_warmup_steps]
    )
    
    dataloader = torch.utils.data.DataLoader(
        dataset,
        num_workers=4,
        batch_size=batch_size,
        shuffle=True,
        pin_memory=device.type == "cuda",
        drop_last=True,
        prefetch_factor=2,
    )
    
    dl_iter = cycle(dataloader)
    
    train_metrics = {
        "loss": AverageMeter("loss", ":.3f"),
        "grad_norm": AverageMeter("grad_norm", ":.3f"),
        "lr": AverageMeter("lr", ":0.1e"),
    }
    
    train_tracker = MetricsTracker(
        batch_size=batch_size,
        num_frames=dataset.num_frames,
        num_episodes=dataset.num_episodes,
        metrics=train_metrics,
        initial_step=0,
    )
    
    logging.info("=" * 80)
    logging.info("Starting training...")
    logging.info("=" * 80)
    
    policy.train()
    
    for step in range(training_steps):
        batch = next(dl_iter)
        batch = preprocessor(batch)
        
        loss, output_dict = policy.forward(batch)
        
        optimizer.zero_grad()
        loss.backward()
        
        grad_norm = torch.nn.utils.clip_grad_norm_(
            policy.parameters(),
            policy.config.optimizer_grad_clip_norm
        )
        
        optimizer.step()
        lr_scheduler.step()
        
        train_tracker.loss = loss.item()
        train_tracker.grad_norm = grad_norm.item()
        train_tracker.lr = optimizer.param_groups[0]["lr"]
        train_tracker.step()
        
        if (step + 1) % log_freq == 0:
            logging.info(train_tracker)
            
            if use_wandb:
                wandb_log_dict = train_tracker.to_dict()
                if output_dict:
                    wandb_log_dict.update(output_dict)
                wandb.log(wandb_log_dict, step=step + 1)
            
            train_tracker.reset_averages()
        
        if (step + 1) % save_freq == 0 or (step + 1) == training_steps:
            checkpoint_dir = output_dir / f"checkpoint_{step + 1}"
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            logging.info(f"Saving checkpoint to {checkpoint_dir}")
            policy.save_pretrained(checkpoint_dir)
            preprocessor.save_pretrained(checkpoint_dir)
            postprocessor.save_pretrained(checkpoint_dir)
            
            torch.save({
                'step': step + 1,
                'optimizer_state_dict': optimizer.state_dict(),
                'lr_scheduler_state_dict': lr_scheduler.state_dict(),
            }, checkpoint_dir / "training_state.pt")
    
    final_dir = output_dir / "final_model"
    final_dir.mkdir(parents=True, exist_ok=True)
    
    logging.info("=" * 80)
    logging.info(f"Training complete! Saving final model to {final_dir}")
    logging.info("=" * 80)
    policy.save_pretrained(final_dir)
    preprocessor.save_pretrained(final_dir)
    postprocessor.save_pretrained(final_dir)
    
    if use_wandb:
        wandb.finish()
    
    logging.info("Training finished successfully!")


if __name__ == "__main__":
    main()
