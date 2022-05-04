#!/usr/bin/env python3

# frame cout
count = 0

# get frame
input_file = "frames/frame_%04d.jpg" %count


# read file
current_frame = cv2.imread(input_file, cv2.IMREAD_COLOR)

while current_frame is not None:

    # convert the image to grayscale
    gray_scale_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    
    # generate output file name
    output_file_name = "gray_frames/grayscale_%04d.jpg" %count

    # write output file
    cv2.imwrite(output_file_name, gray_scale_frame)

    count += 1

    # generate input file name for the next frame
    input_file = "frames/frame_%04d.jpg" %count
    
    # load the next frame
    current_frame = cv2.imread(input_file, cv2.IMREAD_COLOR)