from serial import Serial
from time import time

ser = Serial("/dev/cu.usbserial-1110", 115200)
ser.readline()


