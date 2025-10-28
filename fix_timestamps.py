#!/usr/bin/env python3
"""
Fix timestamps in LeRobot dataset to be uniform at 1/FPS intervals.

This script:
1. Loads the dataset
2. Recalculates timestamps to be uniform within each episode
3. Updates the data parquet files and episode metadata
"""

import pandas as pd
import json
from pathlib import Path

def fix_dataset_timestamps(dataset_path, fps=30):
    """Fix timestamps to be uniform at 1/fps intervals per episode"""
    
    dataset_path = Path(dataset_path)
    print(f"Fixing timestamps in: {dataset_path}")
    print(f"Target FPS: {fps}")
    print(f"Target frame interval: {1/fps:.6f}s")
    
    # Load info
    with open(dataset_path / "meta" / "info.json") as f:
        info = json.load(f)
    
    print(f"\nDataset info:")
    print(f"  Total frames: {info['total_frames']}")
    print(f"  Total episodes: {info['total_episodes']}")
    print(f"  FPS: {info['fps']}")
    
    # Load data
    data_file = dataset_path / "data" / "chunk-000" / "file-000.parquet"
    print(f"\nLoading data from: {data_file}")
    df = pd.read_parquet(data_file)
    
    print(f"Data shape: {df.shape}")
    print(f"\nOriginal timestamp stats:")
    print(f"  Min: {df['timestamp'].min()}")
    print(f"  Max: {df['timestamp'].max()}")
    print(f"  Mean diff: {df.groupby('episode_index')['timestamp'].diff().mean()}")
    
    # Fix timestamps per episode
    print("\nFixing timestamps...")
    frame_interval = 1.0 / fps
    
    for ep_idx in sorted(df['episode_index'].unique()):
        ep_mask = df['episode_index'] == ep_idx
        ep_data = df[ep_mask]
        
        # Calculate new uniform timestamps
        n_frames = len(ep_data)
        new_timestamps = [i * frame_interval for i in range(n_frames)]
        
        # Update timestamps
        df.loc[ep_mask, 'timestamp'] = new_timestamps
        
        if ep_idx % 50 == 0:
            print(f"  Episode {ep_idx}: {n_frames} frames, timestamps 0.0 to {new_timestamps[-1]:.3f}s")
    
    print(f"\nNew timestamp stats:")
    print(f"  Min: {df['timestamp'].min()}")
    print(f"  Max: {df['timestamp'].max()}")
    print(f"  Mean diff: {df.groupby('episode_index')['timestamp'].diff().mean():.6f}")
    
    # Save updated data
    backup_file = data_file.parent / "file-000.parquet.backup"
    print(f"\nBacking up original to: {backup_file}")
    df_original = pd.read_parquet(data_file)
    df_original.to_parquet(backup_file)
    
    print(f"Saving fixed data to: {data_file}")
    df.to_parquet(data_file)
    
    # Update episode metadata with new timestamp ranges
    print("\nUpdating episode metadata...")
    episodes_file = dataset_path / "meta" / "episodes" / "chunk-000" / "file-000.parquet"
    episodes = pd.read_parquet(episodes_file)
    
    for ep_idx in sorted(df['episode_index'].unique()):
        ep_mask = df['episode_index'] == ep_idx
        ep_data = df[ep_mask]
        
        # Update video timestamp ranges for each camera
        for camera in ['up_view', 'wrist_view']:
            from_col = f'videos/observation.images.{camera}/from_timestamp'
            to_col = f'videos/observation.images.{camera}/to_timestamp'
            
            if from_col in episodes.columns:
                episodes.loc[episodes['episode_index'] == ep_idx, from_col] = ep_data['timestamp'].min()
                episodes.loc[episodes['episode_index'] == ep_idx, to_col] = ep_data['timestamp'].max()
    
    # Save updated episodes
    backup_episodes = episodes_file.parent / "file-000.parquet.backup"
    print(f"Backing up episodes to: {backup_episodes}")
    pd.read_parquet(episodes_file).to_parquet(backup_episodes)
    
    print(f"Saving fixed episodes to: {episodes_file}")
    episodes.to_parquet(episodes_file)
    
    print("\n✓ Done! Timestamps fixed.")
    print("\nTo restore backups if needed:")
    print(f"  mv {backup_file} {data_file}")
    print(f"  mv {backup_episodes} {episodes_file}")


if __name__ == "__main__":
    dataset_path = "/home/recherche-a/OneDrive_recherche_a/Linux_onedrive/Projects_linux/Thesis/cleaning_db/combined_cleaned"
    fix_dataset_timestamps(dataset_path)
