#!/bin/bash

# Checkpoints to keep (in step format with leading zeros)
KEEP_CHECKPOINTS=("002000" "004000" "006000" "008000" "010000" "016000" "022000" "028000" "034000" "040000" "046000" "052000" "058000")

# Base directory
TRAIN_DIR="/home/rayen/scratch/lerobot/outputs/train"
CACHE_DIR="/home/rayen/scratch/lerobot/.cache/unwanted_checkpoints"

# Function to check if a checkpoint should be kept
should_keep() {
    local checkpoint=$1
    for keep in "${KEEP_CHECKPOINTS[@]}"; do
        if [[ "$checkpoint" == "$keep" ]]; then
            return 0
        fi
    done
    return 1
}

# Process each training folder
for folder in "$TRAIN_DIR"/*/ ; do
    folder_name=$(basename "$folder")
    echo "Processing: $folder_name"
    
    checkpoint_dir="$folder/checkpoints"
    if [[ ! -d "$checkpoint_dir" ]]; then
        echo "  No checkpoints directory found, skipping..."
        continue
    fi
    
    # Create cache subdirectory for this training run
    cache_subdir="$CACHE_DIR/$folder_name"
    mkdir -p "$cache_subdir"
    
    # Process each checkpoint
    for checkpoint_path in "$checkpoint_dir"/*/ ; do
        checkpoint=$(basename "$checkpoint_path")
        
        # Skip if it's "last" or not a numeric checkpoint
        if [[ "$checkpoint" == "last" ]]; then
            echo "  Keeping: $checkpoint (special)"
            continue
        fi
        
        if should_keep "$checkpoint"; then
            echo "  Keeping: $checkpoint"
        else
            # Check if checkpoint exists before moving
            if [[ -d "$checkpoint_path" ]]; then
                echo "  Moving: $checkpoint -> .cache/$folder_name/"
                mv "$checkpoint_path" "$cache_subdir/"
            else
                echo "  Not found: $checkpoint (already moved)"
            fi
        fi
    done
    
    echo ""
done

echo "Done! Moved checkpoints are in: $CACHE_DIR"
