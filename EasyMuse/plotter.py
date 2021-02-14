# In this file  we try to mimic the functionality of the MatlabMuse.m

from EasyMuse.Muse import Muse
from EasyMuse.helper import *
import matplotlib;

matplotlib.use("TkAgg")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def updateBuffer():
    global plotX
    global plotBuffer
    eegData = muse.pullEEG()  # Only the first four elements of every list member is valuable
    if eegData.__len__() >= samplingBufferLen:
        print("Warning: Missing samples. Increase the sampling buffer length or increase the plot update frequency")
    eegData = np.array(eegData)
    eegTimeStamp = eegData[:, 5]
    eegData = eegData[:, 0:4]
    # Here is where the filtering happens
    filteredEEG = eegData  # TODO

    plotX = np.append(plotX, eegTimeStamp)
    plotBuffer = np.append(plotBuffer, eegData, axis=0)

    plotX = plotX[-plotLength:]
    plotBuffer = plotBuffer[-plotLength:, :]


def animateEEG(i):
    global plotX
    global plotBuffer

    updateBuffer()

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

    updateBuffer()
    fftCoefficients = doMuseFFT(toFFT=plotBuffer, sRate=sampleRate)
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    ax1.bar(np.arange(1,fftCoefficients.shape[0]+1,1), fftCoefficients[:, 0])
    ax2.bar(np.arange(1,fftCoefficients.shape[0]+1,1), fftCoefficients[:, 1])
    ax3.bar(np.arange(1,fftCoefficients.shape[0]+1,1), fftCoefficients[:, 2])
    ax4.bar(np.arange(1,fftCoefficients.shape[0]+1,1), fftCoefficients[:, 3])

    ax1.set_ylim(0, 10)
    ax2.set_ylim(0, 10)
    ax3.set_ylim(0, 10)
    ax4.set_ylim(0, 10)

print('hi')

museName = 'Muse-C3DD'

plotWhat = 2
plotLength = 512  # denominated in samples
samplingBufferLen = 500  # number of samples to be held between two plot updates
plotUpdateInterval = 100  # in milliseconds

sampleRate = 256
bandwidth = 0.707
whichFilters = [1, 0, 1]

highFreq = 0.1
# highPassFilter = biQuadHighPass(highFreq, sampleRate, bandwidth)

lowFreq = 30
# lowPassFilter = biQuadLowPass(lowFreq, sampleRate, bandwidth)

notchFreq = 60
# notchFilter = biQuadNotch(notchFreq, sampleRate, bandwidth)

muse = Muse(target_name=museName, max_buff_len=samplingBufferLen)
for i in range(10):
    print("Attempting to connect to " + museName + ". Attempt " + str(i + 1) + " of 10...")
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

fig = plt.figure()
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)

if plotWhat == 1:

    plotBuffer = np.zeros([plotLength, 4])
    plotX = np.zeros([plotLength, 1])

    ani = animation.FuncAnimation(fig, animateEEG, interval=plotUpdateInterval)

    plt.show()

if plotWhat == 2:

    plotBuffer = np.zeros([plotLength, 4])
    plotX = np.zeros([plotLength, 1])

    ani = animation.FuncAnimation(fig, animateFFT, interval=plotUpdateInterval)

    plt.show()
