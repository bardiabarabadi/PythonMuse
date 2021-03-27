# In this file  we try to mimic the functionality of the MatlabMuse.m

from EasyMuse.Muse import Muse
from EasyMuse.helper import *
import matplotlib;

# matplotlib.use("TkAgg")

from EasyMuse.biQuadFilters import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from scipy.signal import butter, lfilter, freqz


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


plotLength = 512  # denominated in samples
samplingBufferLen = 16  # number of samples to be held between two plot updates
plotUpdateInterval = 32  # in milliseconds

sampleRate = 256
bandwidth = 0.707
whichFilters = [0, 0, 0]

# Create empty arrays

previousSamples = np.zeros([4, 2, 3])
previousResults = np.zeros([4, 2, 3])

highFreq = 100
highPass = biQuadHighPass(highFreq, sampleRate, bandwidth)

lowFreq = 0.1
lowPass = biQuadLowPass(lowFreq, sampleRate, bandwidth)

notchFreq = 60
notchFilter = biQuadNotch(notchFreq, sampleRate, bandwidth)

plotBuffer = np.zeros([plotLength, 4])
plotX = np.zeros([plotLength, 1])

for i in range(1, 100):
    eegData = np.random.rand(16, 6) * 500
    print(plotX.shape)

    eegData[:, 5] = np.linspace(start=np.squeeze(plotX)[511], stop=np.squeeze(plotX)[511] + 15, num=16)
    print(plotX.shape)
    if eegData.__len__() > samplingBufferLen:
        print("Warning: Missing samples. Increase the sampling buffer length or increase the plot update frequency")
    eegData = np.array(eegData)
    eegTimeStamp = eegData[:, 5]
    eegData = eegData[:, 0:4]

    # Filtering
    eegData_t, previousSamples, previousResults = applyBiQuad(eegData.T, whichFilters, highPass, lowPass, notchFilter,
                                                              previousSamples, previousResults)

    eegData = eegData_t.T
    plotX = np.append(plotX, eegTimeStamp)
    plotBuffer = np.append(plotBuffer, eegData, axis=0)

    plotX = plotX[-plotLength:]
    plotBuffer = plotBuffer[-plotLength:, :]

raw = plotBuffer[:, 1]
fft_raw = np.abs(np.fft.fft(plotBuffer[:, 1]))

fft_raw[0] = 0

y = butter_lowpass_filter(plotBuffer[:,1], 30,fs=sampleRate)
z = butter_highpass_filter(y, 0.1,fs=sampleRate)
fft_y = np.abs(np.fft.fft(y))
fft_y[0] = 0

fig, axs = plt.subplots(3)
axs[0].plot(plotX, raw)
axs[1].plot(plotX, y)
axs[2].plot(plotX, z)
plt.show()

