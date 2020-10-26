import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftfreq
from scipy.interpolate import interp1d
import copy
import logging

class Sensor():
    '''
    Class Sensor has all the methods that can be applied to the data of a specific sensor
    '''
    def __init__(self,cdfFileClass, sensorName):

        '''
        ######################################################
        ######################################################
                            Attributes
        ######################################################
        ######################################################
        '''
        ### Logger
        self.logger = logging.getLogger('__main__')
        ###  Name of the sensor
        self.name = sensorName
        ### Path of the CDF file
        self.filePath = cdfFileClass.filePath
        ### Name of the file
        self.fileName = cdfFileClass.fileName
        ### Position of the sensor in the attribute data of the class cdfFileClass
        self.sensorPos = cdfFileClass.CDFpos(sensorName)
        ### Relative time (from 0 to the end)
        self.time = cdfFileClass.time
        self.timeInitial = cdfFileClass.timeInitial
        ### Data of the sensor
        if sensorName == 'GMT':
            self.data = cdfFileClass.time
            self.dataInitial = copy.deepcopy(cdfFileClass.time)
        else:
            self.data = cdfFileClass.data[self.sensorPos]
            self.dataInitial = copy.deepcopy(cdfFileClass.data[self.sensorPos])
        ### Sample rate (deleting nan values that could be in attribute time due to cutting data)
        self.sampleRate = 1/(self.timeInitial[1]-self.timeInitial[0])
        ### Units of sensor
        self.units = cdfFileClass.units[self.name]
        self.fullName = cdfFileClass.fullName[self.name]

    '''
    ######################################################
    ######################################################
                        Methods
    ######################################################
    ######################################################
    '''

    def moving_average(self,overlap, stepSize):
        '''
        Calculate moving average, taking as input overlap (%) and step (S)
        '''

        # stepSize: number of elements that are going to be used every step
        stepSize = int(self.sampleRate * stepSize)
        # overlapSize: number of elements that are going to be used every step
        overlapSize = int(stepSize * overlap * 0.01)

        # To avoid problems when changing value of stepSize in Main Window
        if stepSize == 0:
            moveMean = copy.deepcopy(self.dataInitial)
        else:
            # Moving average
            moveMean = [np.mean(self.dataInitial[i:i + stepSize]) for i in range(0, self.dataInitial.shape[0], stepSize - overlapSize)]
            moveMean = np.asarray(moveMean)
            # Time with the shape of moveMean
            timeMoveMean = np.linspace(self.timeInitial[0], self.timeInitial[-1], moveMean.shape[0])

            # Interpolating to have the same shape that global time and data
            f1 = interp1d(timeMoveMean, moveMean, kind='cubic')
            time = np.linspace(self.timeInitial[0], self.timeInitial[-1], self.time.shape[0])
            moveMean = f1(time)

        return moveMean

    def resampleRate(self, new_sampleRate):
        # The new data and time values are created with the new sampleRate
        new_sampleRate = int(new_sampleRate)
        if len(self.dataInitial) == 0:
            pass
        else:

            f1 = interp1d(self.timeInitial, self.dataInitial, kind = 'cubic')
            self.time = np.arange(self.timeInitial[0], self.timeInitial[-1], 1/new_sampleRate)
            self.data = f1(self.time)
            self.dataInitial = copy.deepcopy(self.data)
            self.timeInitial = copy.deepcopy(self.time)

        self.sampleRate=new_sampleRate

    def cut_data(self,rangeList):
        '''
        This function cuts the data in different ranges, specified in var rangeList

        :param rangeList: List with list of ranges -> Example: rangeList = [[0,13.4], [13.4,22], [22,35]]
        RANGE1 = [0,13.4]
        RANGE2 = [13.4,22]
        RANGE3 = [22,35]
        '''

        # Mask with the length of every sensor data
        mask = np.zeros(self.timeInitial.shape[0])
        n = 0
        for rangeTime in rangeList:
            # Lower time in the range
            first_time = rangeTime[0]
            # Bigger time in the range
            last_time = rangeTime[1]
            # Index of elements that meet the specifications
            indexSpecific = np.where((self.timeInitial >= first_time) & (self.timeInitial <= last_time))[0]

            # Deleting some values of the index, so that the ranges are:
            # Range1 -> [)
            # Range2 -> ()
            # Range3 -> (]
            # It has been done to avoid problems when splitting with times as showed in the example:
            # Range1 -> [0,15], Range2 -> [15,20], Range3 -> [20,30]
            # Doing this there will be not any problem when plotting C+S+V
            if n == 0:
                indexSpecific = indexSpecific[:-1]
            elif n == len(rangeList):
                indexSpecific = indexSpecific[1:]
            else:
                indexSpecific = indexSpecific[1:-1]
            # Changing to 1 all elements that meet the specifications
            np.put(mask, indexSpecific, 1)

            n += 1

        # Changing time attribute
        mask = mask.astype(bool)

        self.time[mask == False] = np.nan

    def detrend(self,overlap,stepSize):
        '''
        Detrend sis defined as data - steady (moving average)
        '''
        dataMovingAvarage = self.moving_average(overlap,stepSize)
        dataDetrended = self.dataInitial - dataMovingAvarage
        return dataDetrended

    def movingRMS(self,overlap, stepSize):
        '''
        RMS is Moving Root Mean Square:
        RMS = sqrt( 1/n * ( X1**2 + X2**2 + X3**2 + ... + Xn**2 ) )
        This function will be applied taking into account the overlap and the step size.
        For all the values of every step, detrend is going to be applied before apply RMS -> Airbus asked for it
        '''

        # stepSize: number of elements that are going to be used every step
        stepSize = int(self.sampleRate * stepSize)
        # overlapSize: number of elements that are going to be used every step
        overlapSize = int(stepSize * overlap * 0.01)

        # Moving RMS
        if stepSize == 0:
            RMS = np.sqrt(np.mean(np.power(signal.detrend(self.dataInitial),2)))
            moveRMS = np.ones(self.dataInitial.shape[0])*RMS
        else:
            moveRMS = [np.sqrt(np.mean(np.power(signal.detrend(self.dataInitial[i:i+stepSize]),2))) for i in range(0,self.dataInitial.shape[0],stepSize - overlapSize)]
            moveRMS = np.asarray(moveRMS)
        # Time with the shame shape of moveRMS
        timeMoveRMS = np.linspace(self.timeInitial[0], self.timeInitial[-1], moveRMS.shape[0])

        # Changing shape of moveRMS and timeMoveRMS to global shape of data and time
        f1 = interp1d(timeMoveRMS, moveRMS, kind='cubic')
        time = np.linspace(self.timeInitial[0], self.timeInitial[-1], self.time.shape[0])
        moveRMS = f1(time)
        return moveRMS

    def displacements(self, lowFreq, highFreq, win):
        '''
        Using digital integrations scheme to calculate displacements is not he best way to do this,
        because they accumulate errors, so it is going to be used Fourier transformation.

        - 1. Conversion to freq domain of the ACC data
        - 2. Filter the desired frequencies (modes, noise, etc)
        - 3. Conversion to displacements in the freq domain
        - 4. Reconstruction of the time series signal
        '''

        self.logger.info('Displacement calculated with the following properties:')
        self.logger.info('- Low pass filter frequency: {}'.format(highFreq))
        self.logger.info('- High pass filter frequency: {}'.format(lowFreq))
        self.logger.info('- Window: {}'.format(win))

        n = self.dataInitial.shape[0]
        if win == 'blackman':
            data = self.dataInitial * np.blackman(n)
        elif win == 'barthann':
            data = self.dataInitial * signal.windows.barthann(n)
        elif win == 'bartlett':
            data = self.dataInitial * signal.windows.bartlett(n)
        elif win == 'hann':
            data = self.dataInitial * signal.windows.hann(n)
        elif win == 'hanning':
            data = self.dataInitial * signal.windows.hanning(n)
        else:
            data = copy.deepcopy(self.dataInitial)


        # Data detrended
        data = signal.detrend(data)
        dt = self.timeInitial[1] - self.timeInitial[0]

        #Data-Time to Data-Freq
        data_freq = np.fft.fft(data)
        freq = fftfreq(n, d=dt)

        #Filter freq -> To erase signal noise -> Change values to 0
        minFreq = lowFreq
        maxFreq = highFreq
        data_freq[np.where(freq<minFreq)] = 0
        data_freq[np.where(freq>maxFreq)] = 0

        # Angular velocity
        w2y = (2*np.pi*freq)**2.

        Y_filt_disp = -(9810*data_freq[1:])/w2y[1:]
        Y_filt_disp = np.insert(Y_filt_disp, 0, 0)

        Yt_ifft_disp = np.fft.ifft(Y_filt_disp)
        Yt_ifft_disp = Yt_ifft_disp.real

        # Creating time with shape of displacements
        timeDisplacem = np.linspace(self.timeInitial[0],self.timeInitial[-1], Yt_ifft_disp.shape[0])

        # Modidying shape to global date and time shape
        f1 = interp1d(timeDisplacem, Yt_ifft_disp, kind='cubic')
        time = np.linspace(self.timeInitial[0], self.timeInitial[-1], self.time.shape[0])
        Yt_ifft_disp = f1(time)

        self.logger.info('****************************************')

        return Yt_ifft_disp

    def applyFilter(self, highPassFreq, lowPassFreq, orderValue):
        data = copy.deepcopy(self.dataInitial)
        if (orderValue == 'n') or (orderValue == ''):
            self.logger.info('Please, order number is required to apply frequency filter.')
            self.logger.info('High pass filter not applied')
            self.logger.info('Low pass filter not applied')

        else:
            nyquistFrequency = self.sampleRate / 2
            orderValue = int(orderValue)
            try:
                lowPassFreq = float(lowPassFreq)
                if (lowPassFreq >= nyquistFrequency):
                    text = 'There have been a problem. User mus take into account that the frequencies should have a ' \
                           'value between 1 Hz and {} Hz, due to the Nyquist theorem.'.format(nyquistFrequency)
                    self.logger.info(text)
                else:
                    # The frequency is normalized (Nyquist)
                    w = lowPassFreq / (self.sampleRate / 2)
                    b, a = signal.butter(orderValue, w, 'lowpass')
                    data = signal.filtfilt(b, a, data)

                    self.logger.info('Applying low pass filter:')
                    self.logger.info('Low pass frequency = {} hz'.format(lowPassFreq))
                    self.logger.info('Order filter = {}'.format(orderValue))
            except:
                self.logger.info('Low pass filter not applied')

            try:
                highPassFreq = float(highPassFreq)
                if (highPassFreq >= nyquistFrequency):
                    text = 'There have been a problem. User mus take into account that the frequencies should have a ' \
                           'value between 1 Hz and {} Hz, due to the Nyquist theorem.'.format(nyquistFrequency)
                    self.logger.info(text)
                else:
                    # The frequency is normalized (Nyquist)
                    w = highPassFreq / (self.sampleRate / 2)
                    b, a = signal.butter(orderValue, w, 'highpass')
                    data = signal.filtfilt(b, a, data)

                    self.logger.info('High pass filter applied:')
                    self.logger.info('High pass frequency = {} hz'.format(highPassFreq))
                    self.logger.info('Order filter = {}'.format(orderValue))
            except:
                self.logger.info('High pass filter not applied')

        self.data = data

    def decimate(self,downsampling_factor,filter_order, order):
        return signal.decimate(self.dataInitial,downsampling_factor,filter_order, ftype='fir')
               
    def tofreq(self,win, detrendBool, highPassFreq, lowPassFreq, order):
        '''
        Changing data to frequency data
        '''

        self.logger.info('FFT calculated with the following properties:')

        self.logger.info('- Window {}'.format(win))
        self.logger.info('- Frequency of data: {}'.format(self.sampleRate))
        self.logger.info('- No detrend applied')
        if detrendBool:
            self.logger.info('- Detrend applied')
        else:
            self.logger.info('- Detrend no applied')

        highPassBool = False
        lowPassBool = False
        if order == 'n':
            self.logger.info('- No high pass filter applied')
            self.logger.info('- No low pass filter applied')
        else:
            order = int(order)
            if highPassFreq == 'High pass' or highPassFreq== '':
                self.logger.info('- No high pass filter applied')
            else:
                highPassFreq = float(highPassFreq)
                highPassBool = True
                self.logger.info('- High pass filter applied. Cut of: {} hz'.format(highPassFreq))
            if lowPassFreq == 'Low pass' or lowPassFreq == '':
                self.logger.info('- No low pass filter applied')
            else:
                lowPassFreq = float(lowPassFreq)
                lowPassBool = True
                self.logger.info('- Low pass filter applied. Cut of: {} hz'.format(lowPassFreq))


        # Creating splitted ranges (if exist)
        timeSplitted = [self.time[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(self.time))]
        dataSplitted = [self.data[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(self.time))]

        freqSplitted = []
        dataFreqWindowSplitted = []

        # Loop through all ranges
        for index in range(len(timeSplitted)):
            timeRange = timeSplitted[index]
            dataRange = dataSplitted[index]

            if highPassBool:
                # The frequency is normalized (Nyquist)
                w = highPassFreq / (self.sampleRate / 2)
                b, a = signal.butter(N = order, Wn = w, btype ='highpass')
                dataRange = signal.filtfilt(b, a, dataRange)

            if lowPassBool:
                # The frequency is normalized (Nyquist)
                w = lowPassFreq / (self.sampleRate / 2)
                b, a = signal.butter(N =order, Wn = w, btype ='lowpass')
                dataRange = signal.filtfilt(b, a, dataRange)


            dt = timeRange[1] - timeRange[0]
            n = timeRange.shape[0]  # Number of intervals
            if detrendBool:
                dataRange = signal.detrend(dataRange)
            else:
                pass

            if win == 'blackman':
                data_freq_window = fft(dataRange*np.blackman(n))
                freq = fftfreq(n, d =dt)

            elif win == 'barthann':
                data_freq_window = fft(dataRange*signal.windows.barthann(n))
                freq = fftfreq(n, d =dt)
            elif win == 'bartlett':
                data_freq_window = fft(dataRange*signal.windows.bartlett(n))
                freq = fftfreq(n, d =dt)
            elif win == 'hann':
                data_freq_window = fft(dataRange*signal.windows.hann(n))
                freq = fftfreq(n, d =dt)
            elif win == 'hanning':
                data_freq_window = fft(dataRange*signal.windows.hanning(n))
                freq = fftfreq(n, d =dt)
            else:
                data_freq_window = fft(dataRange)
                freq = fftfreq(n, d =dt)

            freqSplitted.append(freq)
            dataFreqWindowSplitted.append(data_freq_window)

        self.logger.info('****************************************')

        return freqSplitted, dataFreqWindowSplitted

    def PSD(self, stepWin, overlapWin, win, detrendBool, order, highPassFreq, lowPassFreq ):
        # Creating splitted ranges (if exist)
        timeSplitted = [self.time[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(self.time))]

        freqSplitted = []
        PSDSplitted = []

        self.logger.info('Calculating PSD with the following attributes:')
        self.logger.info('- PSD calculated using Welch’s method.')
        self.logger.info('- Sample rate: {} hz'.format(self.sampleRate))
        if win == 'none':
            win = 'hanning'
            self.logger.info('- Window is imperative. Hanning window will be used.')
        else:
            self.logger.info('- Type of window applied: {}'.format(win))
        self.logger.info('- Number of elements of bins: {}'.format(stepWin))
        self.logger.info('- Number of elements of overlap: {}'.format(overlapWin))
        if detrendBool:
            detrendType = 'constant'
            self.logger.info('- Detrend applied')
        else:
            detrendType = 'constant'
            self.logger.info('- Detrend the signal is imperative for PSD. Detrend applied.')

        highPassBool = False
        lowPassBool = False
        if order == 'n':
            self.logger.info('- No high pass filter applied')
            self.logger.info('- No low pass filter applied')
        else:
            order = int(order)
            if highPassFreq == 'High pass' or highPassFreq == '':
                self.logger.info('- No high pass filter applied')
            else:
                highPassFreq = float(highPassFreq)
                highPassBool = True
                self.logger.info('- High pass filter applied. Cut of: {} hz'.format(highPassFreq))
            if lowPassFreq == 'Low pass' or lowPassFreq == '':
                self.logger.info('- No low pass filter applied')
            else:
                lowPassFreq = float(lowPassFreq)
                lowPassBool = True
                self.logger.info('- Low pass filter applied. Cut of: {} hz'.format(lowPassFreq))

        # Loop through all ranges
        for timeRange in timeSplitted:
            # Saving all indexes of every range
            indexRange = []
            for timeValue in timeRange:
                indexRange.append(np.where(self.time == timeValue)[0][0])

            data = self.data[indexRange]

            if highPassBool:
                # The frequency is normalized (Nyquist)
                w = highPassFreq / (self.sampleRate / 2)
                b, a = signal.butter(N = order, Wn = w, btype ='highpass')
                data = signal.filtfilt(b, a, data)

            if lowPassBool:
                # The frequency is normalized (Nyquist)
                w = lowPassFreq / (self.sampleRate / 2)
                b, a = signal.butter(N =order, Wn = w, btype ='lowpass')
                data = signal.filtfilt(b, a, data)


            freq, PSD = signal.welch(data, fs=self.sampleRate,window = win, nperseg=stepWin,
                                     noverlap=overlapWin,detrend = detrendType)

            freqSplitted.append(freq)
            PSDSplitted.append(PSD)
        self.logger.info('****************************************')

        return freqSplitted, PSDSplitted

    def toSyyp(self, window_selected, overlap, reduction, re_sample, cut_signal):
        '''
        This function must be changed before use it, it has not been specify for this version
        '''
        
        # re_sample must be a number of power in base 2: example 2,4,8,16,32...
        # cut_signal is the number of data that is going to be studied: example 170000
        
        dt = self.time[1]-self.time[0]
        self.cut_signal = min(cut_signal,self.data.shape[0])
        self.data = self.data[0:self.cut_signal:re_sample]
        self.cut_signal = cut_signal
        self.LDATA=np.int(window_selected)
        self.OV=overlap
        self.beta = reduction/(window_selected*dt) 
        self.re_sample = re_sample
        self.data_length = self.data.shape[0]
        
        # BLOCKS
        BLOCKS=np.arange(0,self.data_length-self.LDATA,round(self.LDATA*(100-self.OV)/100))
        BLOCKS=np.hstack((BLOCKS,self.data_length-self.LDATA))
        BLOCKS_length=BLOCKS.shape[0]
        
        #w_exp
        w_exp_linspace=np.linspace(0,int(self.LDATA/2),int(self.LDATA/2))
        w_exp=np.exp(-self.beta*(1/self.sampleRate)*w_exp_linspace[:])
        
        # Hanging symetric window
        w=np.hanning(self.LDATA/self.re_sample)
        #temp=np.zeros((int(self.LDATA/self.re_sample),BLOCKS_length))*1j

        temp=np.zeros((int(self.LDATA/re_sample),BLOCKS_length))
        FFT_block=np.zeros((self.LDATA,BLOCKS_length),dtype=np.complex128)
        kk_block=np.zeros((self.LDATA,BLOCKS_length),dtype=np.complex128)
        kk2_block=np.zeros((self.LDATA,BLOCKS_length),dtype=np.complex128)
        CORR_block = np.zeros((int(self.LDATA/2),BLOCKS_length),dtype=np.complex128)
        fft_CORR=np.zeros((int(self.LDATA/2),BLOCKS_length),dtype=np.complex128)
        syy_plus=np.zeros((int(self.LDATA/2),1),dtype=np.complex128)
        for b in range(0,BLOCKS_length):
            
            init=int(BLOCKS[b])
            final=int(BLOCKS[b]+self.LDATA)

            #tmep
            
            temp[:,b]=self.data[init:final:self.re_sample]-np.mean(self.data[init:final:self.re_sample])
            temp[:,b]=w*temp[:,b]
            
            #FFT    
            FFT_block[:,b]=np.fft.fft(temp[:,b],self.LDATA)
            kk_block[:,b]=np.conj(FFT_block[:,b])*FFT_block[:,b]
            kk2_block[:,b]=np.fft.ifft(kk_block[:,b])/self.LDATA

            # To only keep the positive lags         
            CORR_block[:,b]=kk2_block[:int(self.LDATA/2),b]    

            fft_CORR[:,b]=np.fft.fft(CORR_block[:,b]*w_exp[:],int(self.LDATA/2))
            syy_plus[:,0]=syy_plus[:,0]+fft_CORR[:,b]
            
        self.syy_plus=syy_plus/BLOCKS_length
        self.freq_syy_plus=np.fft.fftfreq(int(self.LDATA/2),d=1./self.sampleRate)
        self.syy_plus=self.syy_plus[self.freq_syy_plus>=0.]
        self.freq_syy_plus=self.freq_syy_plus[self.freq_syy_plus>=0.]
        
        return self.syy_plus, self.freq_syy_plus




