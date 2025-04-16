from serial import Serial
import time

NUM_LEDS = 44
FPS = 300

target_colors = [[b'\xFF',b'\x00',b'\x00'], [b'\x00',b'\xFF',b'\x00'], [b'\x00',b'\x00',b'\xFF']]
def new_test_array(startColor):
    test_array = []
    ci = startColor
    for i in range(NUM_LEDS):
        test_array.append(target_colors[ci])
        ci = (ci + 1) % 3
    return test_array

ser = Serial("/dev/cu.usbserial-1110", 1000000)

def send_all(color_array): # len(color_array) = NUM_LEDS, contains unicode strings of length 6 (hex color value)
    for i in range(NUM_LEDS):
        for j in range(3):
            sendChar = color_array[i][j]
            ser.write(sendChar)
 
# Read line (wait for ready)
print(ser.readline())

test_array = new_test_array(0)

print("start sending")
cnt = 0

avgfps = 0
frame = 0
try:
    while True:
        start = time.time()
        # wait and send new array
        time.sleep(1.0/FPS)

        send_all(test_array)


        # populate array with new data
        cnt = (cnt + 1) % 3
        test_array = new_test_array(cnt)
        end = time.time()

        avgfps = (avgfps * frame + (end - start)) / (frame + 1)
        frame += 1
except KeyboardInterrupt:
    print(1 / avgfps)
