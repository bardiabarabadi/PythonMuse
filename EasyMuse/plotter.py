# In this file  we try to mimic the functionality of the MatlabMuse.m

from EasyMuse.Muse import Muse
from EasyMuse.helper import *
import matplotlib;

matplotlib.use("TkAgg")

# from EasyMuse.biQuadFilters import *
from EasyMuse.butterFilters import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def updateBuffer():
    global plotX
    global plotBuffer
    global previousSamples, previousResults
    global eegData
    # start_buffering_and_filtering_time = time.time()
    fifo_offset = int(eegData.shape[0] / 4)

    # if eegData.__len__() > samplingBufferLen:
    #     print("Warning: Missing samples. Increase the sampling buffer length or increase the plot update frequency")

    eegData_new = muse.pullEEG()  # Only the first four elements of every list member is valuable
    new_samples_count = eegData_new.__len__()
    # print('len: ' + str(new_samples_count))
    if new_samples_count == 0:
        return
    if new_samples_count > fifo_offset * 3 - 1:
        print("Got too man samples. Trimming " + str(new_samples_count - fifo_offset * 3) + " samples...")
        eegData_new = eegData_new[:fifo_offset * 3 - 1]
        new_samples_count = fifo_offset * 3 - 1

    eegData_new = np.array(eegData_new)
    t = (eegData_new[:, 5] < 100)
    a = [i for i, x in enumerate(t) if x]
    eegData_new = np.delete(eegData_new, a, axis=0)
    eegData = np.roll(eegData, -new_samples_count, axis=0)
    eegData[-new_samples_count:, :] = eegData_new

    eegData_filtered_t = eegData
    # Filtering
    # start_filtering_time = time.time()
    eegData_filtered_t[:, 0:4] = applyButter(eegData[:, 0:4], whichFilters, highPass, lowPass, notchFilter)
    # end_filtering_time = time.time()
    # print ("Elapsed Filtering: " + str(end_filtering_time - start_filtering_time))

    eegData[:, 0:4] = eegData_filtered_t[:, 0:4]
    plotX = np.roll(plotX, -new_samples_count)
    plotX[-new_samples_count:, 0] = eegData_filtered_t[-fifo_offset - new_samples_count:-fifo_offset, 5]

    plotBuffer = np.roll(plotBuffer, -new_samples_count, axis=0)
    plotBuffer[-new_samples_count:, 0:4] = eegData_filtered_t[-fifo_offset - new_samples_count:-fifo_offset, 0:4]

    # end_buffering_and_filtering_time = time.time()
    # print ("Elapsed buffering and filtering time: " + str(end_buffering_and_filtering_time-start_buffering_and_filtering_time))


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

    updateBuffer()
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
updateBuffer()
updateBuffer()
updateBuffer()
exit()
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
    ani = animation.FuncAnimation(fig, animateWavelet, interval=plotUpdateInterval, )

    plt.show()
