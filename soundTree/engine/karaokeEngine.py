from soundTree.common import *
from soundTree.engine.abstractEngine import FFTEngine
from soundTree.audioProcessing import getSamplesFromData, computeWindowedSamples, computeEnhancedFFT, freq_to_midi
from soundTree.converter import convert
from soundTree.ledController import LEDController
from soundTree.sender.sender import LEDSender
from soundTree.pitchDetection.yinPitch import pitchDetect

import numpy as np
from clapDetector import ClapDetector

PITCH_DETECT_MIN_FREQ = 100
PITCH_DETECT_MAX_FREQ = 700
CLAP_LOWCUT = 1600
CLAP_HIGHCUT = 5000
PITCH_DETECT_INTERVAL = 500 # ms
CLAP_DETECT_INTERVAL = 50 # ms

WAITING_TIME_AFTER_MELODY = 2000 # ms
WAITING_TIME_AFTER_CLAP = 4500 # ms

PLAYER_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]
MAX_ERROR_SEMITONES = 2.5  # e.g., if on average the error is more than x semitones, score is 0.

abs_distance = lambda a, b : abs(a - b)

def dtw_distance(seq1, seq2, distance_func):
    # Initialize the cost matrix with infinity
    n, m = len(seq1), len(seq2)
    D = np.full((n+1, m+1), np.inf)
    D[0, 0] = 0
    
    # Fill in the matrix using dynamic programming
    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = distance_func(seq1[i-1], seq2[j-1])
            D[i, j] = cost + min(D[i-1, j], D[i, j-1], D[i-1, j-1])
    
    # Optionally, compute the length of the optimal path
    # For simplicity, we can normalize by max(n, m)
    normalized_error = D[n, m] / max(n, m)
    return normalized_error

def calc_score(freqSeqOriginal, freqSeqImitated):
    original_midi = [freq_to_midi(f) for f in freqSeqOriginal]
    imitation_midi = [freq_to_midi(f) for f in freqSeqImitated]
    normalized_error = dtw_distance(original_midi, imitation_midi, abs_distance)

    score = max(0, 1 - (normalized_error / MAX_ERROR_SEMITONES))
    return score


class KaraokeEngine(FFTEngine):
    def __init__(self, n_freqs, min_freq, max_freq, senders: list[LEDSender]):
        super().__init__(n_freqs, min_freq, max_freq)
        self.clapDetector = ClapDetector()
        self.ledController = LEDController()
        for sender in senders:
            self.ledController.add_sender(sender)

    def run(self):
        print("Running Karaoke Game...")
        try:
            def recordPlayerNumber():
                n_players = 0
                lastClapCheck = 0
                startedClapping = False
                lastClapDetected = 0
                accumulatedClapSamples = []
                for i in range(len(PLAYER_COLORS)):
                    accumulatedClapSamples.clear()
                    hasClapped = False # If False after loop, the player did not clap -> Take current number of players
                    while True:
                        samples = getSamplesFromData(self.stream.read(CHUNK, exception_on_overflow=False))
                        accumulatedClapSamples.extend(samples)

                        n_claps = 0
                        if (time_millis() - lastClapCheck >= CLAP_DETECT_INTERVAL):
                            n_claps = len(self.clapDetector.run(audioData = accumulatedClapSamples, lowcut = CLAP_LOWCUT, highcut = CLAP_HIGHCUT))
                            accumulatedClapSamples.clear()
                            lastClapCheck = time_millis()
                        if n_claps > 0:
                            debug_print("Clap detected!")
                            startedClapping = True
                            hasClapped = True
                            break
                        if (time_millis() - lastClapDetected) >= WAITING_TIME_AFTER_CLAP and startedClapping and n_players >= 2:
                            hasClapped = False
                            break
                    if hasClapped:
                        self.ledController.show_blink(PLAYER_COLORS[i], 3)
                        lastClapDetected = time_millis()
                        n_players += 1
                    else:
                        break
                return n_players

            def recordPlayerMelody(player_index):
                lastPitchDetect = time_millis()
                melody_array = []
                collected_samples = []
                melody_started = False
                last_note_time = 0

                while True:
                    samples = self.processSamples()
                    collected_samples.extend(samples)

                    if (time_millis() - lastPitchDetect) >= PITCH_DETECT_INTERVAL:
                        pitch_array = pitchDetect(collected_samples, RATE, PITCH_DETECT_MIN_FREQ, PITCH_DETECT_MAX_FREQ)
                        pitch_array = [f for f in pitch_array if f is not None]
                        if len(pitch_array) > 0:
                            debug_print("Pitch detected!")
                            melody_started = True
                            last_note_time = time_millis()
                            melody_array.extend(pitch_array)
                        collected_samples.clear()
                        lastPitchDetect = time_millis()

                    if melody_started and (time_millis() - last_note_time) >= WAITING_TIME_AFTER_MELODY:
                        break

                    fft_mag_reduced = self.processFFT(samples)
                    maxMag = np.max(fft_mag_reduced)
                    fft_mag_norm_reduced = self.normalizeFFT(fft_mag_reduced, maxMag)

                    byte_arr = convert(fft_mag_norm_reduced, NUM_LEDS, DIST_MODES.HUMAN, [PLAYER_COLORS[player_index] for _ in range(NUM_LEDS)])
                    self.ledController.send_all(byte_arr)

                return melody_array

            # Indicate game start
            for color in PLAYER_COLORS:
                self.ledController.show_blink(color, 1, 0.35, 0.0)

            n_players = recordPlayerNumber()
            while True: # Main loop
                score_sums = [0 for _ in range(n_players)]

                for i_original in range(n_players): # One round where everyone is the original once
                    # Indicate original singer start
                    self.ledController.show_snake(PLAYER_COLORS[i_original])
                    # Record original melody
                    original_melody = recordPlayerMelody(i_original)

                    for i_imitator in [i for i in range(n_players) if i != i_original]: # Imitation round
                        # Indicate imitator start
                        self.ledController.show_snake(PLAYER_COLORS[i_imitator])
                        # Record imitator melody
                        imitator_melody = recordPlayerMelody(i_imitator)
                        score = calc_score(original_melody, imitator_melody)
                        score_sums[i_imitator] += score
                        self.ledController.show_height(score, PLAYER_COLORS[i_imitator])

                score_avgs = [(s / (n_players - 1)) for s in score_sums]
                self.ledController.show_values_increasing(list(zip(score_avgs, PLAYER_COLORS[:n_players])))

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        super().cleanup()
        self.ledController.close()
