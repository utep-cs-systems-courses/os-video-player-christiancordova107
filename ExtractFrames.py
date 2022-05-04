#!/usr/bin/env python3

import cv2

file_name = 'clip.mp4'

vid_cap = cv2.VideoCapture(file_name)
success,image = vid_cap.read()
count = 0

while success:
  cv2.imwrite("frames/frame_%04d.jpg" % count, image)     # save frame as JPEG file      
  success,image = vid_cap.read()
  count += 1