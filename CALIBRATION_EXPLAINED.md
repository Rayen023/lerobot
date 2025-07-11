# LeRobot Motor Calibration Values Explained

## Overview

This document explains the calibration values in LeRobot configuration files (like `my_follower_arm_1.json`) and why they use the range 0-4095 instead of degrees.

## Why 0-4095 Range?

### Encoder Resolution
- Most servo motors in LeRobot use **12-bit encoders**
- 12 bits = 2^12 = 4096 possible positions (0 to 4095)
- Each "tick" represents one discrete position the motor can detect

### Physical vs Digital Mapping
```
Physical rotation:  0° to 360° (one full turn)
Digital encoder:    0 to 4095 (4096 steps)
Resolution:         360° ÷ 4096 = ~0.088° per encoder tick
```

So each encoder step represents approximately **0.088 degrees** of motor shaft rotation.

## What is Homing Offset?

The `homing_offset` is **NOT** an offset from max or min values. Instead, it's a **coordinate transformation** that centers the robot's coordinate system around a meaningful reference point.

### The Problem Without Homing Offset

When you assemble a robot, motors can be installed in any rotational position. For example:
- Robot A's shoulder might read encoder value 1500 when pointing forward
- Robot B's shoulder might read encoder value 2800 when pointing forward
- Same physical position, different encoder readings!

### The Solution: Homing Offset

During calibration:
1. Move each joint to its **middle position** (physically centered)
2. System reads the current encoder value
3. Calculates an offset to make this position equal **2047** (middle of 0-4095)
4. Stores this offset for future use

## Motor Type Differences

### Dynamixel Motors
```
Present_Position = Actual_Position + Homing_Offset
```

### Feetech Motors  
```
Present_Position = Actual_Position - Homing_Offset
```

## Real Example: Gripper Motor

Let's analyze this calibration from your file:

```json
"gripper": {
    "id": 6,
    "drive_mode": 0,
    "homing_offset": -1956,
    "range_min": 1974,
    "range_max": 3221
}
```

### What Happened During Assembly

1. **Physical Setup**: Gripper was positioned at its middle position (half open)
2. **Raw Reading**: Motor encoder read approximately **4003**
3. **Calculation**: To center this at 2047: `2047 - 4003 = -1956`
4. **Result**: Homing offset of -1956

### Physical Interpretation

```
Raw position: 4003 encoder ticks
Degrees: 4003 × 0.088° ≈ 352°
```

This means the motor was assembled about **352 degrees** away from where the encoder naturally considers "zero". This is completely normal!

### Working Range

```
Range: 1974 to 3221 (in calibrated coordinates)
Span: 3221 - 1974 = 1247 ticks
Physical motion: 1247 × 0.088° ≈ 110 degrees
```

The gripper can move about 110 degrees total.

## Complete Example: Shoulder Pan Joint

```json
"shoulder_pan": {
    "id": 1,
    "drive_mode": 0,
    "homing_offset": -191,
    "range_min": 708,
    "range_max": 3398
}
```

### During Calibration

1. **Middle Position**: Shoulder moved to center of its range
2. **Raw Reading**: ~2238 (because 2238 + (-191) = 2047)
3. **Offset Calculated**: -191 to center the coordinate system

### Final Coordinate System

- **Leftmost limit**: 708 (in calibrated coordinates)
- **Center**: 2047 (always the center after calibration)
- **Rightmost limit**: 3398 (in calibrated coordinates)
- **Total range**: 3398 - 708 = 2690 ticks ≈ 237 degrees

## Benefits of This System

### 1. **Robot Portability**
```
Robot A shoulder at "center": reads 2047
Robot B shoulder at "center": reads 2047
→ Same policy works on both robots!
```

### 2. **Meaningful Coordinates**
- 2047 = center of joint range
- Values < 2047 = left/down from center  
- Values > 2047 = right/up from center

### 3. **Safety Boundaries**
The `range_min` and `range_max` ensure motors don't exceed physical limits.

## Key Takeaways

1. **0-4095 range** comes from 12-bit encoder resolution
2. **Homing offset** centers the coordinate system, not offset from limits
3. **Large offsets** (like -1956) are normal - they just reflect assembly position
4. **This system enables** neural network policies to transfer between robots
5. **Each encoder tick** ≈ 0.088 degrees of physical rotation

