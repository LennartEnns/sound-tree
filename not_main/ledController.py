from serial import Serial
import time
from not_main.common import *
from not_main.converter import rgb_to_hex

class LEDController:
    def __init__(self):
        self.ser = Serial("/dev/cu.usbserial-1110", 115200)
        self.ser.readline() # Read line (wait for ready)
    def send_all(self, hex_array): # len(color_array) = NUM_LEDS, contains unicode strings of length 6 (hex color value)
        for i in range(NUM_LEDS):
            for j in range(6):
                sendChar: str = hex_array[i][j]
                self.ser.write(sendChar.encode())
    def blink(self, color, n_times, t_after_on = 0.3, t_after_off = 0.4):
        hex_color = rgb_to_hex(color)
        black = rgb_to_hex((0, 0, 0))
        for _ in range(n_times):
            self.send_all([hex_color for _ in range(NUM_LEDS)])
            time.sleep(t_after_on)
            self.send_all([black for _ in range(NUM_LEDS)])
            time.sleep(t_after_off)
    def show_snake(self, color, width = 5):
        hex_color = rgb_to_hex(color)
        black = rgb_to_hex((0, 0, 0))
        for index in range((-width) + 1, NUM_LEDS + 1):
            self.send_all([black for _ in range(0, index)] + [hex_color for i in range(index, index + width) if i >= 0] + [black for _ in range(index + width, NUM_LEDS)])
            time.sleep(0.1)
    def show_height(self, height, color): # height from 0 to 1
        hex_color = rgb_to_hex(color)
        black = rgb_to_hex((0, 0, 0))
        num_lit = round(height * NUM_LEDS)
        for i in range(1, num_lit):
            self.send_all([hex_color for _ in range(i)] + [black for _ in range(NUM_LEDS - i)])
            time.sleep(0.1)
        for _ in range(5):
            self.send_all([hex_color for _ in range(num_lit)] + [black for _ in range(NUM_LEDS - num_lit)])
            time.sleep(0.3)
            self.send_all([black for _ in range(NUM_LEDS)])
            time.sleep(0.4)
        
    def close(self):
        self.ser.close()
