# In this file  we try to mimic the functionality of the MatlabMuse.m

from EasyMuse.Muse import Muse
from EasyMuse.helper import *
import matplotlib;

matplotlib.use("TkAgg")

from EasyMuse.butterFilters import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def animateEEG(i):
    global plotX
    global plotBuffer
    global eegData

    plotX, plotBuffer, eegData = updateBuffer(plotX, plotBuffer, eegData, muse, whichFilters, highPass, lowPass,
                                              notchFilter)

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax1.plot(plotX, plotBuffer[:, 0])
    ax2.plot(plotX, plotBuffer[:, 1])
    ax3.plot(plotX, plotBuffer[:, 2])
    ax4.plot(plotX, plotBuffer[:, 3])

    ax1.set_ylim(-1000, 1000)
    ax2.set_ylim(-1000, 1000)
    ax3.set_ylim(-1000, 1000)
    ax4.set_ylim(-1000, 1000)


def animateFFT(i):
    global plotX
    global plotBuffer
    global eegData

    plotX, plotBuffer, eegData = updateBuffer(plotX, plotBuffer, eegData, muse, whichFilters, highPass, lowPass,
                                              notchFilter)
    fftCoefficients = doMuseFFT(toFFT=plotBuffer, sRate=sampleRate)
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    ax1.bar(np.arange(1, fftCoefficients.shape[0] + 1, 1), fftCoefficients[:, 0])
    ax2.bar(np.arange(1, fftCoefficients.shape[0] + 1, 1), fftCoefficients[:, 1])
    ax3.bar(np.arange(1, fftCoefficients.shape[0] + 1, 1), fftCoefficients[:, 2])
    ax4.bar(np.arange(1, fftCoefficients.shape[0] + 1, 1), fftCoefficients[:, 3])

    ax1.set_ylim(0, 10)
    ax2.set_ylim(0, 10)
    ax3.set_ylim(0, 10)
    ax4.set_ylim(0, 10)


def animateWavelet(i):
    global plotX
    global plotBuffer
    global eegData

    plotX, plotBuffer, eegData = updateBuffer(plotX, plotBuffer, eegData, muse, whichFilters, highPass, lowPass,
                                              notchFilter)
    wavelet = doMuseWavelet(toWavelet=plotBuffer, sRate=sampleRate)
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    ax1.imshow(wavelet[0, :, :], aspect=plotLength / 60, origin='lower')
    ax2.imshow(wavelet[1, :, :], aspect=plotLength / 60, origin='lower')
    ax3.imshow(wavelet[2, :, :], aspect=plotLength / 60, origin='lower')
    ax4.imshow(wavelet[3, :, :], aspect=plotLength / 60, origin='lower')


def close_handle(evt):
    print("disconnecting Muse")
    muse.disconnect()


# museName = 'Muse-C3DD'
museName = 'Muse-3BEA'

plotWhat = 3
plotLength = 512  # denominated in samples
samplingBufferLen = 384  # max number of samples to be held between two plot updates
plotUpdateInterval = 100  # in milliseconds

sampleRate = 256
bandwidth = 0.707
whichFilters = [1, 1, 1]

highFreq = 0.1
highPass = butter_highpass(highFreq, sampleRate, order=5)

lowFreq = 30
lowPass = butter_lowpass(lowFreq, sampleRate, order=5)

notchFreq = 60
notchFilter = iir_notch(notchFreq, sampleRate, Q=30)
# Quality factor. Dimensionless parameter that characterizes notch filter -3 dB bandwidth
# relative to its center frequency, ``Q = w0/bw``.

muse = Muse(target_name=museName, max_buff_len=samplingBufferLen)
for i in range(10):
    print("Attempting to find " + museName + ". Attempt " + str(i + 1) + " of 10...")
    r = muse.connect()
    if r is not None:
        break
    else:
        print("No MUSE found, trying again...")
        continue

batt = muse.pullBattery()
print('Muse Battery is ' + str(batt))
plt.interactive(False)

global plotBuffer
global plotX
global eegData
eegData = np.zeros([plotLength, 6])

plotBuffer = np.zeros([plotLength, 4])
plotX = np.zeros([plotLength, 1])

fig = plt.figure()
fig.canvas.mpl_connect('close_event', close_handle)
ax1 = fig.add_subplot(2, 2, 3)
ax2 = fig.add_subplot(2, 2, 1)
ax3 = fig.add_subplot(2, 2, 2)
ax4 = fig.add_subplot(2, 2, 4)

if plotWhat == 1:
    ani = animation.FuncAnimation(fig, animateEEG, interval=plotUpdateInterval)

    plt.show()

if plotWhat == 2:
    ani = animation.FuncAnimation(fig, animateFFT, interval=plotUpdateInterval)

    plt.show()

if plotWhat == 3:
    ani = animation.FuncAnimation(fig, animateWavelet, interval=plotUpdateInterval)

    plt.show()
