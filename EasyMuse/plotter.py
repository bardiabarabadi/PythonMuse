# In this file  we try to mimic the functionality of the MatlabMuse.m

from EasyMuse.Muse import Muse
import matplotlib;

matplotlib.use("TkAgg")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def animate(i):
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

    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax1.plot(plotX, plotBuffer[:, 0])
    ax2.plot(plotX, plotBuffer[:, 1])
    ax3.plot(plotX, plotBuffer[:, 2])
    ax4.plot(plotX, plotBuffer[:, 3])


print('hi')

museName = 'Muse-C3DD'

plotWhat = 1
plotLength = 1000  # denominated in samples
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
muse.connect()

batt = muse.pullBattery()
print('Muse Battery is ' + str(batt))
plt.interactive(False)

if plotWhat == 1:
    fig = plt.figure()
    ax1 = fig.add_subplot(2, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    ax1.set_ylim(-1000,1000)
    ax2.set_ylim(-1000,1000)
    ax3.set_ylim(-1000,1000)
    ax4.set_ylim(-1000,1000)

    global plotBuffer
    global plotX
    plotBuffer = np.zeros([plotLength, 4])
    plotX = np.zeros([plotLength, 1])

    ani = animation.FuncAnimation(fig, animate, interval=plotUpdateInterval)

    plt.show()
