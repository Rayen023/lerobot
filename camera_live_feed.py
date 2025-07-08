#!/usr/bin/env python3
"""
Simple script to open a live camera feed using OpenCV.
Camera: OpenCV Camera @ /dev/video0
"""

import sys

import cv2


def main():
    # Open camera (using device ID 0 which corresponds to /dev/video0)
    cap = cv2.VideoCapture(1)

    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera /dev/video0")
        sys.exit(1)

    # Set camera properties to match detected specifications
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    print("Camera opened successfully!")
    print("Press 'q' to quit or 'ESC' to exit")

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture frame")
                break

            # Display the frame
            cv2.imshow("Live Camera Feed - /dev/video0", frame)

            # Check for key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:  # 'q' or ESC key
                break

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released and windows closed")


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
