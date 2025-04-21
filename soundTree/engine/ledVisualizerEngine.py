from soundTree.common import *
from soundTree.converter import convert
from soundTree.ledController import LEDController
from soundTree.sender.webSender import WebSender
from soundTree.sender.sender import LEDSender
from soundTree.engine.abstractEngine import FFTEngine
import numpy as np
from random import randint, choice

TREE_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]

def randomNormalizedRGBList(n: int) -> list:
    rgbList = []
    for _ in range(n):
        tempList = [randint(0, 255) for _ in range(3)]
        brightestIndex = randint(0, 2)
        tempList[brightestIndex] = 255
        rgbList.append(tuple(tempList))
    return rgbList

def randomNormalizedRGBsSingle(n: int) -> tuple:
    rgb = choice(TREE_COLORS)
    return [rgb for _ in range(n)]

class LEDVisualizerEngine(FFTEngine):
    def __init__(self, n_freqs, min_freq, max_freq, enhance_peaks, distMode, beatDetect: bool, trackMaximumLevel: bool, senders: list[LEDSender]):
        super().__init__(n_freqs, min_freq, max_freq, enhance_peaks)
        self.distMode = distMode
        self.beatDetect = beatDetect
        self.trackMaximumLevel = trackMaximumLevel

        self.ledController = LEDController()
        for sender in senders:
            self.ledController.add_sender(sender)

    def run(self):
        # Boolean mask for High-Pass level tracking AFTER frequency reduction
        tracking_mask = (self.freq_axis_reduced >= LEVEL_TRACKING_MIN_FREQ) & (self.freq_axis_reduced <= LEVEL_TRACKING_MAX_FREQ)
        # Boolean masks for snare/kick detection
        snare_mask = (self.freq_axis_reduced >= SNARE_MIN_FREQ) & (self.freq_axis_reduced <= SNARE_MAX_FREQ)
        kick_mask = (self.freq_axis_reduced >= KICK_MIN_FREQ) & (self.freq_axis_reduced <= KICK_MAX_FREQ)

        # True if a kick or snare is likely to be present in this window
        def beat_detect(freq_arr: np.ndarray) -> bool:
            return (np.average(freq_arr[snare_mask]) >= MIN_SNARE_AVG_MAG) or (np.average(freq_arr[kick_mask]) >= MIN_KICK_AVG_MAG)

        # Initialize normalized rgbs
        normalized_rgbs = randomNormalizedRGBsSingle(NUM_LEDS)

        print("Running Visualizer with" + ("" if self.trackMaximumLevel else "out") + " maximum level tracking...")

        try:
            trackingMaxMag = 0 # Maximum level used for normalization
            lastBeatTime = time_millis()

            while True:
                samples = self.processSamples()
                fft_mag_reduced = self.processFFT(samples)

                # Normalize FFT magnitude
                if self.trackMaximumLevel:
                    trackingMaxMag = max(np.max(fft_mag_reduced[tracking_mask]), trackingMaxMag)
                    maxMag = max(trackingMaxMag, np.max(fft_mag_reduced)) # In case some magnitudes outside of tracking range are higher than maxMag
                else:
                    maxMag = np.max(fft_mag_reduced)
                fft_mag_norm_reduced = self.normalizeFFT(fft_mag_reduced, maxMag)

                if self.beatDetect:
                    if ((time_millis() - lastBeatTime) >= MIN_BEAT_INTERVAL) and beat_detect(fft_mag_norm_reduced):
                        lastBeatTime = time_millis()
                        normalized_rgbs = randomNormalizedRGBsSingle(NUM_LEDS)

                byte_arr = convert(fft_mag_norm_reduced, NUM_LEDS, self.distMode, normalized_rgbs)
                self.ledController.send_all(byte_arr)

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.cleanup()

    def cleanup(self):
        super().cleanup()
        self.ledController.close()
