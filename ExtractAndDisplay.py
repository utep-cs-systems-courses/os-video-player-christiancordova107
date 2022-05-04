#!/usr/bin/env python3


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
        threading.Thread.__init__(self)
        self.file = file
        self.queues = queues
        self.max_frames = max_frames

    # generate frame and put in color queue
    def run(self):
        # Initialize frame count to not go beyond the number of frames in the video
        count = 0

        # open video file
        vidcap = cv2.VideoCapture(self.file)

        success = True
        while success and count < self.max_frames:
            success, frame = vidcap.read()

            # Uses Empty cells, so check if any Empty available. Otherwise, block thread.
            self.queues.empty.acquire()

            # Insert into color queue
            self.queues.qLock.acquire()
            self.queues.color_queue.put(frame)
            self.queues.qLock.release()

            self.queues.full.release()

            count += 1

# thread. Reads color frames from color queue. Generates monochrome frames. Put monochrome frames into gray queue.
class ConvertToGrayscale(threading.Thread):

    def __init__(self, queues, max_frames):
        threading.Thread.__init__(self)
        self.queues = queues
        self.max_frames = max_frames

    # Reads color frames -> generates monochrome.
    def run(self):
        count = 0

        while count < self.max_frames:
            # Check if available frames from color queue, otherwise, block thread.
            if not self.queues.color_queue.empty():
                # Get frame.
                frame = self.queues.color_queue.get()

                # Convert frame to grayscale.
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                self.queues.qLock.acquire()
                self.queues.gray_queue.put(gray_frame)
                self.queues.qLock.release()

                count += 1


# Displayer thread. Reads monochrome frames. Display frames at a normal frame rate.
class DisplayFrame(threading.Thread):

    def __init__(self, queues, max_frames):
        threading.Thread.__init__(self)
        self.queues = queues
        self.max_frames = max_frames

    # Produces empty cells. Thread takes frames from gray queue and displays them
    def run(self):
        count = 0

        # Go through each frame in the buffer until the buffer is empty.
        while count < self.max_frames:
            # Uses Full cells, so check if any Full available and any frames in gray queue. Otherwise, block thread.
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

        
        # remove all windows
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