import pyaudio
import time
import math

# Audio configuration
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # Mono channel
RATE = 44100              # Sampling rate in Hz
CHUNK = 1024              # Number of samples per frame
# CHUNK = 2048

# Refinement configuration
NORM_TARGET = 1           # Target level to normalize to

MIN_FREQ_MUSIC = 20
MAX_FREQ_MUSIC = 12000
MIN_FREQ_HUMAN = 0
MAX_FREQ_HUMAN = 1200

EPSILON = 1e-7  # Small value to prevent log(0)

# Frequency range used for maximum level tracking
LEVEL_TRACKING_MIN_FREQ = 4000
LEVEL_TRACKING_MAX_FREQ = MAX_FREQ_MUSIC

# Beat detection constants
SNARE_MIN_FREQ = 6000
SNARE_MAX_FREQ = 7000
KICK_MIN_FREQ = 80
KICK_MAX_FREQ = 200

MIN_SNARE_AVG_MAG = 0.23 # Average amplitude threshold for snare detection
MIN_KICK_AVG_MAG = 0.5
MIN_BEAT_INTERVAL = 1000 # ms

NUM_LEDS = 44
FPS = 30

# Weight function for magnitude adjustment (Use only with values in range [0,1])
# weight_func = lambda x: math.log((x + 1) * 1.1)
weight_func = lambda x: (math.log(x + 0.03) + 4) if x <= 0.2 else (math.log(0.23) + 4)

# Utils
def time_millis():
    return int(time.time() * 1000)
