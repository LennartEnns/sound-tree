from not_main.common import *

import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Force a GUI backend; adjust if necessary
import matplotlib.pyplot as plt
from not_main.yin.yinPitch import pitchDetect

def run(trackMaximumLevel, min_freq, max_freq, n_freqs):
    # Initialize PyAudio
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels = CHANNELS,
                    rate=RATE,
                    input = True,
                    frames_per_buffer = CHUNK)

    # Full frequency axis for FFT
    xf = np.fft.rfftfreq(n_freqs, 1.0 / RATE)
    # Boolean mask for specified frequency range
    freq_mask = (xf >= min_freq) & (xf <= max_freq)
    # Reduced frequency axis
    xf_reduced = xf[freq_mask]
    # Boolean mask for High-Pass level tracking AFTER frequency reduction
    tracking_mask = (xf_reduced >= LEVEL_TRACKING_MIN_FREQ) & (xf_reduced <= LEVEL_TRACKING_MAX_FREQ)

    # Set up Matplotlib plot
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(xf_reduced, np.zeros_like(xf_reduced))
    ax.set_xlim(min_freq, max_freq)
    ax.set_ylim(0, NORM_TARGET)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_title('Real-Time Frequency Spectrum')

    print("Running with" + ("" if trackMaximumLevel else "out") + " maximum level tracking...")

    try:
        maxMag = 0 # Maximum level used for normalization
        lastPitchDetect = time_millis()
        collected_samples = []
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            # Convert audio data to numpy array and remove DC offset
            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples - np.mean(samples)
            collected_samples.extend(samples)
            
            # Apply Hann window for smoother spectrum
            window = np.hanning(len(samples))
            samples_windowed = samples * window
            
            fft_data = np.fft.rfft(samples_windowed, n_freqs) # Compute FFT
            fft_magnitude = np.abs(fft_data) # Take magnitude
            # Apply weight function
            for i in range(fft_magnitude.size):
                fft_magnitude[i] *= weight_func(i / fft_magnitude.size) # Ensure arguments reach from 0 to 1

            fft_magnitude_reduced = fft_magnitude[freq_mask] # Reduce frequency range
            
            # Normalize FFT magnitude
            maxMag = max(np.max(fft_magnitude_reduced[tracking_mask]), maxMag) if trackMaximumLevel else np.max(fft_magnitude_reduced)
            fft_mag_norm_reduced = (NORM_TARGET * (fft_magnitude_reduced / maxMag)) if maxMag > 0 else fft_magnitude_reduced

            # Update the plot
            line.set_ydata(fft_mag_norm_reduced)
            fig.canvas.draw()
            fig.canvas.flush_events()

            if (time_millis() - lastPitchDetect >= 500):
                pitch_array = pitchDetect(collected_samples, RATE, 100, 800)
                print(pitch_array)
                collected_samples.clear()
                lastPitchDetect = time_millis()

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
