import numpy as np
from scipy import fft as spfft

from EasyMuse.butterFilters import *


def is_data_valid(data, timestamps):
    if timestamps == 0.0:
        return False
    if all(data == 0.0):
        return False
    return True


def PPG_error(Exceptions):
    pass


def doMuseFFT(toFFT, sRate):
    lengthFFT = toFFT.shape[0]
    resolution = sRate / lengthFFT
    frequenciesToKeep = 60

    binWidth = int(np.ceil(1 / resolution))
    numBins = int(np.floor(frequenciesToKeep / binWidth))

    coefficients = np.fft.fft(toFFT, axis=0)
    coefficients = coefficients / lengthFFT
    coefficients = np.abs(coefficients)
    coefficients = coefficients[1:frequenciesToKeep + 1] * 2

    coefficients = np.reshape(coefficients, [numBins, binWidth, toFFT.shape[1]])
    coefficients = np.mean(coefficients, axis=1)

    return coefficients


def doMuseWavelet(toWavelet, sRate):
    minimumFrequency = 1
    maximumFrequency = 30
    frequencySteps = 60
    mortletParameter = [6]
    samplingRate = sRate

    frequencyResolution = np.linspace(start=minimumFrequency, stop=maximumFrequency, num=frequencySteps)  # linear scale
    s = np.divide(
        np.logspace(start=np.log10(mortletParameter[0]), stop=np.log10(mortletParameter[-1]), num=frequencySteps), (
                2 * np.pi * frequencyResolution))
    waveletTime = np.arange(start=-2, stop=2, step=1 / samplingRate)

    lengthWavelet = waveletTime.shape[0] + 1
    middleWavelet = int((lengthWavelet - 1) / 2)

    lengthData = toWavelet.shape[0]

    lengthConvolution = lengthWavelet + lengthData - 1

    waveletData = np.zeros([toWavelet.shape[1], frequencyResolution.shape[0], toWavelet.shape[0]])
    for channelCounter in range(toWavelet.shape[1]):

        channelData = toWavelet[:, channelCounter]
        fftData = spfft.fft(channelData, lengthConvolution)
        timeFrequencyData = np.zeros([toWavelet.shape[0], frequencyResolution.shape[0]])

        for fi in range(frequencyResolution.shape[0]):
            wavelet = np.multiply(
                np.exp(2 * (0 + 1j) * np.pi * frequencyResolution[fi] * waveletTime),
                np.exp(-waveletTime ** 2 / (2 * s[fi] ** 2)))

            fftWavelet = spfft.fft(wavelet, lengthConvolution)
            fftWavelet = fftWavelet / np.max(fftWavelet)

            waveletOutput = spfft.ifft(np.multiply(fftWavelet, fftData))

            waveletOutput = waveletOutput[middleWavelet:-middleWavelet]

            timeFrequencyData[:, fi] = np.abs(waveletOutput)

        waveletData[channelCounter, :, :] = timeFrequencyData.T
    return waveletData


def updateBuffer(plotX, plotBuffer, eegData, muse, whichFilters, highPass, lowPass, notchFilter):
    fifo_offset = int(eegData.shape[0] / 4)

    eegData_new = muse.pullEEG()
    new_samples_count = eegData_new.__len__()
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
    eegData_filtered_t[:, 0:4] = applyButter(eegData[:, 0:4], whichFilters, highPass, lowPass, notchFilter)

    eegData[:, 0:4] = eegData_filtered_t[:, 0:4]
    plotX = np.roll(plotX, -new_samples_count)
    plotX[-new_samples_count:, 0] = eegData_filtered_t[-fifo_offset - new_samples_count:-fifo_offset, 5]

    plotBuffer = np.roll(plotBuffer, -new_samples_count, axis=0)
    plotBuffer[-new_samples_count:, 0:4] = eegData_filtered_t[-fifo_offset - new_samples_count:-fifo_offset, 0:4]

    return plotX, plotBuffer, eegData
