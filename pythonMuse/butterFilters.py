from scipy.signal import butter, lfilter, iirnotch


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


def iir_notch(notch_freq, fs, Q=30):
    b, a = iirnotch(w0=notch_freq, Q=Q, fs=fs)
    return b, a


def applyButter(sample, highPass, lowPass, notchFilter):
    filtered = sample
    for channel in range(sample.shape[1]):  # For each EEG channel
        if lowPass is not None:  # Filter only if the filter is selected by the user
            filtered[:, channel] = lfilter(lowPass[0], lowPass[1], filtered[:, channel])
        if highPass is not None:  # Filter only if the filter is selected by the user
            filtered[:, channel] = lfilter(notchFilter[0], notchFilter[1], filtered[:, channel])
        if notchFilter is not None:  # Filter only if the filter is selected by the user
            filtered[:, channel] = lfilter(highPass[0], highPass[1], filtered[:, channel])
    return filtered
