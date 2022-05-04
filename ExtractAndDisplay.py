#!/usr/bin/env python3

# Producer needs to produce faster for smooth (fps)

import cv2
import threading
import queue

# Structure that keeps track of the queues, global lock, and the semaphores
class Queue:
    color_queue = queue.Queue()
    gray_queue = queue.Queue()
    qLock = threading.Lock()
    full = threading.Semaphore(0)
    empty = threading.Semaphore(10)

# Reads mp4 to generate original frames and puts them in the color queue
class ExtractFrame(threading.Thread):
    def __init__(self, file, queues, max_frames=999):
        # print("Init ExtractFrame")
        threading.Thread.__init__(self)
        self.file = file
        self.queues = queues
        self.max_frames = max_frames

    # generate frame and put in color queue
    def run(self):
        # print("Run Extract")
        # Initialize frame count to not go beyond the number of frames in the video
        count = 0

        # open video file
        vidcap = cv2.VideoCapture(self.file)

        success = True
        while success and count < self.max_frames:
            success, frame = vidcap.read()

            # Uses Empty cells, so check if any Empty available. Otherwise, block thread.
            self.queues.empty.acquire()

            # Insert into Q
            self.queues.qLock.acquire()
            self.queues.color_queue.put(frame)
            self.queues.qLock.release()

            self.queues.full.release()

            count += 1
        # print('Frame extraction complete')

# BW-izer thread. Reads color frames from q. Generates monochrome frames. Put monochrome frames into q2.
class ConvertToGrayscale(threading.Thread):

    def __init__(self, queues, max_frames):
        # print("Init ConvertFrame")
        threading.Thread.__init__(self)
        self.queues = queues
        self.max_frames = max_frames

    # Reads color frames -> generates monochrome.
    def run(self):
        # print("Run Convert")
        count = 0

        while count < self.max_frames:
            # Check if available frames from q, otherwise, block thread.
            if not self.queues.color_queue.empty():
                # Get frame.
                frame = self.queues.color_queue.get()

                # Convert frame to grayscale.
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                self.queues.qLock.acquire()
                self.queues.gray_queue.put(gray_frame)
                self.queues.qLock.release()

                count += 1
        # print('Frame conversion complete')


# Displayer thread. Reads monochrome frames. Display frames at a normal frame rate.
class DisplayFrame(threading.Thread):

    def __init__(self, queues, max_frames):
        # print("Init DisplayFrame")
        threading.Thread.__init__(self)
        self.queues = queues
        self.max_frames = max_frames

    # Produces empty Q cells. Thread takes frames from q2 and displays them
    def run(self):
        # print("Run DisplayFrame")
        count = 0

        # Go through each frame in the buffer until the buffer is empty.
        while count < self.max_frames:
            # Uses Full cells, so check if any Full available and any frames in q2. Otherwise, block thread.
            if not self.queues.gray_queue.empty():
                self.queues.full.acquire()

                self.queues.qLock.acquire()
                frame = self.queues.gray_queue.get()
                self.queues.qLock.release()

                self.queues.empty.release()

                count += 1

                cv2.imshow('Video', frame)
                if cv2.waitKey(21) and 0xFF == ord("q"):
                    break

        # print('Finished displaying all frames')
        # cleanup the windows
        cv2.destroyAllWindows()

def main():
    Q = Queue()

    # Create threads
    extractFrame = ExtractFrame("clip.mp4", Q, 72)
    convertToGrayscale = ConvertToGrayscale(Q, 72)
    displayFrame = DisplayFrame(Q, 72)

    # Start threads
    extractFrame.start()
    convertToGrayscale.start()
    displayFrame.start()


main()