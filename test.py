from soundTree.sender.webSender import WebSender
import time

test_frame = [(b'\xFF', b'\x00', b'\x00'), (b'\x00', b'\x07', b'\x00'), (b'\x00', b'\r', b'\x00'), (b'\x00', b'\x12', b'\x00'), (b'\x00', b'\x14', b'\x00'), (b'\x00', b'\x17', b'\x00'), (b'\x00', b"'", b'\x00'), (b'\x00', b'R', b'\x00'), (b'\x00', b'\x99', b'\x00'), (b'\x00', b'\xe2', b'\x00'), (b'\x00', b'\xff', b'\x00'), (b'\x00', b'\xda', b'\x00'), (b'\x00', b'\x8d', b'\x00'), (b'\x00', b'I', b'\x00'), (b'\x00', b"'", b'\x00'), (b'\x00', b'%', b'\x00'), (b'\x00', b'/', b'\x00'), (b'\x00', b'6', b'\x00'), (b'\x00', b'3', b'\x00'), (b'\x00', b"'", b'\x00'), (b'\x00', b'\x1a', b'\x00'), (b'\x00', b'\x11', b'\x00'), (b'\x00', b'\x0b', b'\x00'), (b'\x00', b'\x0b', b'\x00'), (b'\x00', b'\x0e', b'\x00'), (b'\x00', b'\x11', b'\x00'), (b'\x00', b'\x11', b'\x00'), (b'\x00', b'\r', b'\x00'), (b'\x00', b'\x08', b'\x00'), (b'\x00', b'\x04', b'\x00'), (b'\x00', b'\x02', b'\x00'), (b'\x00', b'\x01', b'\x00'), (b'\x00', b'\x01', b'\x00'), (b'\x00', b'\x00', b'\x00'), (b'\x00', b'\x00', b'\x00'), (b'\x00', b'\x00', b'\x00'), (b'\x00', b'\x00', b'\x00'), (b'\x00', b'\x00', b'\x00'), (b'\x00', b'\x01', b'\x00'), (b'\x00', b'\x02', b'\x00'), (b'\x00', b'\x02', b'\x00'), (b'\x00', b'\r', b'\x00'), (b'\x00', b'\x01', b'\x00'), (b'\x00', b'\x05', b'\x00')]

web = WebSender()

#web.enqueue_frame(test_frame)
time.sleep(5)

print("start")
start_time = time.time()
while time.time() - start_time <= 10:
    web.enqueue_frame(test_frame)
    time.sleep(1/500)
web.close()