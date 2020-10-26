# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 08:56:47 2020

@author: Pedro Marlo
"""
import pandas as pd
import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import copy
from scipy import signal


#    import itertools

#def grouper(n, iterable, fillvalue=None):
#    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
#    args = [iter(iterable)] * n
#    return itertools.zip_longest(*args, fillvalue=fillvalue)
#
#
#cols = list(grouper(2, range(86)))
#usefulcols = []
#grpcols = []
#
#for p, v in enumerate(cols):
#    if p % 2 == 0:
#        usefulcols.extend(v)
#        grpcols.append(v)


class TxtFileData():

    # Class variables--Common to all files
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    txt_dir = os.path.join(parent_dir, "txt")
    csv_dir = os.path.join(parent_dir, "csv")
    csv_flight_dir = os.path.join(csv_dir, "Flights")
    csv_sensor_dir = os.path.join(csv_dir, "Sensor List")
    fig_dir = os.path.join(parent_dir, "figures")

    def __init__(self, filename):
        #        instance variables-- particular to each object
        self.filename = filename
        # self.excelfile = excelfile
        self.csv_file = self.filename.replace('.txt', '.csv')
        self.csv_flight_path = os.path.join(self.csv_flight_dir, self.csv_file)
        self._csv = self.check4csv()

    def check4csv(self):
        if os.path.isfile(self.csv_flight_path):
            # print("{} exists, call CSV_2_DF for speed".format(self.csv_file))
            return True
        else:
            print("{} does not exist, reading {}".format(self.csv_file,
                                                         self.filename))
            print("it can take a bit")
            return False

    def get_txt_info(self, num_lines=50, print_end=False):
        if not self._csv:
            # print("has entrado a get_txt_info")
            with open(os.path.join(self.txt_dir, self.filename)) as my_file:
                self.my_info = my_file.readlines()
                self.sampleRate = self.my_info[34].split("Sample frequency\t")[0]
#            print("has leido  el archivo bien")

            if print_end:
                # check how many endlines have irregularities
                for i in range(num_lines):
                    print(self.my_info[-i])
                    print('*****\n')
            return self.my_info
        else:
            print("there is a csv file, use the CSV_2_DF method")

    def txt2sensors(self):
#        checks that get_txt_info was instantiated

        if self.my_info:
            self.sensor_list = []
            self.sensors ={}
    #    sensors primary ID  in line 5
            for elem, line in enumerate(self.my_info[5].split('PRIMARY ID\t')[0:]):
                if elem==0:
                    continue              
                Y_axis = self.my_info[38].split('Y axis unit\t')[elem]
                if Y_axis.startswith('g'):
                    temp = 'g'
                elif Y_axis.startswith('N'):
                    temp = 'N'
                elif Y_axis.startswith('U'):
                    temp = 'mm/m'
                sensor = line.replace('\t\t\t', '').replace('\n','')+temp
                # First create an empty list for every sensor
                self.sensor_list.append(sensor)
                self.sensors[sensor] = []
            return  self.sensor_list
        else:
            print("instantiate ""get_txt_info"" first")


    def txt2DF(self, start_row=39,rows2delete=100 ):
        if self.sensor_list:
#        checks that txt2sensors was instantiated
            time = []
            measurement = []
            self.dataInitial= pd.DataFrame()
            del self.my_info[-rows2delete:]
            #Then reads the
            for line in self.my_info[start_row:]:
                for tupla in line.split('\t\t\t'):
                    try:
                        acc = float(tupla.lstrip('\t').rstrip('\n').split('\t')[1])
                        measurement.append(acc)
                        t = tupla.lstrip('\t').rstrip('\t').split('\t')[0]
                    except IndexError:
                        pass
                time.append(t)
                
                
                for pos, sensor in enumerate(self.sensor_list):
                    try:
                        self.sensors[sensor].append(measurement[pos])
                    except:
                        pass
                measurement = []
#                

            self.dataInitial = pd.DataFrame(self.sensors)
            self.dataInitial['time'] = np.asarray(time)

#            print("has creado el DF")

            try:
                flightFolder = os.path.join(self.csv_dir,"Flights")
                os.makedirs(flightFolder)
            except FileExistsError:
                pass
            print("writing {} file".format(self.csv_file))
            self.dataInitial.to_csv(os.path.join(flightFolder,self.csv_file))
            return self.dataInitial
    
    
        else:
            print("instantiate ""txt2sensors"" first")

    
    def sensors2csv(self,foldername="Sensor List"):
#        print("has entrado a sensors2csv")
        try:
            foldername = os.path.join(self.csv_dir,foldername)
            os.makedirs(foldername)
        except:
            pass
        with open(os.path.join(foldername, self.csv_file), "w", newline="") as f:
            writer = csv.writer(f, delimiter=' ')
            for item in self.sensor_list:
                writer.writerow(item)

    def DF2csv(self):
        #        print("has entrado a DF2csv")
        try:
            flightFolder = os.path.join(self.parent_dir, "csv", "parameters")
            os.makedirs(flightFolder)
        except FileExistsError:
            pass
        self.dataInitial.to_csv(os.pathg.join(flightFolder, self.csv_file))

    def CSV_2_DF(self):
        if self._csv:
            print("importing {}".format(self.csv_file))
            self.dataInitial = pd.read_csv(self.csv_flight_path, index_col=0, na_filter=False)
            self.sampleRate = 1/(self.dataInitial["time"][1]-self.dataInitial["time"][0])
            self.sensor_list = list(self.dataInitial.columns)
            self.sensor_list.pop()
            
            return self.dataInitial
        else:
            return None

    def plot_raw_signals(self, flight="Original"):
        sensors = list(self.dataInitial.columns)
        sensors.remove("time")
        try:
            os.makedirs(os.path.join(self.fig_dir, "{}".format(flight)))
        except FileExistsError:
            pass

        for sensor in sensors:
            plt.figure()
            plt.plot(self.dataInitial["time"], self.dataInitial[sensor])
            plt.xlabel("time[s]")
            plt.ylabel(sensor.split("--")[1])
            plt.title(sensor.split("--")[0])
            try:
                plt.savefig(os.path.join(self.fig_dir, flight, sensor))
            except FileNotFoundError:
                sensor_rpl = sensor.replace("/", "%")
                plt.savefig(os.path.join(self.fig_dir, flight, sensor_rpl))
#            plt.show()
            plt.close()





#    def get_RAI_RAO_Excel(self, excelfile, sheet, speed):
#
#        my_file = pd.read_excel(excelfile, sheet, skiprows=2,
#                                usecols=["Kts", "npoints", "RAI", "RAO"])
#
#        my_time = my_file[my_file["Kts"] == speed]
#
## posible tener que eliminar si los pts RAI/RAO no cuadran al plotear
#        Rai = []
#        Rao = []
#        for pos, points in enumerate(my_time["npoints"]):
#            Rai += int(round(points))*[my_time["RAI"][pos]]
#            Rao += int(round(points))*[my_time["RAO"][pos]]
#
#        self.dataInitial["RAI"] = pd.Series(Rai)
#        self.dataInitial["RAO"] = pd.Series(Rao)
#       rai_rao = pd.Series(list(zip(Rai, Rao)))
#        self.dataInitial["RAI/RAO"] = pd.Series(list(zip(Rai, Rao)))
#        self.dataInitial = self.dataInitial.dropna()
#
#        return rai_rao
    
    def moving_average(self,  overlap, stepSize, sps=1024, sensor= "50215101--N"):
        '''
        Calculate moving average, taking as input overlap (%) and step (S)
        '''
        self.timeInitial = self.dataInitial["time"]

        # stepSize: number of elements that are going to be used every step
        stepSize = int(sps * stepSize)
        # overlapSize: number of elements that are going to be used every step
        overlapSize = int(stepSize * overlap * 0.01)

        # To avoid problems when changing value of stepSize in Main Window
        if stepSize == 0:
            moveMean = copy.deepcopy(self.dataInitial)
        else:
            # Moving average
            moveMean = [np.mean(self.dataInitial[sensor][i:i + stepSize]) for i in range(0, self.dataInitial.shape[0], stepSize - overlapSize)]
            moveMean = np.asarray(moveMean)
            # Time with the shape of moveMean
            timeMoveMean = np.linspace(self.timeInitial.values[0], self.timeInitial.values[-1], moveMean.shape[0])

            # Interpolating to have the same shape that global time and data
            f1 = interp1d(timeMoveMean, moveMean, kind='cubic')
            time = np.linspace(self.timeInitial.values[0], self.timeInitial.values[-1], self.timeInitial.shape[0])
            moveMean = f1(time)

        return moveMean
    
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
        timeMoveRMS = np.linspace(self.timeInitial.values[0], self.timeInitial.values[-1], moveRMS.shape[0])
    
        # Changing shape of moveRMS and timeMoveRMS to global shape of data and time
        f1 = interp1d(timeMoveRMS, moveRMS, kind='cubic')
        time = np.linspace(self.timeInitial.values[0], self.timeInitial.values[-1], self.timeInitial.shape[0])
        moveRMS = f1(time)
        return moveRMS
    
    
    
    def get_transitory(self):
        pass
'''#########################################################################
   ******************************** MAIN ***********************************
   #########################################################################'''

if __name__ == "__main__":

    flight_list = ["V836_250Kts.txt"]

#    flight_list = ["V835_240Kts.txt", "V835_300Kts.txt",
#                   "V835_340Kts.txt", "V836_300Kts.txt", "V836_250Kts.txt"]
#    try:
#        if "Full_DF" in locals():
#            if len(Full_DF)==len(flight_list):
#                print("no need to run the program")
#    except NameError:
    Object_collector = {}
    Full_DF = {}

    for flight in flight_list:
        Object_collector[flight] = TxtFileData(flight)
        if Object_collector[flight]._csv:
            Full_DF[flight] = Object_collector[flight].CSV_2_DF()
            SensorList = Object_collector[flight].sensor_list

        else:
            Object_collector[flight].get_txt_info()
            SensorList = Object_collector[flight].txt2sensors()
            Object_collector[flight].sensors2csv()
            Full_DF[flight] = Object_collector[flight].txt2DF()
#        Object_collector[flight].plot_raw_signals(flight.replace(".txt", ""))


#        for sensor in Object_collector[flight].sensor_list:


time=5
movingAvg = Object_collector[flight].moving_average(1,time)
dataDetrended = Full_DF[flight]["50215101--N"]-movingAvg
rmse =  Object_collector[flight].movingRMS(1,time)

tol=0.005
TFvalues = []
delta=time*1024
true_count=0
false_count=0
exception = 0

a1 = movingAvg[:-1]
a2 = movingAvg[1:]
b = a1-a2
#
def check_RMSE(pos):
    pass

for pos, val in enumerate(movingAvg):
    try:
        if (true_count<(6*delta) and false_count<(6*delta)):
            
            if abs((val-movingAvg[pos+delta])/delta)<tol:
        #        st_time.append(Full_DF[flight]["time"][pos])
        #        st_pos.append(pos)
                TFvalues.append(True)
                true_count += 1
                false_count = 0
    
                
            else:
        #        tr_time.append(Full_DF[flight]["time"][pos])
        #        tr_pos.append(pos)
                TFvalues.append(False)
                false_count += 1
                true_count = 0
        else:
            TFvalues.append(-0.5)
            true_count = 0
            false_count = 0
                
    except (IndexError, KeyError):
        exception +=1
        pass
    
plt.close()

#plt.plot(Full_DF[flight]["time"][:-1],values)
#plt.plot(Full_DF[flight]["time"][:-1],Full_DF[flight]["50215101--N"][:-1])

#plt.subplot(223)
plt.plot(Full_DF[flight]["time"],Full_DF[flight]["50215101--N"])

#plt.subplot(221)
plt.plot(Full_DF[flight]["time"],movingAvg)


plt.figure()
#plt.subplot(222)
if exception == 0:
    
    plt.plot(Full_DF[flight]["time"][:-1],TFvalues)
else:
    plt.plot(Full_DF[flight]["time"][:-exception],TFvalues)

#plt.subplot(223)
#plt.plot(Full_DF[flight]["time"],dataDetrended)        
#












####attempt to get sections with moving average and increment (no detrend)

#plt.close()
#a = Object_collector[flight].moving_average(2,18)
#a1 = a[:-1]
#a2 = a[1:]
#b = a1-a2
#
#tol=0.003
#values = []
#
#for pos, dif in enumerate(b):
#    if abs(dif)<tol:
##        st_time.append(Full_DF[flight]["time"][pos])
##        st_pos.append(pos)
#        values.append(True)
#    else:
##        tr_time.append(Full_DF[flight]["time"][pos])
##        tr_pos.append(pos)
#        values.append(False) 
##
##plt.plot(Full_DF[flight]["time"][:-1],values)
##plt.plot(Full_DF[flight]["time"][:-1],Full_DF[flight]["50215101--N"][:-1])
#plt.subplot(311)
#plt.plot(Full_DF[flight]["time"][:-1],b)
#
#plt.subplot(312)
#plt.plot(Full_DF[flight]["time"][:-1],values)
#
#plt.subplot(313)
#plt.plot(Full_DF[flight]["time"][:-1],Full_DF[flight]["50215101--N"][:-1])









#########        Routine to get the RAI RAO values form excel           ########

#        my_times[flight] = Object_collector[flight].get_RAI_RAO_Excel(
#                            excelfile,
#                            flight.split("_")[0],
#                            flight.split("_")[1].replace(".txt", '').lower())
#
#

#
#    RaiRao = my_times[flight]['RAI/RAO'].unique()
#    counter = 0
#    x = []
#    y = []
#    plt.figure()
#    plt.xlabel("time[ms]")
#    plt.ylabel("50215101--N")
#    for rai_rao in RaiRao:
#        x = []
#        y = []
#        try:
#            while my_times[flight]['RAI/RAO'][counter] == rai_rao:
#
#                x.append(my_times[flight]["time"][counter])
#                y.append(my_times[flight]["50215101--N"][counter])
#                counter += 1
#
#        except KeyError:
#            pass
#
#        plt.plot(x, y)
##        plt.legend(list(rai_rao))
#
#    new_dir = os.path.join(r"Z:\aie_load\A380\A380CEO\DOSSIERS\NACA_INTAKE\FTR2\FT_results\V835&836\figures\V836_250Kts", "50215101--N")
#    try:
#        os.makedirs(new_dir)
#    except FileExistsError:
#        pass
#    plt.savefig(os.path.join(new_dir, "cortes.png"))
#    plt.show()
#    plt.close()


