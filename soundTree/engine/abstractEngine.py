from abc import ABC, abstractmethod
from soundTree.common import *
from soundTree.audioProcessing import computeWindowedSamples, computeEnhancedFFT

import pyaudio
import numpy as np

# Abstract Base Class for an audio processing pipeline
class Engine(ABC):
    def __init__(self):
        # Initialize PortAudio
        self.pyAudio = pyaudio.PyAudio()

        # Open audio stream
        self.stream = self.pyAudio.open(format=FORMAT,
                                        channels = CHANNELS,
                                        rate=RATE,
                                        input = True,
                                        frames_per_buffer = CHUNK)

    @abstractmethod
    def run(self):
        pass
    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pyAudio.terminate()

    def processSamples(self):
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        return computeWindowedSamples(data)

# Engine that performs FFT
class FFTEngine(Engine):
    def __init__(self, n_freqs, min_freq, max_freq):
        super().__init__()

        self.n_freqs = n_freqs
        self.min_freq = min_freq
        self.max_freq = max_freq
        # Full frequency axis for FFT
        xf = np.fft.rfftfreq(n_freqs, 1.0 / RATE)
        # Boolean mask for specified frequency range
        self.freq_mask = (xf >= min_freq) & (xf <= max_freq)
        # Reduced frequency axis
        self.freq_axis_reduced = xf[self.freq_mask]

    def processFFT(self, samples):
        return computeEnhancedFFT(samples, self.n_freqs, self.freq_mask)

    def normalizeFFT(self, fft_mag_reduced, maxMag):
        return ((fft_mag_reduced / maxMag)) if maxMag > 0 else fft_mag_reduced
