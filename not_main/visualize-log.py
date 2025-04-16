from common import *

import pyaudio
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Force a GUI backend; adjust if necessary
import matplotlib.pyplot as plt

def run(useSystemAudio = True):
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels = (2 if useSystemAudio else CHANNELS),
                    rate=RATE,
                    input=True,
                    input_device_index = (1 if useSystemAudio else None),
                    frames_per_buffer=CHUNK)

    # Compute full frequency axis for FFT
    xf = np.fft.rfftfreq(CHUNK, 1.0 / RATE)
    # Boolean mask for specified frequency range
    freq_mask = (xf >= MIN_FREQ_MUSIC) & (xf <= MAX_FREQ_MUSIC)
    # Reduce frequency axis
    xf_reduced = xf[freq_mask]

    # Set up Matplotlib figure and axis
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(xf_reduced, np.zeros_like(xf_reduced))
    # ax.set_xscale("log")           # Set the frequency axis to logarithmic scale
    ax.set_xlim(MIN_FREQ_MUSIC, MAX_FREQ_MUSIC)
    ax.set_ylim(-100, 0)           # Decibel scale; adjust as needed
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title('Real-Time Frequency Spectrum (Log Scaled)')

    print("Running... Speak or play sounds into your mic")

    try:
        while True:
            # Read a chunk of audio data from the stream
            data = stream.read(CHUNK, exception_on_overflow=False)
            # Convert to numpy array and remove DC offset
            samples = np.frombuffer(data, dtype=np.int16)
            samples = samples - np.mean(samples)

            # Apply a Hann window to reduce spectral leakage
            window = np.hanning(len(samples))
            samples_windowed = samples * window

            # Compute FFT and magnitude
            fft_data = np.fft.rfft(samples_windowed)
            fft_magnitude = np.abs(fft_data)

            # Optionally zero out the DC component
            fft_magnitude[0] = 0

            # Convert magnitude to decibel scale
            # Note: 20*log10(x) is standard for amplitude (not power)
            fft_db = 20 * np.log10(fft_magnitude + EPSILON)

            # Use the mask to select frequencies within the desired range
            fft_db_short = fft_db[freq_mask]
            # Normalize to 0 db
            fft_db_short -= np.max(fft_db_short)

            # Update the plot
            line.set_ydata(fft_db_short)
            fig.canvas.draw()
            fig.canvas.flush_events()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

run(False)
