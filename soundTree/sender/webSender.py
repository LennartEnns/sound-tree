from soundTree.sender.sender import LEDSender
from websockets.sync.server import serve
import threading
from soundTree.common import *

class WebSender(LEDSender):
    def __init__(self):
        
        self.frame_queue = []

        self.running = True
        self.send_thread = threading.Thread(target=self.ws_run)

        self.send_thread.start()

    def ws_run(self):
        with serve(self.run_send, WEB_IP, WS_PORT) as self.server:
            self.server.serve_forever()

    def run_send(self, ws):
        last_send = 0

        avgFPS, ctr = 0, 0

        time_start = time_millis()
        while self.running:
            if (time_millis() - last_send) < (1000/FPS):
                continue

            queue_len = len(self.frame_queue)
            if queue_len > 0:
                ws.send(list(sum(self.frame_queue.pop(), ())))
                last_send = time_millis()

                if DEBUG:
                    avgFPS = ((avgFPS * ctr) + (1000/ (last_send - time_start))) / (ctr + 1)
                    ctr += 1
                    time_start = last_send
        
        debug_print("AVG FPS:", avgFPS)
    
    def close(self):
        self.running = False
        self.server.shutdown()
        self.send_thread.join()
    
    def enqueue_frame(self, frame):
        queue_len = len(self.frame_queue)
        if queue_len >= MAX_QUEUE_SIZE:
            self.frame_queue = [frame]
            #debug_print("sender not fast enough!")
        else:
            self.frame_queue.insert(0, frame)