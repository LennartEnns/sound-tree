from soundTree.common import weight_func
import numpy as np
from scipy.ndimage import gaussian_filter1d

def getSamplesFromData(audioData):
    # Convert audio data to numpy array and remove DC offset
    samples = np.frombuffer(audioData, dtype=np.int16)
    samples = samples - np.mean(samples)
    return samples

def computeWindowedSamples(audioData):
    samples = getSamplesFromData(audioData)

    # Apply Hann window for smoother spectrum
    window = np.hanning(len(samples))
    samples_windowed = samples * window
    return samples_windowed

def computeEnhancedFFT(samples, n_freqs, freq_mask = None, enhance_peaks = True):
    fft_data = np.fft.rfft(samples, n_freqs) # Compute FFT
    fft_mag = np.abs(fft_data) # Take magnitude

    # Apply weight function
    for i in range(fft_mag.size):
        fft_mag[i] *= weight_func(i / fft_mag.size) # Ensure arguments reach from 0 to 1

    fft_mag_reduced = fft_mag[freq_mask] if freq_mask is not None else fft_mag # Reduce frequency range

    ############################# Peak Enhancement #############################
    fft_mag_reduced = gaussian_filter1d(fft_mag_reduced, sigma = 1.5) # Smooth the curves
    if enhance_peaks:
        background = moving_average(fft_mag_reduced, w = 30) # Estimate overall curve
        fft_mag_reduced = fft_mag_reduced - background # Subtract overall curve to enhance peaks
        fft_mag_reduced = np.clip(fft_mag_reduced, 0, np.inf) # Clip to zero
    ############################################################################

    return fft_mag_reduced

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'same') / w

def freq_to_midi(frequency):
    return 69 + 12 * np.log2(frequency / 440.0)
