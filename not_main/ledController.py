from serial import Serial
from common import *

class LEDController:
    def __init__(self):
        self.ser = Serial("/dev/cu.usbserial-1110", 115200)
        self.ser.readline() # Read line (wait for ready)
    def send_all(self, color_array): # len(color_array) = NUM_LEDS, contains unicode strings of length 6 (hex color value)
        for i in range(NUM_LEDS):
            for j in range(6):
                sendChar: str = color_array[i][j]
                self.ser.write(sendChar.encode())
    def close(self):
        self.ser.close()
