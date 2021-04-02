from EasyMuse.Muse import Muse
import matplotlib;

matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def animateEEG(i):
    muse.updateBuffer()
    plotX, plotBuffer = muse.getPlot()

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
    muse.updateBuffer()
    fftX, fftCoefficients = muse.getPlotFFT()
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    ax1.bar(fftX, fftCoefficients[:, 0])
    ax2.bar(fftX, fftCoefficients[:, 1])
    ax3.bar(fftX, fftCoefficients[:, 2])
    ax4.bar(fftX, fftCoefficients[:, 3])

    ax1.set_ylim(0, 10)
    ax2.set_ylim(0, 10)
    ax3.set_ylim(0, 10)
    ax4.set_ylim(0, 10)


def animateWavelet(i):
    muse.updateBuffer()
    wavelet = muse.getPlotWavelet()
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    ax1.imshow(wavelet[0, :, :], aspect=muse.plotLength / 60, origin='lower')
    ax2.imshow(wavelet[1, :, :], aspect=muse.plotLength / 60, origin='lower')
    ax3.imshow(wavelet[2, :, :], aspect=muse.plotLength / 60, origin='lower')
    ax4.imshow(wavelet[3, :, :], aspect=muse.plotLength / 60, origin='lower')


def close_handle(evt):
    print("disconnecting Muse")
    muse.disconnect()


# museName = 'Muse-C3DD'
museName = 'Muse-3BEA'

plotWhat = 3
plotUpdateInterval = 100  # in milliseconds

sampleRate = 256

highFreq = 0.1
lowFreq = 30
notchFreq = 60

muse = Muse(target_name=museName, plotLength=512, sampleRate=256, highPassFreq=highFreq, lowPassFreq=lowFreq,
            notchFreq=notchFreq)

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
