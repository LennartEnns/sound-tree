from serial import Serial
import time

NUM_LEDS = 44
FPS = 30

target_colors = ['FF00FF', '00FFFF', 'FFFF00']
def new_test_array(startColor):
    test_array = []
    ci = startColor
    for i in range(NUM_LEDS):
        test_array.append(target_colors[ci])
        ci = (ci + 1) % 3
    return test_array

ser = Serial("/dev/cu.usbserial-1110", 115200)

def send_all(color_array): # len(color_array) = NUM_LEDS, contains unicode strings of length 6 (hex color value)
    for i in range(NUM_LEDS):
        for j in range(6):
            sendChar = color_array[i][j]
            ser.write(sendChar.encode())

# Read line (wait for ready)
bs = ser.readline()
print(bs)

test_array = new_test_array(0)

cnt = 0
while True:
    # wait and send new array
    time.sleep(1.0/FPS)
    send_all(test_array)

    # populate array with new data
    cnt = (cnt + 1) % 3
    test_array = new_test_array(cnt)
