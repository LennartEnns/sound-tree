import threading
import time
from not_main.sender.sender import LEDSender
from not_main.common import NUM_LEDS,MAX_QUEUE_SIZE,FPS,time_millis

class TreeLEDSender(LEDSender):
    def __init__(self):
        self.frame_queue = []

        self.running = True
        self.send_thread = threading.Thread(target=self.run_send)

        self.send_thread.start()

    def close(self):
        self.running = False
        self.send_thread.join()
    
    def run_send(self):
        last_send = 0
        while self.running:
            if (time_millis() - last_send) < (1000/FPS):
                continue

            queue_len = len(self.frame_queue)
            if queue_len > 0:
                self.send_all(self.frame_queue.pop())
                last_send = time_millis()

    def send_all(self, byte_array): # array contains elements of 3 bytes
        for i in range(NUM_LEDS):
            for j in range(3):
                sendChar = byte_array[i][j]
                self.ser.write(sendChar)

    def enqueue_frame(self, frame):
        queue_len = len(self.frame_queue)
        if queue_len >= MAX_QUEUE_SIZE:
            self.frame_queue = [frame]
        else:
            self.frame_queue.insert(0, frame)