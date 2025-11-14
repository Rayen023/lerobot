import pandas as pd
import shutil
from pathlib import Path

# Read the parquet file
parquet_path = "/home/rayen/scratch/lerobot/datasets/merged-sort-blocks-12/meta/episodes/chunk-000/file-000.parquet"

# Create backup first
backup_path = parquet_path + ".backup"
shutil.copy2(parquet_path, backup_path)
print(f"✓ Backup created at: {backup_path}\n")

# Read the parquet file
df = pd.read_parquet(parquet_path)

# Filter for episodes 30 and 31
episodes_30_31 = df[df['episode_index'].isin([30, 31])]

# Define the columns we want to extract
columns_of_interest = [
    'episode_index',
    'videos/observation.images.front/from_timestamp',
    'videos/observation.images.front/to_timestamp',
    'videos/observation.images.wrist/from_timestamp',
    'videos/observation.images.wrist/to_timestamp'
]

# Select only the columns of interest
result = episodes_30_31[columns_of_interest]

print("Episodes 30 and 31 data:")
print("=" * 100)
print(result.to_string())
print("\n")
print(f"Total rows: {len(result)}")
print("\n")

# Dry run: Calculate corrected values for episode 31 front camera
print("=" * 100)
print("DRY RUN - Proposed Corrections:")
print("=" * 100)

# Get episode 30 data
ep30 = episodes_30_31[episodes_30_31['episode_index'] == 30].iloc[0]
ep31 = episodes_30_31[episodes_30_31['episode_index'] == 31].iloc[0]

# Current values
ep30_front_from = ep30['videos/observation.images.front/from_timestamp']
ep30_front_to = ep30['videos/observation.images.front/to_timestamp']
ep31_front_from = ep31['videos/observation.images.front/from_timestamp']
ep31_front_to = ep31['videos/observation.images.front/to_timestamp']
ep31_wrist_from = ep31['videos/observation.images.wrist/from_timestamp']
ep31_wrist_to = ep31['videos/observation.images.wrist/to_timestamp']

print(f"\nEpisode 30 Front Camera:")
print(f"  from_timestamp: {ep30_front_from}")
print(f"  to_timestamp: {ep30_front_to}")
print(f"  Duration: {ep30_front_to - ep30_front_from:.6f} seconds")

print(f"\nEpisode 31 Wrist Camera (correct reference):")
print(f"  from_timestamp: {ep31_wrist_from}")
print(f"  to_timestamp: {ep31_wrist_to}")
print(f"  Duration: {ep31_wrist_to - ep31_wrist_from:.6f} seconds")

print(f"\nEpisode 31 Front Camera (CURRENT - WRONG):")
print(f"  from_timestamp: {ep31_front_from}")
print(f"  to_timestamp: {ep31_front_to}")
print(f"  Duration: {ep31_front_to - ep31_front_from:.6f} seconds")

# Calculate corrected values
# Should start from end of episode 30 front camera
corrected_ep31_front_from = ep30_front_to
# Duration should match episode 31 wrist camera duration
ep31_duration = ep31_wrist_to - ep31_wrist_from
corrected_ep31_front_to = corrected_ep31_front_from + ep31_duration

print(f"\nEpisode 31 Front Camera (CORRECTED):")
print(f"  from_timestamp: {corrected_ep31_front_from}")
print(f"  to_timestamp: {corrected_ep31_front_to}")
print(f"  Duration: {corrected_ep31_front_to - corrected_ep31_front_from:.6f} seconds")

print(f"\n" + "=" * 100)
print("SUMMARY OF CHANGES NEEDED:")
print("=" * 100)
print(f"Episode 31 'videos/observation.images.front/from_timestamp':")
print(f"  Current: {ep31_front_from}")
print(f"  Should be: {corrected_ep31_front_from}")
print(f"  Change: {corrected_ep31_front_from - ep31_front_from:+.6f}")

print(f"\nEpisode 31 'videos/observation.images.front/to_timestamp':")
print(f"  Current: {ep31_front_to}")
print(f"  Should be: {corrected_ep31_front_to}")
print(f"  Change: {corrected_ep31_front_to - ep31_front_to:+.6f}")

# Apply the correction
print("\n" + "=" * 100)
print("APPLYING CORRECTIONS...")
print("=" * 100)

# Update the dataframe
df.loc[df['episode_index'] == 31, 'videos/observation.images.front/from_timestamp'] = corrected_ep31_front_from
df.loc[df['episode_index'] == 31, 'videos/observation.images.front/to_timestamp'] = corrected_ep31_front_to

# Save the corrected parquet file
df.to_parquet(parquet_path)
print(f"✓ Corrected parquet file saved to: {parquet_path}")

# Verify the changes
print("\n" + "=" * 100)
print("VERIFICATION - Reading corrected file:")
print("=" * 100)

df_verify = pd.read_parquet(parquet_path)
episodes_verify = df_verify[df_verify['episode_index'].isin([30, 31])][columns_of_interest]

print(episodes_verify.to_string())
print("\n✓ Correction complete!")