## Configuration File Structure

```json
{
    "motor_name": {
        "id": 1,                    // Motor ID on the bus
        "drive_mode": 0,            // 0=normal, 1=inverted direction
        "homing_offset": -191,      // Coordinate transformation offset
        "range_min": 708,           // Minimum safe position (calibrated coords)
        "range_max": 3398          // Maximum safe position (calibrated coords)
    }
}
```

The calibration system transforms arbitrary assembly positions into a standardized coordinate system that works consistently across different robot instances.

## Identifying Your Motor Type

### Feetech vs Dynamixel Motors

LeRobot supports two main types of servo motors, and knowing which type you have is important because they handle homing offsets differently:

#### SO-101 Uses Feetech Motors

Based on the SO-101 documentation, your robot uses **STS3215 Feetech motors**. Here's the evidence:

- **Documentation**: "The follower arm uses 6x STS3215 motors with 1/345 gearing"
- **Code Implementation**: Uses `FeetechMotorsBus` in the robot configuration

### How to Confirm Your Motor Type

#### 1. **Check Physical Motor Labels**
Look at the motors on your robot - they should have "STS3215" printed on them for Feetech motors.

#### 2. **Check Your Robot's Configuration Code**
Look for these imports in your robot's code:
- `FeetechMotorsBus` → You have Feetech motors
- `DynamixelMotorsBus` → You have Dynamixel motors

#### 3. **Verify the Homing Offset Formula**
The formula differs between motor types:

**Feetech Motors (Your SO-101):**
```
Present_Position = Actual_Position - Homing_Offset
```

**Dynamixel Motors:**
```
Present_Position = Actual_Position + Homing_Offset
```

### Your Gripper Example Explained

For your gripper with `homing_offset: -1956`:

1. **Target center**: 2047 (middle of 0-4095 range)
2. **Actual raw reading**: ~4003 (because 2047 - (-1956) = 4003)
3. **Calibrated position**: 4003 - (-1956) = 2047 ✓

The large negative offset means your gripper motor was assembled almost a full rotation away from the encoder's natural center position.

### Motor Type Comparison

| Aspect | Feetech (Your Motors) | Dynamixel |
|--------|----------------------|-----------|
| **Protocol** | Protocol 0 (older) | Protocol 2.0 (newer) |
| **Homing Formula** | Present = Actual - Offset | Present = Actual + Offset |
| **Typical Use** | Cost-effective robotics | Higher-end robotics |
| **Models** | STS3215, STS3250, etc. | XL330, XM430, etc. |
| **Resolution** | 12-bit (0-4095) | 12-bit (0-4095) |
| **Cost** | Lower cost | Higher cost |

### Why SO-101 Uses Feetech

Your SO-101 uses **Feetech STS3215 motors** because they offer an excellent balance of:
- **Performance**: Sufficient precision for research and education
- **Cost**: More affordable than Dynamixel alternatives  
- **Reliability**: Proven track record in robotics applications
- **Compatibility**: Well-supported in LeRobot framework

This makes the SO-101 accessible for educational institutions and researchers while maintaining professional-grade capabilities.

## Understanding 12-bit Encoders: Hardware vs Software

### What "12-bit encoder" Really Means

You're absolutely right! The **12-bit encoder is a hardware component** inside the servo motor itself. Here's how it works:

#### Hardware Level
- Inside each servo motor, there's a physical **magnetic or optical encoder** attached to the motor shaft
- This encoder has **12-bit resolution**, meaning it can distinguish between 2^12 = 4096 different angular positions per full rotation
- The encoder hardware directly outputs digital values from 0 to 4095
- This conversion from physical rotation to digital value happens **entirely in hardware**

#### Communication Protocol
When the software asks "what's your current position?", the motor's internal microcontroller:
1. Reads the hardware encoder (gets a value 0-4095)
2. Applies any internal offsets (like homing_offset)
3. Sends this digital value over the communication bus (USB/serial)

#### No Software Conversion Needed
The software receives the position as a **ready-to-use integer** (like 2047, 3221, etc.). There's no analog-to-digital conversion happening in the software - that already happened inside the motor.

