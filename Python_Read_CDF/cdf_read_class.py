# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 16:17:44 2019

@author: juan.torresescolano
"""

import cdflib
import numpy as np
import logging
import copy
import os

class CdfFileData():
    def __init__(self,filePath, sensorKeyList, boolReadUnits = False):

        logger = logging.getLogger('__main__')
        
        #### Path of the file.
        self.filePath = filePath
        index = self.filePath.rfind(os.path.sep)
        self.fileName  = self.filePath[index+1:]


        #### List with all the sensors of the CDF. If sensorKeyList == 'all', all sensors will be saved, else: specific sensors
        if sensorKeyList == 'all':
            self.sensorNamesList = cdflib.CDF(self.filePath).cdf_info().get('zVariables')
        else:
            self.sensorNamesList = []
            for sensorName in sensorKeyList:
                if sensorName in cdflib.CDF(self.filePath).cdf_info().get('zVariables'):
                    self.sensorNamesList.append(sensorName)
                else:
                    logger.info('Sensor {} not found in the CDF {}'.format(sensorName, self.fileName))


        if boolReadUnits:
            #### Saving units in a dictionary
            self.units = {}
            self.fullName = {}
            logger.info('Reading {} sensors of {}'.format(len(self.sensorNamesList), self.fileName))
            for sensorName in self.sensorNamesList:
                if sensorName != 'GMT':
                    try:
                        self.units[sensorName] = cdflib.CDF(self.filePath).varattsget(sensorName)['UNIT']
                    except:
                        self.units[sensorName] = ''
                    try:
                        self.fullName[sensorName] = cdflib.CDF(self.filePath).varattsget(sensorName)['EG_NAME']
                    except:
                        self.fullName[sensorName] = ''
                else:
                    self.units['GMT'] = 's'
                    self.fullName['GMT'] = 'Time'
        else:
            self.units = {}
            self.fullName = {}
            for sensorName in self.sensorNamesList:
                self.fullName[sensorName] = ''
                self.units[sensorName] = ''


        #### List with all the times.
        self.time = []
        self.time_year = []

        ### Reading time value
        GMT = cdflib.CDF(self.filePath).varget('GMT')
        ### Changing numpy array to 1D array
        GMT = GMT.ravel()
        ### Last wrong values are -1, deleting them
        indexToDelete = np.where(GMT.astype(int) == -1)
        GMT = np.delete(GMT, indexToDelete)
        ### Creating attributes of time
        self.time_year = GMT
        self.time = GMT-self.time_year[0]
        ### self.timeInitial is an attribute in which range of initial time is copied. It will be always the same
        self.timeInitial = copy.deepcopy(self.time)
        
        #### Value of the shample rate
        time = self.time[~np.isnan(self.time)]
        self.sampleRate = int(1/(time[1]-time[0]))
        
        #### List with all the data of every sensor. Organized by columns.
        self.data = []
        self.dataInitial = []
        n = 0
        # All sensors are going to be read
        totalSensorCount = len(self.sensorNamesList)
        # Var to print some percentages, not every step.
        percentageToPrint = 0

        for sensorName in self.sensorNamesList:
            n += 1
            percentage = n/totalSensorCount*100
            if (percentage >= percentageToPrint) or (percentage>= 99):
                logger.info('{:.2f} % completed.'.format(percentage))
                percentageToPrint += 3
            else:
                pass
            # Returns raw data of the variable
            raw_data = cdflib.CDF(self.filePath).varget(sensorName)
            # Deleting elements that were not correct in GMT var
            raw_data = raw_data.ravel()
            raw_data = np.delete(raw_data, indexToDelete)
            # Appending every array in attribute data
            self.data.append(raw_data)
            self.dataInitial.append(raw_data)


    def CDFpos(self,sensor_name):
        '''
        Due to the fact that self.data is a list of lists, it does not have any key to call the sensors, so this method
        returns the position of an specific value.
        '''
        self.cdfpos = self.sensorNamesList.index(sensor_name)
        return self.cdfpos
