from not_main.common import *
from not_main.converter import convert
from not_main.ledController import LEDController
import pyaudio
import numpy as np
from scipy.ndimage import gaussian_filter1d
from random import randint

def randomNormalizedRGBList(n: int) -> list:
    rgbList = []
    for _ in range(n):
        tempList = [randint(0, 255) for _ in range(3)]
        brightestIndex = randint(0, 2)
        tempList[brightestIndex] = 255
        rgbList.append(tuple(tempList))
    return rgbList

def run(trackMaximumLevel, min_freq, max_freq, n_freqs, distMode):
    ledController = LEDController()

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels = CHANNELS,
                    rate=RATE,
                    input = True,
                    frames_per_buffer=CHUNK)

    # Full frequency axis for FFT
    xf = np.fft.rfftfreq(n_freqs, 1.0 / RATE)
    # Boolean mask for specified frequency range
    freq_mask = (xf >= min_freq) & (xf <= max_freq)
    # Reduced frequency axis
    xf_reduced = xf[freq_mask]
    # Boolean mask for High-Pass level tracking AFTER frequency reduction
    tracking_mask = (xf_reduced >= LEVEL_TRACKING_MIN_FREQ) & (xf_reduced <= LEVEL_TRACKING_MAX_FREQ)
    # Boolean masks for snare/kick detection
    snare_mask = (xf_reduced >= SNARE_MIN_FREQ) & (xf_reduced <= SNARE_MAX_FREQ)
    kick_mask = (xf_reduced >= KICK_MIN_FREQ) & (xf_reduced <= KICK_MAX_FREQ)

    # True if a kick or snare is likely to be present in this window
    def beat_detect(freq_arr: np.ndarray) -> bool:
        return (np.average(freq_arr[snare_mask]) >= MIN_SNARE_AVG_MAG) or (np.average(freq_arr[kick_mask]) >= MIN_KICK_AVG_MAG)

    # Initialize normalized rgb
    #normalized_rgbs = randomNormalizedRGBList(NUM_LEDS)
    normalized_rgbs = [(255, 0, 0) for _ in range(NUM_LEDS)]

    print("Running with" + ("" if trackMaximumLevel else "out") + " maximum level tracking...")

    try:
        maxMag = 0 # Maximum level used for normalization
        lastSentTime = time_millis()
        lastBeatTime = lastSentTime

        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            if (time_millis() - lastSentTime) < (1000 / FPS):
                continue # Skip this audio chunk to adhere to given FPS

            # Convert audio data to numpy array and remove DC offset
            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples - np.mean(samples)

            # Apply Hann window for smoother spectrum
            window = np.hanning(len(samples))
            samples_windowed = samples * window
            
            fft_data = np.fft.rfft(samples_windowed, n_freqs) # Compute FFT
            fft_magnitude = np.abs(fft_data) # Take magnitude

            # Apply weight function
            for i in range(fft_magnitude.size):
                fft_magnitude[i] *= weight_func(i / fft_magnitude.size) # Ensure arguments reach from 0 to 1

            ############################# Peak Enhancement #############################
            fft_magnitude = fft_magnitude ** 2 # Square to exaggerate peaks
            fft_magnitude = gaussian_filter1d(fft_magnitude, sigma = 1.5) # Smooth the curves
            background = moving_average(fft_magnitude, w = 30) # Estimate overall curve
            fft_magnitude = fft_magnitude - background # Subtract overall curve to enhance peaks
            fft_magnitude -= np.min(fft_magnitude) # Shift to zero
            ############################################################################

            fft_magnitude_reduced = fft_magnitude[freq_mask] # Reduce frequency range
            
            # Normalize FFT magnitude
            if trackMaximumLevel:
                maxMag = max(np.max(fft_magnitude_reduced[tracking_mask]), maxMag)
            else:
                maxMag = np.max(fft_magnitude_reduced)
            fft_mag_norm_reduced = (NORM_TARGET * (fft_magnitude_reduced / maxMag)) if maxMag > 0 else fft_magnitude_reduced
            
            # Apply clipping in case of magnitudes > 1
            if trackMaximumLevel:
                # Magnitudes outside of tracking range may be higher than normalization magnitude, so clip them
                fft_mag_norm_reduced = np.clip(fft_mag_norm_reduced, 0, 1)

            if distMode == DIST_MODES.MUSIC and beat_detect(fft_mag_norm_reduced) and ((time_millis() - lastBeatTime) >= MIN_BEAT_INTERVAL):
                lastBeatTime = time_millis()
                # normalized_rgbs = randomNormalizedRGBList(NUM_LEDS)

            hex_arr = convert(fft_mag_norm_reduced, NUM_LEDS, distMode, normalized_rgbs)
            ledController.send_all(hex_arr)
            lastSentTime = time_millis()

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        ledController.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
