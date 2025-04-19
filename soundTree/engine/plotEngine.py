from soundTree.common import *
from soundTree.engine.abstractEngine import FFTEngine

import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib

matplotlib.use("TkAgg")  # Force a GUI backend; adjust if necessary
import matplotlib.pyplot as plt

class PlotEngine(FFTEngine):
    def __init__(self, n_freqs, min_freq, max_freq, trackMaximumLevel: bool):
        super().__init__(n_freqs, min_freq, max_freq)
        self.trackMaximumLevel = trackMaximumLevel

    def run(self):
        # Boolean mask for High-Pass level tracking AFTER frequency reduction
        tracking_mask = (self.freq_axis_reduced >= LEVEL_TRACKING_MIN_FREQ) & (self.freq_axis_reduced <= LEVEL_TRACKING_MAX_FREQ)

        # Set up Matplotlib plot
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot(self.freq_axis_reduced, np.zeros_like(self.freq_axis_reduced))
        ax.set_xlim(self.min_freq, self.max_freq)
        ax.set_ylim(0, 1)
        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Magnitude (dB)')
        ax.set_title('Real-Time Frequency Spectrum')

        print("Running Plotter with" + ("" if self.trackMaximumLevel else "out") + " maximum level tracking...")

        try:
            trackingMaxMag = 0 # Maximum level used for normalization
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

                # Update the plot
                line.set_ydata(fft_mag_norm_reduced)
                fig.canvas.draw()
                fig.canvas.flush_events()

        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        super().cleanup()
