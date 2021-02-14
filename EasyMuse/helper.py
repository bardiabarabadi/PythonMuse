import numpy as np


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

    binWidth = int(np.ceil(1/resolution))
    numBins = int(np.floor(frequenciesToKeep/binWidth))

    coefficients = np.fft.fft(toFFT, axis=0)
    coefficients = coefficients / lengthFFT
    coefficients = np.abs(coefficients)
    coefficients = coefficients[1:frequenciesToKeep+1] * 2


    coefficients = np.reshape(coefficients, [numBins,binWidth,toFFT.shape[1]])
    coefficients = np.mean(coefficients, axis=1)

    return coefficients
