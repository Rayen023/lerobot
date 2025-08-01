#!/usr/bin/env python3
"""
Simple script to compare calibration values between reference and current calibration files.
"""

import json


def load_json_file(file_path):
    """Load JSON file and return its content."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return {}


def compare_calibrations(ref_file, current_file):
    """Compare two calibration files and print results."""
    
    # Load both calibration files
    reference_calibration = load_json_file(ref_file)
    current_calibration = load_json_file(current_file)
    
    if not reference_calibration or not current_calibration:
        return
    
    # Calculate distances for each joint
    joint_distances = []
    total_distance = 0.0
    
    print("CALIBRATION COMPARISON")
    print("=" * 50)
    
    for joint_name in reference_calibration.keys():
        if joint_name in current_calibration:
            ref_joint = reference_calibration[joint_name]
            current_joint = current_calibration[joint_name]
            
            # Calculate distance for this joint
            joint_distance = 0.0
            for param in ['homing_offset', 'range_min', 'range_max']:
                if param in ref_joint and param in current_joint:
                    distance = abs(ref_joint[param] - current_joint[param])
                    joint_distance += distance
            
            joint_distances.append((joint_name, joint_distance))
            total_distance += joint_distance
    
    # Sort joints by distance (least to most)
    joint_distances.sort(key=lambda x: x[1])
    
    # Print results
    for i, (joint_name, joint_distance) in enumerate(joint_distances, 1):
        ref_joint = reference_calibration[joint_name]
        current_joint = current_calibration[joint_name]
        
        print(f"• {joint_name}: {joint_distance:.1f} total distance")
        for param in ['homing_offset', 'range_min', 'range_max']:
            if param in ref_joint and param in current_joint:
                diff = abs(ref_joint[param] - current_joint[param])
                print(f"  - {param}: {diff:.1f} (ref: {ref_joint[param]}, current: {current_joint[param]})")
        print()
    
    print(f"TOTAL ABSOLUTE DISTANCE: {total_distance:.1f}")


def main():
    # File paths
    ref_file = "/mnt/67202c8a-ad15-4297-8aba-aeafd1dd3341/Data2/Backups/Backup_23_jul_2025/.cache/huggingface/lerobot/calibration/robots/so101_follower/my_follower_arm_1.json"
    current_file = "/home/recherche-a/.cache/huggingface/lerobot/calibration/robots/so101_follower/my_calibrated_follower_arm8.json"
    
    compare_calibrations(ref_file, current_file)


if __name__ == "__main__":
    main()
