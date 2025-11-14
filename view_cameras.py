#!/usr/bin/env python

import cv2

# Open cameras
cap0 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(2)

print("Press 'q' to quit")

while True:
    ret0, frame0 = cap0.read()
    ret2, frame2 = cap2.read()
    
    if ret0:
        cv2.imshow('Camera 0', frame0)
    if ret2:
        cv2.imshow('Camera 2', frame2)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap0.release()
cap2.release()
cv2.destroyAllWindows()
