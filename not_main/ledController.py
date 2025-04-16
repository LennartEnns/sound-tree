from serial import Serial
import time
from not_main.common import *
from not_main.converter import rgb_to_bytes

class LEDController:
    def __init__(self):
        self.ser = Serial(USB_SERIAL_PORT, USB_BAUD_RATE)
        self.ser.readline() # Read line (wait for ready)

    def send_all(self, byte_array): # array contains elements of 3 bytes
        for i in range(NUM_LEDS):
            for j in range(3):
                sendChar = byte_array[i][j]
                self.ser.write(sendChar)

    # Animation functions
    def blink(self, color, n_times, t_after_on = 0.3, t_after_off = 0.4):
        byte_color = rgb_to_bytes(color)
        black = rgb_to_bytes((0, 0, 0))
        for _ in range(n_times):
            self.send_all([byte_color for _ in range(NUM_LEDS)])
            time.sleep(t_after_on)
            self.send_all([black for _ in range(NUM_LEDS)])
            time.sleep(t_after_off)
    def show_snake(self, color, width = 5):
        byte_color = rgb_to_bytes(color)
        black = rgb_to_bytes((0, 0, 0))
        for index in range((-width) + 1, NUM_LEDS + 1):
            self.send_all([black for _ in range(0, index)] + [byte_color for i in range(index, index + width) if i >= 0] + [black for _ in range(index + width, NUM_LEDS)])
            time.sleep(0.1)
    def show_height(self, height, color): # height from 0 to 1
        byte_color = rgb_to_bytes(color)
        black = rgb_to_bytes((0, 0, 0))
        num_lit = round(height * NUM_LEDS)
        for i in range(1, num_lit):
            self.send_all([byte_color for _ in range(i)] + [black for _ in range(NUM_LEDS - i)])
            time.sleep(0.1)
        for _ in range(5):
            self.send_all([byte_color for _ in range(num_lit)] + [black for _ in range(NUM_LEDS - num_lit)])
            time.sleep(0.3)
            self.send_all([black for _ in range(NUM_LEDS)])
            time.sleep(0.4)
    def show_values_increasing(self, pairs: list):
        pairs_sorted = pairs.sort(lambda pair: pair[0])
        black = rgb_to_bytes((0, 0, 0))
        byte_colors = [rgb_to_bytes(pair[1]) for pair in pairs_sorted]
        colors_arr = [black for _ in range(NUM_LEDS)]
        for (i, pair) in enumerate(pairs_sorted):
            col = byte_colors[i]
            led_val = round(pair[0] * NUM_LEDS)
            for pos in range(led_val):
                colors_arr[pos] = col
                self.send_all(colors_arr)
                time.sleep(0.08)
            time.sleep(3)

    def close(self):
        self.ser.close()
