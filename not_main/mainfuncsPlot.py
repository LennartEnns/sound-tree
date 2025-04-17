from not_main.common import *

import pyaudio
import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use("TkAgg")  # Force a GUI backend; adjust if necessary
import matplotlib.pyplot as plt

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
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title('Real-Time Frequency Spectrum')

    print("Running with" + ("" if trackMaximumLevel else "out") + " maximum level tracking...")

    try:
        maxMag = 0 # Maximum level used for normalization
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)

            # Convert audio data to numpy array and remove DC offset
            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples - np.mean(samples)
            
            # Apply Hann window for smoother spectrum
            window = np.hanning(len(samples))
            samples_windowed = samples * window
            
            fft_data = np.fft.rfft(samples_windowed, n_freqs) # Compute FFT
            fft_mag = np.abs(fft_data) # Take magnitude
            # Apply weight function
            for i in range(fft_mag.size):
                fft_mag[i] *= weight_func(i / fft_mag.size) # Ensure arguments reach from 0 to 1
            fft_mag_reduced = fft_mag[freq_mask] # Reduce frequency range

            ############################# Peak Enhancement #############################
            fft_mag_reduced = fft_mag_reduced ** 2 # Square to exaggerate peaks
            fft_mag_reduced = gaussian_filter1d(fft_mag_reduced, sigma = 1.5) # Smooth the curves
            # background = moving_average(fft_mag_reduced, w = 30) # Estimate overall curve
            # fft_mag_reduced = fft_mag_reduced - background # Subtract overall curve to enhance peaks
            # fft_mag_reduced -= np.min(fft_mag_reduced) # Shift to zero
            ############################################################################
            
            # Normalize FFT magnitude
            if trackMaximumLevel:
                maxMag = max(np.max(fft_mag_reduced[tracking_mask]), maxMag)
            else:
                maxMag = np.max(fft_mag_reduced)
            fft_mag_norm_reduced = (NORM_TARGET * (fft_mag_reduced / maxMag)) if maxMag > 0 else fft_mag_reduced
            
            # Apply clipping in case of magnitudes > 1
            if trackMaximumLevel:
                # Magnitudes outside of tracking range may be higher than normalization magnitude, so clip them
                fft_mag_norm_reduced = np.clip(fft_mag_norm_reduced, 0, 1)

            # Update the plot
            line.set_ydata(fft_mag_norm_reduced)
            fig.canvas.draw()
            fig.canvas.flush_events()

    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