### Comparison with Other Systems

#### 12-bit vs Higher Resolution
- **12-bit**: 4096 positions per rotation (0.088° resolution)
- **14-bit**: 16384 positions per rotation (0.022° resolution) 
- **16-bit**: 65536 positions per rotation (0.0055° resolution)

#### Why 12-bit is Common
- Good balance between **precision** and **cost**
- 0.088° resolution is sufficient for most robotic applications
- Faster communication (smaller data packets)
- Less computational overhead

### The Data Flow

```
Physical rotation → Hardware encoder → Digital value (0-4095) → Communication bus → Software
```

So when you see values like:
- `"homing_offset": -1956` 
- `"range_min": 708`
- `"range_max": 3398`

These are all **hardware-generated integers** that represent actual encoder tick counts from the physical encoder inside the motor. The software just does coordinate transformations and safety checks on these pre-digitized values.

The beauty is that the motor handles all the complex analog-to-digital conversion internally, and the software just works with clean, discrete position values!

## Comparison with Industrial Robots (KUKA)

### Industrial Robot Approach
KUKA robots use **absolute encoders** on each joint, but they handle the data very differently:

#### 1. **Higher Resolution Encoders**
- KUKA typically uses **17-bit to 20-bit encoders** (131,072 to 1,048,576 positions per revolution)
- Much higher precision than the 12-bit servos (4,096 positions)
- Some use multi-turn encoders that track multiple full rotations

#### 2. **Software Coordinate Transformation**
Instead of raw encoder values, KUKA's control system provides:

```python
# KUKA returns meaningful units directly:
joint_positions = [45.2, -30.5, 90.0, 0.0, 60.3, -15.7]  # degrees
cartesian_pose = {
    'x': 500.2,    # mm
    'y': 300.1,    # mm  
    'z': 400.5,    # mm
    'a': 45.0,     # degrees (rotation around X)
    'b': 0.0,      # degrees (rotation around Y) 
    'c': 90.0      # degrees (rotation around Z)
}
```

#### 3. **Multiple Coordinate Systems**
KUKA robots provide positions in several formats:
- **Joint angles** (degrees for each of the 6 joints)
- **Cartesian coordinates** (X,Y,Z position + orientation)
- **Tool coordinates** (relative to the end effector)
- **Base coordinates** (relative to robot base)

### Key Differences from LeRobot Servos

| Aspect | LeRobot Servos | KUKA Robots |
|--------|----------------|-------------|
| **Raw Data** | Encoder ticks (0-4095) | Already converted to degrees/mm |
| **Conversion** | Software does coordinate transform | Robot controller does everything |
| **Precision** | 12-bit (~0.088°) | 17-20 bit (~0.003°) |
| **Coordinate Systems** | Single joint space | Multiple (joint, cartesian, tool, etc.) |
| **Calibration** | Manual homing offset | Factory calibrated + automatic referencing |

### KUKA Programming Example

```python
# KUKA robot (using their API)
robot = KUKA_Robot()

# Get current position - already in meaningful units
current_joints = robot.get_joint_position()  # [j1°, j2°, j3°, j4°, j5°, j6°]
current_pose = robot.get_cartesian_position()  # {x, y, z, a, b, c}

# Move to position - specify in degrees/mm
robot.move_to_joint([30, -45, 90, 0, 45, -30])  # degrees
robot.move_to_pose({'x': 600, 'y': 200, 'z': 300, 'a': 0, 'b': 0, 'c': 90})
```

### Why the Difference?

#### Industrial vs Research/Hobbyist
- **KUKA**: Industrial robots designed for precision manufacturing
- **LeRobot**: Research/educational robots optimized for cost and learning

#### Control Philosophy
- **KUKA**: Sophisticated internal controller handles all low-level details
- **LeRobot**: Expose more low-level control for learning and experimentation

#### Cost vs Capability
- **KUKA**: $50,000-500,000+ robots with advanced control systems
- **LeRobot**: $1,000-10,000 robots with simpler, more accessible control

The fundamental difference is that KUKA robots are "black boxes" that give you high-level, meaningful coordinates, while LeRobot servos expose the raw encoder data and let you build the coordinate systems yourself.
