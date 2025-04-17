from not_main.common import *
from not_main.converter import convert
from not_main.ledController import LEDController
from not_main.sender.webSender import WebSender
from not_main.sender.sender import LEDSender
import pyaudio
import numpy as np
from scipy.ndimage import gaussian_filter1d
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

def run(trackMaximumLevel, min_freq, max_freq, n_freqs, distMode, beatDetect: bool, senders: list[LEDSender]):
    ledController = LEDController()
    for sender in senders:
        ledController.add_sender(sender)

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

    # Initialize normalized rgbs
    normalized_rgbs = randomNormalizedRGBsSingle(NUM_LEDS)

    print("Running with" + ("" if trackMaximumLevel else "out") + " maximum level tracking...")

    # hannAvg, fftAvg, weightAvg, enhAvg, normAvg, beatAvg, csAvg = 0, 0, 0, 0, 0, 0, 0
    # fps_ctr = 0

    try:
        maxMag = 0 # Maximum level used for normalization
        lastBeatTime = time_millis()

        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            # Convert audio data to numpy array and remove DC offset
            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples - np.mean(samples)

            # hann_start = time_millis()
            # Apply Hann window for smoother spectrum
            window = np.hanning(len(samples))
            samples_windowed = samples * window
            # hann_time = time_millis() - hann_start
            # hannAvg = ((hannAvg * fps_ctr) + hann_time) / (fps_ctr + 1)

            # fft_start = time_millis()
            fft_data = np.fft.rfft(samples_windowed, n_freqs) # Compute FFT
            fft_mag = np.abs(fft_data) # Take magnitude
            # fft_time = time_millis() - fft_start
            # fftAvg = ((fftAvg * fps_ctr) + fft_time) / (fps_ctr + 1)

            # weight_start = time_millis()
            # Apply weight function
            for i in range(fft_mag.size):
                fft_mag[i] *= weight_func(i / fft_mag.size) # Ensure arguments reach from 0 to 1
            # weight_time = time_millis() - weight_start
            # weightAvg = ((weightAvg * fps_ctr) + weight_time) / (fps_ctr + 1)

            fft_mag_reduced = fft_mag[freq_mask] # Reduce frequency range

            # enhancement_start = time_millis()
            ############################# Peak Enhancement #############################
            fft_mag_reduced = fft_mag_reduced ** 2 # Square to exaggerate peaks
            fft_mag_reduced = gaussian_filter1d(fft_mag_reduced, sigma = 1.5) # Smooth the curves
            # background = moving_average(fft_mag_reduced, w = 30) # Estimate overall curve
            # fft_mag_reduced = fft_mag_reduced - background # Subtract overall curve to enhance peaks
            # fft_mag_reduced -= np.min(fft_mag_reduced) # Shift to zero
            ############################################################################
            # enhancement_time = time_millis() - enhancement_start
            # enhAvg = ((enhAvg * fps_ctr) + enhancement_time) / (fps_ctr + 1)

            # Normalize FFT magnitude
            # norm_start = time_millis()
            if trackMaximumLevel:
                maxMag = max(np.max(fft_mag_reduced[tracking_mask]), maxMag)
            else:
                maxMag = np.max(fft_mag_reduced)
            fft_mag_norm_reduced = (NORM_TARGET * (fft_mag_reduced / maxMag)) if maxMag > 0 else fft_mag_reduced
            # norm_time = time_millis() - norm_start
            # normAvg = ((normAvg * fps_ctr) + norm_time) / (fps_ctr + 1)

            # Apply clipping in case of magnitudes > 1
            if trackMaximumLevel:
                # Magnitudes outside of tracking range may be higher than normalization magnitude, so clip them
                fft_mag_norm_reduced = np.clip(fft_mag_norm_reduced, 0, 1)

            if beatDetect:
                # bt_start = time_millis()
                if ((time_millis() - lastBeatTime) >= MIN_BEAT_INTERVAL) and beat_detect(fft_mag_norm_reduced):
                    lastBeatTime = time_millis()
                    normalized_rgbs = randomNormalizedRGBsSingle(NUM_LEDS)
                # bt_time = time_millis() - bt_start
                # beatAvg = ((beatAvg * fps_ctr) + bt_time) / (fps_ctr + 1)

            # cs_start = time_millis()
            byte_arr = convert(fft_mag_norm_reduced, NUM_LEDS, distMode, normalized_rgbs)
            ledController.send_all(byte_arr)
            # cs_time = time_millis() - cs_start
            # csAvg = ((csAvg * fps_ctr) + cs_time) / (fps_ctr + 1)

            # fps_ctr += 1

    except KeyboardInterrupt:
        # print("Stopping...")
        # print(f"Hann average: {hannAvg}")
        # print(f"FFT average: {fftAvg}")
        # print(f"Weight average: {weightAvg}")
        # print(f"Enhancement average: {enhAvg}")
        # print(f"Normalization average: {normAvg}")
        # print(f"Beat Detection average: {beatAvg}")
        # print(f"Convert + send average: {csAvg}")
        # print(f"Average Sum: {hannAvg + fftAvg + weightAvg + enhAvg + normAvg + beatAvg + csAvg}")
        pass
    finally:
        ledController.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
