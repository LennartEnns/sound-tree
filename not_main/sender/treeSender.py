import threading
import time
from serial import Serial

from not_main.sender.sender import LEDSender
from not_main.common import *


class TreeLEDSender(LEDSender):
    def __init__(self):
        self.ser = Serial(USB_SERIAL_PORT, USB_BAUD_RATE)
        self.ser.readline() # Read line (wait for ready)
        self.frame_queue = []

        self.running = True
        self.send_thread = threading.Thread(target=self.run_send)

        self.send_thread.start()

    def close(self):
        self.running = False
        self.send_thread.join()
        self.ser.close()
    
    def run_send(self):
        last_send = 0

        avgFPS, ctr = 0

        while self.running:
            if DEBUG:
                time_start = time_millis()
            
            if (time_millis() - last_send) < (1000/FPS):
                continue

            queue_len = len(self.frame_queue)
            if queue_len > 0:
                self.send_all(self.frame_queue.pop())
                last_send = time_millis()

                if DEBUG:
                    avgFPS = ((avgFPS * ctr) + (1000/ (last_send - time_start))) / (ctr + 1)
                    ctr += 1
            else:
                debug_print("calculation not fast enough!")
        
        debug_print("AVG FPS:", avgFPS)

    def send_all(self, byte_array): # array contains elements of 3 bytes
        for i in range(NUM_LEDS):
            for j in range(3):
                sendChar = byte_array[i][j]
                self.ser.write(sendChar)

    def enqueue_frame(self, frame):
        queue_len = len(self.frame_queue)
        if queue_len >= MAX_QUEUE_SIZE:
            self.frame_queue = [frame]
            debug_print("sender not fast enough!")
        else:
            self.frame_queue.insert(0, frame)