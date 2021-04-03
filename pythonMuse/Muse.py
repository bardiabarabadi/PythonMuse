from functools import partial

from .MuseBLE import *
from .MuseFinder import *
from .butterFilters import *
from .constants import *
from .helper import *


class Muse:

    def __init__(self,
                 loop=None,  # the current eventloop. Only use if using Kivy GUI
                 target_name=None,  # Should be a string containing four digits/letters
                 timeout=10,  # Connection (and search) timeout
                 plotLength=512,  # length of the plot (horizantal, in samples)
                 sampleRate=256,  # Sample rate
                 highPassFreq=-1,  # -1 indicates that this filter will not be used
                 lowPassFreq=-1,  # -1 indicates that this filter will not be used
                 notchFreq=-1,  # -1 indicates that this filter will not be used
                 filterOrder=5  # Butterworth Filter order for low/high pass filters
                 ):
        self.all_muses = []
        self.target_name = target_name
        self.timeout = timeout
        self.muse = None
        self.target_muse = None

        self.eeg_buff = []
        self.ppg_buff = []
        self.acc_buff = []
        self.gyro_buff = []
        self.max_buff_len = plotLength
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        self.recv_command = None
        self.plotLength = plotLength
        self.sampleRate = sampleRate

        self.highPassFreq = highPassFreq
        self.lowPassFreq = lowPassFreq
        self.notchFreq = notchFreq
        self.filterOrder = filterOrder

        self.highPassFilter = None
        self.lowPassFilter = None
        self.notchFilter = None

        self.makeFilters()

        self.eegData = np.zeros([plotLength, 6])
        self.plotBuffer = np.zeros([plotLength, 4])
        self.plotX = np.zeros([plotLength, 1])

        self.fifo_offset = int(plotLength / 4)

    def disconnect(self):
        self.loop.run_until_complete(self.muse.disconnect())
        self.loop.run_until_complete(self.muse.disconnect())

    def connect(self, target_name=None):

        if target_name is not None:
            self.target_name = target_name
        elif self.target_name is None:
            print("No target name specified")
            return None

        mf = MuseFinder()
        self.loop.run_until_complete(mf.search_for_muses(timeout=self.timeout))
        self.all_muses = mf.get_muses()

        if len(self.all_muses) < 1:
            print("No MUSEs found, please try again or increase the timeout")
            return None
        else:
            found = False
            for d in self.all_muses:
                if self.target_name.upper() in d.name.upper():
                    print("Target MUSE found. Attempting to connect...")
                    self.target_muse = d
                    found = True
            if found is False:
                print("Couldn't find target, + " + str(self.target_name) + ". Try again or increase the timeout.")
                return None

        # Connecting
        push_eeg = partial(self._push, offset=EEG_PORT_OFFSET)
        push_ppg = partial(self._push, offset=PPG_PORT_OFFSET)
        push_acc = partial(self._push, offset=ACC_PORT_OFFSET)
        push_gyro = partial(self._push, offset=GYRO_PORT_OFFSET)
        self.muse = MuseBLE(client=self.target_muse, callback_control=self._command_callback,
                            callback_acc=push_acc, callback_eeg=push_eeg, callback_gyro=push_gyro,
                            callback_ppg=push_ppg)
        try:
            self.loop.run_until_complete(self.muse.connect(timeout=30))
        except asyncio.exceptions.TimeoutError:
            print("30 second time out reached, cannot connect to MUSE! Ty again...")
            return None
        print("connection was successful")
        _ = self.pullACC()
        _ = self.pullEEG()
        _ = self.pullGyro()
        _ = self.pullPPG()
        return self

    def pullEEG(self):
        self.loop.run_until_complete(self.muse.start())
        to_return = self.eeg_buff
        self.eeg_buff = []
        return to_return

    def pullPPG(self):
        self.loop.run_until_complete(self.muse.start())
        to_return = self.ppg_buff
        self.ppg_buff = []
        return to_return

    def pullACC(self):
        self.loop.run_until_complete(self.muse.start())
        to_return = self.acc_buff
        self.acc_buff = []
        return to_return

    def pullGyro(self):
        self.loop.run_until_complete(self.muse.start())
        to_return = self.gyro_buff
        self.gyro_buff = []
        return to_return

    def reset_buffers(self):
        self.eeg_buff = []
        self.ppg_buff = []
        self.acc_buff = []
        self.gyro_buff = []

    def _push(self, data, timestamps, offset=0):
        for ii in range(data.shape[1]):
            if not is_data_valid(data[:, ii], timestamps[ii]):
                continue
            if offset == EEG_PORT_OFFSET:
                to_append_eeg_data = [data[0, ii], data[1, ii], data[2, ii], data[3, ii], data[4, ii],
                                      (timestamps[ii])]
                if len(self.eeg_buff) >= self.max_buff_len:
                    self.eeg_buff.pop(0)
                self.eeg_buff.append(to_append_eeg_data)

            elif offset == PPG_PORT_OFFSET:
                to_append_ppg_data = [data[0, ii], data[1, ii], data[2, ii],
                                      (timestamps[ii])]
                if len(self.ppg_buff) >= self.max_buff_len:
                    self.ppg_buff.pop(0)
                self.ppg_buff.append(to_append_ppg_data)

            elif offset == ACC_PORT_OFFSET:
                to_append_acc_data = [data[0, ii], data[1, ii], data[2, ii],
                                      (timestamps[ii])]
                if len(self.acc_buff) >= self.max_buff_len:
                    self.acc_buff.pop(0)
                self.acc_buff.append(to_append_acc_data)

            elif offset == GYRO_PORT_OFFSET:
                to_append_gyro_data = [data[0, ii], data[1, ii], data[2, ii],
                                       (timestamps[ii])]
                if len(self.gyro_buff) >= self.max_buff_len:
                    self.gyro_buff.pop(0)
                self.gyro_buff.append(to_append_gyro_data)

    def _command_callback(self, a):
        if len(a) != 1:
            self.recv_command = a

    def pullBattery(self):
        self.recv_command = None
        for i in range(10):
            self.loop.run_until_complete(self.muse.ask_control())
            if self.recv_command is not None:
                break
            self.loop.run_until_complete(asyncio.sleep(1))
        if self.recv_command is None:
            return -1
        else:
            return self.recv_command['bp']

    def makeFilters(self):  # set up the filters is selected by the user
        if self.highPassFreq > 0:  # only if the frequency is positive
            self.highPassFilter = butter_highpass(self.highPassFreq, self.sampleRate, self.filterOrder)
        if self.lowPassFreq > 0:  # only if the frequency is positive
            self.lowPassFilter = butter_lowpass(self.lowPassFreq, self.sampleRate, self.filterOrder)
        if self.notchFreq > 0:  # only if the frequency is positive
            self.notchFilter = iir_notch(self.notchFreq, self.sampleRate, Q=30)
            # Q=Quality factor. Dimensionless parameter that characterizes notch filter -3 dB bandwidth
            # relative to its center frequency, ``Q = w0/bw``.

    def updateBuffer(self):
        eegData_new = self.pullEEG()  # Pull new samples from MUSE
        new_samples_count = eegData_new.__len__()  # Get the number of new samples received
        if new_samples_count == 0:  # return if no new samples received
            return
        if new_samples_count > self.fifo_offset * 2 - 1:  # If received samples count is greater than maximum allowed
            print("Got too many samples. Trimming " + str(new_samples_count - self.fifo_offset * 2) + " samples...")
            eegData_new = eegData_new[:self.fifo_offset * 2 - 1]  # trim extra samples
            new_samples_count = self.fifo_offset * 2 - 1  # update the new sample count (post-trimming)

        eegData_new = np.array(eegData_new)  # cast list to np.array
        t = (eegData_new[:, 5] < 100)  # Find invalid samples (if timestamp is too small, should be a very large number)
        a = [i for i, x in enumerate(t) if x]  # find invalid samples' indices
        eegData_new = np.delete(eegData_new, a, axis=0)  # remove the invalid samples
        # FIFO implementation
        self.eegData = np.roll(self.eegData, -new_samples_count,
                               axis=0)  # roll over the old eegData to make room for the new samples
        self.eegData[-new_samples_count:, :] = eegData_new  # Fill in the FIFO with new samples

        eegData_filtered_t = self.eegData  # Initiate filtering
        # Filtering
        eegData_filtered_t[:, 0:4] = applyButter(self.eegData[:, 0:4], self.highPassFilter, self.lowPassFilter,
                                                 self.notchFilter)  # See function implementation for more details

        self.plotX = np.roll(self.plotX, -new_samples_count)  # roll thw timestamps to make room for new samples (FIFO)
        self.plotX[-new_samples_count:, 0] = eegData_filtered_t[  # Append new timestamps (from the middle of the FIFO)
                                             -self.fifo_offset - new_samples_count: -self.fifo_offset, 5]

        self.plotBuffer = np.roll(self.plotBuffer, -new_samples_count, axis=0)  # Roll the output (filtered) fifo
        self.plotBuffer[-new_samples_count:, 0:4] = eegData_filtered_t[  # Append new samples (filtered) to the FIFO
                                                    -self.fifo_offset - new_samples_count:-self.fifo_offset, 0:4]

    def getPlot(self):
        return self.plotX, self.plotBuffer  # return time stamps and filtered samples.

    def getPlotFFT(self):
        fftCoefficients = doMuseFFT(toFFT=self.plotBuffer, sRate=self.sampleRate)  # Perform FFT on the samples
        fftFrequencies = np.arange(1, fftCoefficients.shape[0] + 1, 1)  # X-axis values for the FFT bar chart
        return fftFrequencies, fftCoefficients

    def getPlotWavelet(self, frequencySteps=60, minimumFrequency=1, maximumFrequency=30):
        return doMuseWavelet(toWavelet=self.plotBuffer, sRate=self.sampleRate, frequencySteps=frequencySteps,
                             minimumFrequency=minimumFrequency, maximumFrequency=maximumFrequency)
