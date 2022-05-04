#!/usr/bin/env python3

import cv2,time

delay = 42       

# frame count
count = 0

# Generate the filename for the first current_frame 
gray_frame_path = "gray_frame/grayscale_%04d.jpg" %count

# load the current_frame
current_frame = cv2.imread(gray_frame_path)

while current_frame is not None:
    # Display the current_frame in a window called "Video"
    cv2.imshow('Video', current_frame)

    # Wait for 42 ms and check if the user wants to quit
    if cv2.waitKey(delay):
        break    
    
    # get the next current_frame filename
    count += 1
    gray_frame_path = "gray_frames/grayscale_%04d.jpg" %count

    # Read the next current_frame file
    current_frame = cv2.imread(gray_frame_path)

# make sure we cleanup the windows, otherwise we might end up with a mess
cv2.destroyAllWindows()