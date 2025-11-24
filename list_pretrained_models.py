#!/usr/bin/env python3

import os
from pathlib import Path

# Base path to search
BASE_PATH = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/VLA_weights_evals/new"
OUTPUT_FILE = "pretrained_models_list.txt"

def find_pretrained_models(base_path):
    """Find all directories ending with 'pretrained_model' under the base path."""
    pretrained_paths = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name == "pretrained_model":
                full_path = os.path.join(root, dir_name)
                pretrained_paths.append(full_path)
    
    # Sort alphabetically
    pretrained_paths.sort()
    
    return pretrained_paths

def write_to_file(paths, output_file):
    """Write paths to output file in the specified format."""
    with open(output_file, 'w') as f:
        for path in paths:
            f.write(f'POLICY_PATH = "{path}"\n')
    
    print(f"Found {len(paths)} pretrained_model directories")
    print(f"Results written to: {output_file}")

if __name__ == "__main__":
    print(f"Searching for pretrained_model directories in: {BASE_PATH}")
    
    if not os.path.exists(BASE_PATH):
        print(f"Error: Base path does not exist: {BASE_PATH}")
        exit(1)
    
    pretrained_paths = find_pretrained_models(BASE_PATH)
    
    if pretrained_paths:
        write_to_file(pretrained_paths, OUTPUT_FILE)
        print("\nFirst 5 entries:")
        for path in pretrained_paths[:5]:
            print(f'  POLICY_PATH = "{path}"')
    else:
        print("No pretrained_model directories found.")
