#!/usr/bin/env python3
"""
Simple script to check connected cameras using OpenCV.
This script will scan for available camera devices and display basic information.
"""

import sys
import cv2


def check_cameras(max_cameras=10):
    """
    Check for connected cameras by trying to open each camera index.

    Args:
        max_cameras (int): Maximum number of camera indices to check

    Returns:
        list: List of available camera indices
    """
    available_cameras = []

    print("Checking for connected cameras...")
    print("-" * 40)

    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)

        if cap.isOpened():
            # Try to read a frame to confirm the camera is working
            ret, frame = cap.read()
            if ret:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)

                print(f"Camera {i}: Available")
                print(f"  Resolution: {width}x{height}")
                print(f"  FPS: {fps}")
                print()

                available_cameras.append(i)
            else:
                print(f"Camera {i}: Detected but cannot read frames")

        cap.release()

    return available_cameras


def test_camera(camera_index):
    """
    Test a specific camera by opening a live feed.
    Press 'q' to quit the live feed.

    Args:
        camera_index (int): Index of the camera to test
    """
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print(f"Error: Cannot open camera {camera_index}")
        return

    print(f"Testing camera {camera_index}. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Cannot read frame")
            break

        # Add camera info overlay
        cv2.putText(
            frame,
            f"Camera {camera_index}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            "Press 'q' to quit",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

        cv2.imshow(f"Camera {camera_index}", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main function to check cameras and optionally test one."""
    available_cameras = check_cameras()

    if not available_cameras:
        print("No cameras found!")
        return

    print(f"Found {len(available_cameras)} camera(s): {available_cameras}")

    # Ask user if they want to test a camera
    try:
        choice = input(
            "\nEnter camera index to test (or press Enter to exit): "
        ).strip()

        if choice:
            camera_index = int(choice)
            if camera_index in available_cameras:
                test_camera(camera_index)
            else:
                print(f"Camera {camera_index} is not available.")
    except ValueError:
        print("Invalid input. Exiting.")
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()
