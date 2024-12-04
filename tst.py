import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, notch_filter, ifft

# Example: Correcting an Arrhythmic ECG Signal

# Load your arrhythmic ECG signal (use your actual data here)
fs = 500  # Sampling frequency in Hz
t = np.linspace(0, 10, fs * 10)  # 10-second signal
ecg_signal = np.sin(2 * np.pi * 1 * t) + 0.2 * np.sin(2 * np.pi * 10 * t)  # Example arrhythmic signal

# Band-pass filter to focus on normal ECG range (0.5–50 Hz)
def bandpass_filter(signal, lowcut, highcut, fs, order=2):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

filtered_signal = bandpass_filter(ecg_signal, lowcut=0.5, highcut=50, fs=fs)

# Apply notch filter to remove arrhythmic components (e.g., 10 Hz)
def apply_notch_filter(signal, freq, fs, quality=30):
    nyquist = 0.5 * fs
    notch_freq = freq / nyquist
    b, a = notch_filter(notch_freq, Q=quality, fs=fs)
    return filtfilt(b, a, signal)

notch_corrected_signal = apply_notch_filter(filtered_signal, freq=10, fs=fs)

# Plot the original and corrected signals
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
plt.plot(t, ecg_signal, label="Arrhythmic ECG Signal")
plt.legend()
plt.subplot(2, 1, 2)
plt.plot(t, notch_corrected_signal, label="Corrected ECG Signal")
plt.legend()
plt.xlabel("Time (s)")
plt.tight_layout()
plt.show()
