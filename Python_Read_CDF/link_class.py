from cdf_read_class import CdfFileData
from sensor_class import Sensor
from scipy.spatial import ConvexHull
import copy
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.interpolate import interp1d
import logging
import os

class TestFlight():
    '''
    The main function of this class is to create the relation between the user interface and classes Sensor and CdfFileData
    '''
    def __init__(self,kwargs):
        '''
        Dictionary with the name of the files as key and class CdfFileData as value
        '''
        self.nameFiles = {}
        '''
        Dictionary with the key of the sensors as keys and list of [full name, units, CDF pos index] as value.
        '''
        self.parameters = {}
        '''
        Dicionary with the sensor's key as a key and the class Sensor as value
        '''
        self.sensor = {}

        i = 0
        '''
        kwargs has the following var:
        dictFiles = {}
        dictFiles['nameFiles'] = self.nameCDFList       -> List with name of the CDFs
        dictFiles['pathFiles'] = self.pathFiles         -> List with the paths of the CDFs
        dictFiles['sensorToReadList'] = parameterKey    - > 'all' string or list of the parameter's key
        dictFiles['boolReadUnits'] = boolReadUnits      -> bool to read units and full name in CDF
        '''
        for file_name in kwargs.get('nameFiles'):
            # path_doc -> global path of the CDF
            path_doc = kwargs.get('pathFiles')[i]
            path_doc = '{}{}{}'.format(path_doc,os.path.sep,file_name)

            self.nameFiles[file_name] = copy.deepcopy(CdfFileData(path_doc,
                                                      sensorKeyList = kwargs.get('sensorToReadList'),
                                                      boolReadUnits = kwargs.get('boolReadUnits')))
            path_doc = kwargs.get('pathFiles')[i]
            i +=1

        # A dicctionary with all the sensors names and their data is kept.
        for fileName in self.nameFiles.keys():
            sensor_aux = {}
            for sensorName in self.nameFiles[fileName].sensorNamesList:
                sensor_aux[sensorName] = Sensor(self.nameFiles[fileName],sensorName)
            self.sensor[fileName] = sensor_aux
        self.mask = np.ones((self.nameFiles.get(list(self.nameFiles.keys())[0]).time.shape[0]))

        for fileName in self.nameFiles.keys():
            dictAux = {}
            for sensorName in self.nameFiles[fileName].sensorNamesList:
                cdfPos = self.nameFiles[fileName].CDFpos(sensorName)
                units = self.sensor[fileName][sensorName].units
                fullName = self.sensor[fileName][sensorName].fullName
                dictAux[sensorName] = [fullName,units,cdfPos]

            self.parameters[fileName] = dictAux

    def RMS_loads(self, file_name, sensor_name,overlap, stepSize):
        '''
        Reading initial data and time, so no np.nan in the values
        '''
        data = self.sensor[file_name].get(sensor_name).dataInitial
        time = self.sensor[file_name].get(sensor_name).timeInitial

        #Zero crossing frequency
        dataDetrend = self.sensor[file_name][sensor_name].detrend(overlap,stepSize)
        timeDetrend = np.linspace(time[0],time[-1], dataDetrend.shape[0])

        # Root Mean Square -> It has been used data detrended instead
        # of raw data because Airbus has asked for it.
        RMS = np.sqrt(np.mean(np.power(dataDetrend, 2)))

        zeroCrossing=((dataDetrend[:-1]*dataDetrend[1:])<0).sum()
        if zeroCrossing != 0:
            zeroPosition = []
            for i in range(0,dataDetrend.shape[0]-1):
                if (dataDetrend[i]<0 and dataDetrend[i+1]>0) or (dataDetrend[i]>0 and dataDetrend[i+1]<0):
                    zeroPosition.append(i)
                else:
                    pass

            if np.absolute(timeDetrend[zeroPosition[-1]]-timeDetrend[zeroPosition[0]]) < 10**-4:
                N0 = np.inf
            else:
                N0 = (zeroCrossing)/(timeDetrend[zeroPosition[-1]]-timeDetrend[zeroPosition[0]])
            N0 = "{0:.4f}".format(N0)
        else:
            N0 = 0

        return RMS, N0

    
    def corr_loads(self):
        # For every sensor, its maximum value is searched among all the CDF files and all the information of this time
        # is kept. Everything is kept with dictionaries.

        corr_loads_dict = {}
        corr_loads_dict_aux = {}
        for file_name in self.nameFiles.keys():
            corr_loads_dict[file_name] = {}
            for sensor_name in self.sensor[file_name].keys():
                corr_loads_dict[file_name][sensor_name]= {}
                max_value_index = np.where(self.sensor[file_name][sensor_name].data == np.amax(self.sensor[file_name][sensor_name].data))[0][0]

                for i in  self.sensor[file_name].keys():
                    corr_loads_dict[file_name][sensor_name][i]= self.sensor[file_name][i].data[max_value_index]
        return corr_loads_dict
            
        
    def convex_hull(self,file_name1,sensor_name1,file_name2, sensor_name2):
        logger = logging.getLogger('__main__')

        # All data must have the same shape
        dataSensor1 = self.sensor[file_name1][sensor_name1].dataInitial
        time1 = self.sensor[file_name1][sensor_name1].timeInitial
        dataSensor2 = self.sensor[file_name2][sensor_name2].dataInitial
        time2 = self.sensor[file_name2][sensor_name2].timeInitial
        shapeConvex = dataSensor1.shape[0]
        if dataSensor1.shape[0] != dataSensor2.shape[0]:
            logger.info('Different length of the sensors that are going to be plotted. A cubic interpolation'
                  'is going to be done so that both of them have the shame length.')
            shapeConvex = max(dataSensor1.shape[0], dataSensor2.shape[0])
            f1 = interp1d(time1, dataSensor1, kind='cubic')
            f2 = interp1d(time2, dataSensor2, kind='cubic')
            time1 = np.linspace(time1[0], time1[-1], shapeConvex)
            time2 = np.linspace(time2[0], time2[-1], shapeConvex)
            dataSensor1 = f1(time1)
            dataSensor2 = f2(time2)

        points = np.ones((shapeConvex,2))
        for i in range(shapeConvex):
            points[i,0] = dataSensor1[i]
            points[i,1] = dataSensor2[i]

        hull = ConvexHull(points)

        #Bigger and shorter axis
        small_latwise = np.min(points[points[:,0]==np.min(points[:,0])],0)
        small_lonwise = np.min(points[points[:,1]==np.min(points[:,1])],0)
        big_latwise = np.max(points[points[:, 0] == np.max(points[:, 0])], 0)
        big_lonwise = np.max(points[points[:, 1] == np.max(points[:, 1])], 0)

        distance_lat = euclidean(big_latwise, small_latwise)
        distance_lon = euclidean(big_lonwise, small_lonwise)

        if distance_lat >= distance_lon:
            major_axis_length = distance_lat
            minor_axis_length = distance_lon
        else:
            major_axis_length = distance_lon
            minor_axis_length = distance_lat

        return hull, points, major_axis_length,minor_axis_length,small_lonwise,big_lonwise,small_latwise,big_latwise