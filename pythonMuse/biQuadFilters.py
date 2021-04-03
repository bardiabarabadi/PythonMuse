import numpy as np


def biQuadHighPass(frequency, sampleRate, bandWidth):
    filterCoefficients = np.zeros([5, 1])

    omega = 2 * np.pi * frequency / sampleRate
    sn = np.sin(omega)
    cs = np.cos(omega)
    alpha = sn * np.sinh(np.log(2) / 2 * bandWidth * omega / sn)
    b0 = (1 + cs) / 2
    b1 = -1 * (1 + cs)
    b2 = (1 + cs) / 2
    a0 = 1 + alpha
    a1 = -2 * cs
    a2 = 1 - alpha

    filterCoefficients[0] = b0 / a0
    filterCoefficients[1] = b1 / a0
    filterCoefficients[2] = b2 / a0
    filterCoefficients[3] = a1 / a0
    filterCoefficients[4] = a2 / a0
    return filterCoefficients


def biQuadLowPass(frequency, sampleRate, bandWidth):
    filterCoefficients = np.zeros([5, 1])

    omega = 2 * np.pi * frequency / sampleRate
    sn = np.sin(omega)
    cs = np.cos(omega)
    alpha = sn * np.sinh(np.log(2) / 2 * bandWidth * omega / sn)
    b0 = (1 - cs) / 2
    b1 = 1 - cs
    b2 = (1 - cs) / 2
    a0 = 1 + alpha
    a1 = -2 * cs
    a2 = 1 - alpha

    filterCoefficients[0] = b0 / a0
    filterCoefficients[1] = b1 / a0
    filterCoefficients[2] = b2 / a0
    filterCoefficients[3] = a1 / a0
    filterCoefficients[4] = a2 / a0
    return filterCoefficients


def biQuadNotch(frequency, sampleRate, bandWidth):
    filterCoefficients = np.zeros([5, 1])

    omega = 2 * np.pi * frequency / sampleRate
    sn = np.sin(omega)
    cs = np.cos(omega)
    alpha = sn * np.sinh(np.log(2) / 2 * bandWidth * omega / sn)
    b0 = 1
    b1 = -2 * cs
    b2 = 1
    a0 = 1 + alpha
    a1 = -2 * cs
    a2 = 1 - alpha

    filterCoefficients[0] = b0 / a0
    filterCoefficients[1] = b1 / a0
    filterCoefficients[2] = b2 / a0
    filterCoefficients[3] = a1 / a0
    filterCoefficients[4] = a2 / a0
    return filterCoefficients


def biQuadFilter(coefficients, eegSample, pastSamples, pastResults):
    filteredSample = np.zeros(eegSample.shape)

    nPoints = eegSample.shape[1]

    samplesToCount = list(range(nPoints - 1, -1, -1))

    for sampleCounter in samplesToCount:
        filteredSample[:, sampleCounter] = coefficients[0] * eegSample[:, sampleCounter] + \
                                           coefficients[1] * pastSamples[:, 0] + \
                                           coefficients[2] * pastSamples[:, 1] - \
                                           coefficients[3] * pastResults[:, 0] - \
                                           coefficients[4] * pastResults[:, 1]
        pastSamples[:, 1] = pastSamples[:, 0]
        pastSamples[:, 0] = eegSample[:, sampleCounter]
        pastResults[:, 1] = pastResults[:, 0]
        pastResults[:, 0] = filteredSample[:, sampleCounter]

    return filteredSample, pastSamples, pastResults


def applyBiQuad(sample, whichFilters, highPass, lowPass, notchFilter, samples, results):
    if whichFilters[0] == 1:
        sample, samples[:, :, 0], results[:, :, 0] = biQuadFilter(highPass, sample, samples[:, :, 0], results[:, :, 0])
    if whichFilters[1] == 1:
        sample, samples[:, :, 1], results[:, :, 1] = biQuadFilter(lowPass, sample, samples[:, :, 1], results[:, :, 1])
    if whichFilters[2] == 1:
        sample, samples[:, :, 2], results[:, :, 2] = biQuadFilter(notchFilter, sample, samples[:, :, 2],
                                                                  results[:, :, 2])
    return sample, samples, results
