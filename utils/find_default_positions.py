#!/usr/bin/env python3
"""
Helper script to find and record good default positions for the SO101 follower robot.
Run this script, manually position your robot in a good starting pose, then press Enter.
"""

from lerobot.robots.so101_follower import SO101Follower, SO101FollowerConfig

def find_default_positions():
    """Interactive script to determine good default positions."""
    
    # Configure the robot
    robot_config = SO101FollowerConfig(
        port="/dev/ttyACM1",
        id="my_follower_arm_1",
    )
    
    robot = SO101Follower(robot_config)
    robot.connect()
    
    try:
        print("="*60)
        print("FINDING DEFAULT POSITIONS FOR SO101 FOLLOWER")
        print("="*60)
        print("\nInstructions:")
        print("1. Manually move your robot to a good starting position")
        print("2. This should be a pose that:")
        print("   - Is safe and stable")
        print("   - Provides good workspace access")
        print("   - Is repeatable")
        print("   - Won't collide with objects")
        print("3. Press ENTER when robot is in desired position")
        print("\nCurrent robot positions will be read and displayed...")
        
        input("\nPress ENTER when robot is positioned correctly: ")
        
        # Read current position
        current_pos = robot.bus.sync_read("Present_Position")
        
        print("\n" + "="*60)
        print("CURRENT ROBOT POSITIONS:")
        print("="*60)
        
        print("\n# Copy these values to your inference script:")
        print("DEFAULT_POSITIONS = {")
        for motor, pos in current_pos.items():
            print(f'    "{motor}": {pos:.1f},')
        print("}")
        
        print("\n" + "="*60)
        print("POSITION DETAILS:")
        print("="*60)
        for motor, pos in current_pos.items():
            print(f"{motor:15s}: {pos:8.1f}")
            
        print("\nThese positions have been recorded.")
        print("Update your inference script with these DEFAULT_POSITIONS values.")
        
    finally:
        robot.disconnect()
        print("\nRobot disconnected safely.")

if __name__ == "__main__":
    find_default_positions()
