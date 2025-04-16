from not_main.common import *
from not_main.converter import convert
from not_main.ledController import LEDController
from not_main.yin.yinPitch import pitchDetect
import pyaudio
import numpy as np
from scipy.ndimage import gaussian_filter1d
from clapDetector import ClapDetector

N_FREQS = 2048 # Number of frequency points
PITCH_DETECT_INTERVAL = 500 # ms
CLAP_DETECT_INTERVAL = 50 # ms
WAITING_TIME_AFTER_MELODY = 2000 # ms
WAITING_TIME_AFTER_CLAP = 5000 # ms
PLAYER_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255)]

def freq_to_midi(frequency):
    return 69 + 12 * np.log2(frequency / 440.0)

abs_distance = lambda a, b: abs(a - b)

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

    # Define a threshold value (error_max) or sensitivity (alpha)
    error_max = 2.0  # e.g., if on average the error is more than x semitones, score is 0.
    score = max(0, 1 - (normalized_error / error_max))
    return score

def run():
    clapDetector = ClapDetector(logLevel = 0)

    ledController = LEDController()
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels = CHANNELS,
                    rate=RATE,
                    input = True,
                    frames_per_buffer=CHUNK)

    # Full frequency axis for FFT
    xf = np.fft.rfftfreq(N_FREQS, 1.0 / RATE)
    # Boolean mask for specified frequency range
    freq_mask = (xf >= MIN_FREQ_HUMAN) & (xf <= MAX_FREQ_HUMAN)
    # Reduced frequency axis
    # xf_reduced = xf[freq_mask]

    # Initialize rgb
    # normalized_rgbs = [(0, 0, 255) for _ in range(NUM_LEDS)]

    print("Running karaoke game...")

    try:
        def recordPlayerNumber():
            n_players = 0
            lastClapDetect = 0
            startedClapping = False
            lastClapTime = 0
            accumulatedClapSamples = []
            for i in range(len(PLAYER_COLORS)):
                accumulatedClapSamples.clear()
                hasClapped = False # If False after loop, the player did not clap -> Take current number of players
                while True:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    # Convert audio data to numpy array and remove DC offset
                    samples = np.frombuffer(data, dtype=np.int16)
                    samples = samples - np.mean(samples)
                    accumulatedClapSamples.extend(samples)

                    n_claps = 0
                    if (time_millis() - lastClapDetect >= 50):
                        n_claps = len(clapDetector.run(audioData = accumulatedClapSamples, thresholdBias = 6000, lowcut = 1600, highcut = 5000))
                        accumulatedClapSamples.clear()
                        lastClapDetect = time_millis()
                    if n_claps > 0:
                        print("Clap detected!")
                        startedClapping = True
                        hasClapped = True
                        break
                    if (time_millis() - lastClapTime) >= WAITING_TIME_AFTER_CLAP and startedClapping and n_players >= 2:
                        hasClapped = False
                        break
                if hasClapped:
                    ledController.blink(PLAYER_COLORS[i], 3, 0.2, 0.3)
                    lastClapTime = time_millis()
                    n_players += 1
                else:
                    break
            return n_players

        def recordPlayerMelody(player_index):
            lastSentTime = time_millis()
            lastPitchDetect = time_millis()
            melody_array = []
            collected_samples = []
            melody_started = False
            last_note_time = 0

            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)

                # Convert audio data to numpy array and remove DC offset
                samples = np.frombuffer(data, dtype=np.int16)
                samples = samples - np.mean(samples)
                collected_samples.extend(samples)

                if (time_millis() - lastPitchDetect) >= PITCH_DETECT_INTERVAL:
                    pitch_array = pitchDetect(collected_samples, RATE, 100, 1000)
                    pitch_array = [f for f in pitch_array if f is not None]
                    if len(pitch_array) > 0:
                        print("Pitch detected!")
                        melody_started = True
                        last_note_time = time_millis()
                        melody_array.extend(pitch_array)
                    collected_samples.clear()
                    lastPitchDetect = time_millis()

                if melody_started and (time_millis() - last_note_time) >= WAITING_TIME_AFTER_MELODY:
                    break

                if (time_millis() - lastSentTime) < (1000 / FPS):
                    continue # Skip this audio chunk to adhere to given FPS
                
                # Apply Hann window for smoother spectrum
                window = np.hanning(len(samples))
                samples_windowed = samples * window
                
                fft_data = np.fft.rfft(samples_windowed, N_FREQS) # Compute FFT
                fft_magnitude = np.abs(fft_data) # Take magnitude
                # Apply weight function
                for i in range(fft_magnitude.size):
                    fft_magnitude[i] *= weight_func(i / fft_magnitude.size) # Ensure arguments reach from 0 to 1

                ############################# Peak Enhancement #############################
                fft_magnitude = fft_magnitude ** 2 # Square to enhance peaks
                fft_magnitude = gaussian_filter1d(fft_magnitude, sigma = 1.5) # Smooth the curves
                background = moving_average(fft_magnitude, w = 30) # Estimate overall curve
                fft_magnitude = fft_magnitude - background # Subtract overall curve to enhance peaks
                ############################################################################

                fft_magnitude_reduced = fft_magnitude[freq_mask] # Reduce frequency range
                
                # Normalize FFT magnitude
                maxMag = np.max(fft_magnitude_reduced)
                fft_mag_norm_reduced = (NORM_TARGET * (fft_magnitude_reduced / maxMag)) if maxMag > 0 else fft_magnitude_reduced

                hex_arr = convert(fft_mag_norm_reduced, NUM_LEDS, DIST_MODES.HUMAN, [PLAYER_COLORS[player_index] for _ in range(NUM_LEDS)])
                ledController.send_all(hex_arr)
                lastSentTime = time_millis()
            return melody_array


        # Indicate game start
        for color in PLAYER_COLORS:
            ledController.blink(color, 1)

        n_players = recordPlayerNumber()
        score_sums = [0 for _ in range(n_players)]
        while True: # Main loop
            for i_original in range(n_players): # One round where everyone is the original once
                # Indicate original singer start
                ledController.show_snake(PLAYER_COLORS[i_original])
                # Record original melody
                original_melody = recordPlayerMelody(i_original)

                for i_imitator in [i for i in range(n_players) if i != i_original]: # Imitation round
                    # Indicate imitator start
                    ledController.show_snake(PLAYER_COLORS[i_imitator])
                    # Record imitator melody
                    imitator_melody = recordPlayerMelody(i_imitator)
                    score = calc_score(original_melody, imitator_melody)
                    score_sums[i_imitator] += score
                    ledController.show_height(score, PLAYER_COLORS[i_imitator])
            score_avgs = [(s / (n_players - 1)) for s in score_sums]
            ledController.show_values_increasing(zip(score_avgs, PLAYER_COLORS[:n_players]))

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        ledController.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
