#!/usr/bin/env python3

import csv
import random
import os
import cv2
import matplotlib.pyplot as plt
from datetime import datetime

CAMERA_INDEX = 0
CUP_IMAGE_PATH = "cup.png"
BLOCK_IMAGE_PATH = "legoblock.png"
OUTPUT_CSV_PATH = "object_positions.csv"
CUP_SCALE = 0.7
BLOCK_SCALE = 0.8
# Large boundary coordinates (x_min, y_min, x_max, y_max)
LARGE_BOUNDARY = (80, 30, 580, 430)
# Exclusion zone coordinates (x_min, y_min, x_max, y_max)
EXCLUSION_ZONE = (280, 0, 388, 120)
MIN_DISTANCE_BETWEEN_OBJECTS = 110
MIN_DISTANCE_BETWEEN_CONFIGS = 23.5
NUM_POSITIONS = 100


def is_in_exclusion_zone(x, y, img_width, img_height):
    excl_x1, excl_y1, excl_x2, excl_y2 = EXCLUSION_ZONE
    img_x1, img_y1 = x, y
    img_x2, img_y2 = x + img_width, y + img_height
    overlap = not (img_x2 < excl_x1 or img_x1 > excl_x2 or img_y2 < excl_y1 or img_y1 > excl_y2)
    return overlap


def get_random_position(img_width, img_height, other_pos=None, other_size=None):
    min_x, min_y, max_x, max_y = LARGE_BOUNDARY
    max_x = max_x - img_width
    max_y = max_y - img_height
    min_distance = MIN_DISTANCE_BETWEEN_OBJECTS
    
    for attempt in range(1000):
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        
        if is_in_exclusion_zone(x, y, img_width, img_height):
            continue
        
        if other_pos is not None and other_size is not None:
            other_x, other_y = other_pos
            other_w, other_h = other_size
            center_x = x + img_width // 2
            center_y = y + img_height // 2
            other_center_x = other_x + other_w // 2
            other_center_y = other_y + other_h // 2
            dx = abs(center_x - other_center_x)
            dy = abs(center_y - other_center_y)
            
            if dx < min_distance or dy < min_distance:
                continue
        
        return x, y
    
    return min_x, min_y


def is_far_enough(cup_pos, block_pos, saved_positions):
    for saved_cup, saved_block in saved_positions:
        cup_dist = ((cup_pos[0] - saved_cup[0])**2 + (cup_pos[1] - saved_cup[1])**2)**0.5
        block_dist = ((block_pos[0] - saved_block[0])**2 + (block_pos[1] - saved_block[1])**2)**0.5
        
        if cup_dist < MIN_DISTANCE_BETWEEN_CONFIGS or block_dist < MIN_DISTANCE_BETWEEN_CONFIGS:
            return False
    
    return True


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_filename = os.path.join(script_dir, OUTPUT_CSV_PATH)
    
    cup_path = os.path.join(script_dir, CUP_IMAGE_PATH)
    block_path = os.path.join(script_dir, BLOCK_IMAGE_PATH)
    
    cup_img = cv2.imread(cup_path, cv2.IMREAD_UNCHANGED)
    block_img = cv2.imread(block_path, cv2.IMREAD_UNCHANGED)
    
    cup_img = cv2.resize(cup_img, None, fx=CUP_SCALE, fy=CUP_SCALE, interpolation=cv2.INTER_AREA)
    block_img = cv2.resize(block_img, None, fx=BLOCK_SCALE, fy=BLOCK_SCALE, interpolation=cv2.INTER_AREA)
    
    cup_width = cup_img.shape[1]
    cup_height = cup_img.shape[0]
    block_width = block_img.shape[1]
    block_height = block_img.shape[0]
    
    saved_positions = []
    
    print(f"Generating {NUM_POSITIONS} well-distributed positions...")
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'cup_x', 'cup_y', 'block_x', 'block_y'])
        
        attempts = 0
        max_attempts = NUM_POSITIONS * 10000
        
        while len(saved_positions) < NUM_POSITIONS and attempts < max_attempts:
            attempts += 1
            
            cup_pos = get_random_position(cup_width, cup_height)
            block_pos = get_random_position(block_width, block_height, 
                                           other_pos=cup_pos,
                                           other_size=(cup_width, cup_height))
            
            if is_far_enough(cup_pos, block_pos, saved_positions):
                saved_positions.append((cup_pos, block_pos))
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([timestamp, cup_pos[0], cup_pos[1], block_pos[0], block_pos[1]])
                
                if len(saved_positions) % 10 == 0:
                    print(f"Generated {len(saved_positions)}/{NUM_POSITIONS} positions...")
    
    print(f"\n✓ Successfully generated {len(saved_positions)} positions")
    print(f"  Saved to: {csv_filename}")
    print(f"  Total attempts: {attempts}")
    
    cup_x = [pos[0][0] for pos in saved_positions]
    cup_y = [pos[0][1] for pos in saved_positions]
    block_x = [pos[1][0] for pos in saved_positions]
    block_y = [pos[1][1] for pos in saved_positions]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    
    ax1.scatter(cup_x, cup_y, c='blue', alpha=0.6, s=50)
    ax1.set_xlim(0, 640)
    ax1.set_ylim(480, 0)
    ax1.set_xlabel('X Position')
    ax1.set_ylabel('Y Position')
    ax1.set_title('Cup Positions')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal')
    
    ax2.scatter(block_x, block_y, c='red', alpha=0.6, s=50)
    ax2.set_xlim(0, 640)
    ax2.set_ylim(480, 0)
    ax2.set_xlabel('X Position')
    ax2.set_ylabel('Y Position')
    ax2.set_title('Block Positions')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
