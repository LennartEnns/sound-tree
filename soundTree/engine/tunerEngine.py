from soundTree.common import *
from soundTree.converter import rgb_array_to_bytes
from soundTree.ledController import LEDController
from soundTree.sender.webSender import WebSender
from soundTree.sender.sender import LEDSender
from soundTree.engine.abstractEngine import Engine
from soundTree.pitchDetection.yinPitch import pitchDetect
from soundTree.audioProcessing import freq_to_midi

import numpy as np

TUNER_COOLDOWN = 2000 # ms
PITCH_DETECT_INTERVAL = 400 # ms
NOTE_COLORS = [
    (255, 23, 70), # C: Crimson
    None, # C#: Crimson + Cyan alternating
    (0, 255, 255), # D: Cyan
    None, # D#
    (255, 0, 255), # E: Purple
    (255, 150, 150), # F: Flamingo (Pink)
    None, # F#
    (0, 255, 0), # G: Green
    None, # G#
    (255, 191, 0), # A: Amber
    None, # A#
    (0, 0, 255) # B: Blue
]
BIAS_COLOR_NEGATIVE = (255, 0, 0) # Red
BIAS_COLOR_POSITIVE = (255, 255, 255) # White

class TunerEngine(Engine):
    def __init__(self, min_freq_detected, max_freq_detected, senders: list[LEDSender]):
        super().__init__()
        self.pd_min_freq = min_freq_detected
        self.pd_max_freq = max_freq_detected
        self.ledController = LEDController()
        for sender in senders:
            self.ledController.add_sender(sender)

    def run(self):
        print("Running Tuner...")

        try:
            lastPitchCheck = 0
            lastDetectedPitch = 0
            collected_samples = []
            while True:
                samples = self.processSamples()
                collected_samples.extend(samples)

                if (time_millis() - lastPitchCheck) >= PITCH_DETECT_INTERVAL:
                        pitch_array = pitchDetect(collected_samples, RATE, self.pd_min_freq, self.pd_max_freq)
                        pitch_array = [f for f in pitch_array if f is not None]
                        if len(pitch_array) > 0:
                            avgMidi = (freq_to_midi(np.average(pitch_array))) % 12
                            targetMidi = round(avgMidi) % 12 # Estimated target note
                            biasMidi = avgMidi - targetMidi # value from -0.5 to 0.5
                            rgbs = self.getTunerResultRGBs(targetMidi, biasMidi)
                            self.ledController.send_all(rgb_array_to_bytes(rgbs))
                            lastDetectedPitch = time_millis()
                        elif (time_millis() - lastDetectedPitch) >= TUNER_COOLDOWN:
                            self.ledController.off()
                        collected_samples.clear()
                        lastPitchCheck = time_millis()

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.cleanup()

    def getTunerResultRGBs(self, targetMidi, biasMidi):
        # Step 1: Fill with the RGB pattern that represents the target note
        rgbs = []
        targetRGB = NOTE_COLORS[targetMidi]
        if targetRGB is not None:
            rgbs = [targetRGB for _ in range(NUM_LEDS)]
        else:
            leftRGB = NOTE_COLORS[targetMidi - 1]
            rightRGB = NOTE_COLORS[targetMidi + 1]
            alt = True
            for _ in range(NUM_LEDS):
                rgbs.append(leftRGB if (alt := not alt) else rightRGB)
        if abs(biasMidi) < (12 / NUM_LEDS):
            return rgbs

        # Step 2: Fill in the bias
        endpoint1 = ((NUM_LEDS - 1) // 2) if (biasMidi < 0) else (NUM_LEDS // 2) # Basically the center
        endpoint2 = round((NUM_LEDS / 2) + (biasMidi * NUM_LEDS))
        iFrom = min(endpoint1, endpoint2, NUM_LEDS - 1)
        iTo = max(endpoint1, endpoint2, 0)
        bcol = BIAS_COLOR_NEGATIVE if biasMidi < 0 else BIAS_COLOR_POSITIVE
        rgbs[iFrom : iTo] = [bcol for _ in range(iTo - iFrom)]
        return rgbs

    def cleanup(self):
        super().cleanup()
        self.ledController.close()
