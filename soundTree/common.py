import pyaudio
import time
import math
import numpy as np

# enable debug values
DEBUG = False

# Audio configuration
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # Mono channel
RATE = 44100              # Sampling rate in Hz
CHUNK = 1024              # Number of samples per frame
# CHUNK = 2048

# Refinement configuration
MIN_FREQ_MUSIC = 20
MAX_FREQ_MUSIC = 12000
MIN_FREQ_HUMAN = 50
MAX_FREQ_HUMAN = 2000

EPSILON = 1e-8  # Small value to prevent log(0)

# Frequency range used for maximum level tracking
LEVEL_TRACKING_MIN_FREQ = 200
LEVEL_TRACKING_MAX_FREQ = MAX_FREQ_MUSIC

# Beat detection constants
SNARE_MIN_FREQ = 6000
SNARE_MAX_FREQ = 7000
KICK_MIN_FREQ = 80
KICK_MAX_FREQ = 200

MIN_SNARE_AVG_MAG = 0.23 # Average amplitude threshold for snare detection
MIN_KICK_AVG_MAG = 0.5
MIN_BEAT_INTERVAL = 1200 # ms

NUM_LEDS = 44
FPS = 300
USB_SERIAL_PORT = "/dev/cu.usbserial-1110"
USB_BAUD_RATE = 1000000
MAX_QUEUE_SIZE = 3

# Web Interface
WEB_IP = "localhost"
WS_PORT = 8080

class DIST_MODES:
    MUSIC = 0
    HUMAN = 1
    LINEAR = 2

# Weight function for magnitude adjustment (Use only with values in range [0,1])
# weight_func = lambda x: math.log((x + 1) * 1.1)
wf_const = (math.log(0.23) + 3.6)
weight_func = lambda x: ((math.log(x + 0.03) + 3.6)) if x <= 0.2 else wf_const

# Utils
def debug_print(*args):
    if DEBUG:
        print(args)

def time_millis():
    return time.time() * 1000
