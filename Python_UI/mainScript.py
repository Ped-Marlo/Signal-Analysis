##############################################
##              Python Libraries
##############################################
import sys
import os

# Appending directory Python_Read_CDF to sys.path.
PYFATpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,'{}{}{}'.format(PYFATpath,os.path.sep,'Python_Read_CDF' ))

# Appending directories with all modules that are going to be used from Python.
PYTHONpath1 = r'Z:\Software\General\Python\Python373'
PYTHONpath2 = r'Z:\Software\General\Python\Python373\Library\bin'
PYTHONpath3 = r'Z:\Software\General\Python\Python373\Scripts'
PYTHONpath4 = r'Z:\Software\General\Python\Python373\lib\site-packages'

sys.path.insert(0,PYTHONpath1)
sys.path.insert(0,PYTHONpath2)
sys.path.insert(0,PYTHONpath3)
sys.path.insert(0,PYTHONpath4)

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
import copy
from scipy.spatial.distance import euclidean
from scipy import signal
from sklearn.decomposition import PCA
from itertools import zip_longest
from datetime import datetime
# Importing modules that are going to be use of PyQt5
import PyQt5
import logging


##############################################
##              Own Libraries
##############################################
# Importing Main Window - User Interface (created with QtDesigner)
from mainWindow import Ui_MainWindow
# Importing all modules of sensor_class
from sensor_class import Sensor
# Importing all modules of link_class
from link_class import TestFlight
# Importing modules of plotWidget
from plotWidget import MplWidget
# Importing search CDF window class
from searchCDFWindowClass import searchCDFWindow
# Importing reference window class
from referenceWindowClass import referenceWindow

class MainWindow(PyQt5.QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        '''
        ################################################################################################################
        ################################################################################################################
        
                                                        MAIN WINDOW
        
        ################################################################################################################
        ################################################################################################################
        
        '''

        '''
        ######################################
                Signals of Main Window
        ######################################
        '''
        #self.showMaximized()
        # Searching directory and reading data
        self.buttonSearchDirectory.clicked.connect(self.searchDirectory)
        self.buttonApplyDirectory.clicked.connect(self.applyDirectory)
        self.buttonApplyDirectoryTXT.clicked.connect(self.applyDirectoryTXT)
        # Changing CDF file selected
        self.fileSelect.itemSelectionChanged.connect(self.fileSelected)
        # Conditional Selection of Data
        self.condSel.cellClicked.connect(self.condSel_single_click)
        self.condSel.cellChanged.connect(self.condSel_cell_changed)
        self.condSelParList.itemClicked.connect(self.condSelParList_single_click)
        # Resample
        self.buttonResample.clicked.connect(self.resample)
        # Filter
        self.buttonFilterFreq.clicked.connect(self.filterFreq)
        # Clear all
        self.buttonClearAll.clicked.connect(self.clearAll)
        # Conditional
        self.buttonConditional.clicked.connect(self.conditionalPlot)
        self.buttonClearSelection.clicked.connect(self.clearConditional)
        self.buttonClearSelection.clicked.connect(self.checkPlotMain)
        # Import-Export-currentView CSV
        self.buttonReadCondCSV.clicked.connect(self.readConditionalCSV)
        self.buttonWriteCondCSV.clicked.connect(self.writeConditionalCSV)

        # Change subset of parameter selection
        self.buttonChangeParameters.clicked.connect(self.changeParameterSelection)
        # Unselecting parameters
        self.buttonUnselParameters.clicked.connect(self.unselectParameterSelection)
        self.buttonResetParameters.clicked.connect(self.resetParametersSelection)
        self.buttonDeleteReference.clicked.connect(self.deleteReference)
        # TabWidget
        self.tabWidget.currentChanged.connect(self.selectTabBarIndex)
        # Export all data
        self.buttonExportAllData.clicked.connect(self.exportAllData)
        # Signal when changing element of paramSel QListWidget
        self.paramSel.itemSelectionChanged.connect(self.checkPlotMain)
        # Signal when changing check of QRadioButton
        self.checkCompleteSignalMain.clicked.connect(self.plotCompleteSignalMainWindow)
        self.checkSteadySignalMain.clicked.connect(self.plotSteadySignalMainWindow)
        self.checkVibrationsMain.clicked.connect(self.plotVibrationsMainWindow)
        self.checkAllSignalsMain.clicked.connect(self.plotAllSignalsMainWindow)
        self.checkDisplacement.clicked.connect(self.plotDisplacementMainWindow)
        self.checkMovingRMS.clicked.connect(self.plotMovingRMSMainWindow)
        self.buttonApplyAllSignals.clicked.connect(self.plotAllSignalsMainWindow)
        self.checkAxesYesMain.clicked.connect(self.checkPlotMain)
        self.checkAxesNoMain.clicked.connect(self.checkPlotMain)
        self.checkKeyAxisName.clicked.connect(self.checkPlotMain)
        self.checkNameAxisName.clicked.connect(self.checkPlotMain)
        # Signal when changing step or overlap texts
        self.buttonApplyStepMain.clicked.connect(self.checkPlotMain)
        # Applying reference to all CDFs
        self.buttonSelectReference.clicked.connect(self.referenceWindow)
        # Exporting all plots
        self.buttonExportAllPlots.clicked.connect(self.exportAllPlots)
        # Creating new sensor with data plotted
        self.buttonCreateSensorCond.clicked.connect(self.createSensorCond)
        # Clearing created sensors
        self.buttonDeleteSensorCond.clicked.connect(self.deleteCreatedSensors)
        # Apply different filter for displacements
        self.buttonApplyFilterDisp.clicked.connect(self.checkPlotMain)
        # Select ranges dynamically
        self.buttonSelectTimeDyn.clicked.connect(self.selectRangeDynamically)
        # Apply range of time
        self.buttonApplyRangeTime.clicked.connect(self.applyRangeTime)
        # Select ranges manually
        self.buttonSelectTimeMan.clicked.connect(self.selectManRangeTime)
        self.buttonCurrentView.clicked.connect(self.currentView)


        '''
        ######################################
            Attributes of Main Window
        ######################################
        '''
        # Conditional Selection of Data
        self.groupCondSel.setHidden(True)
        self.filterDisplacementFrame.setHidden(True)
        self.groupSelectionPlotAll.setHidden(True)
        self.manualSelectTimeFrame.setHidden(True)
        # QTableWidgets properties
        self.paramSel.setHorizontalHeaderLabels(['Key', 'Ref','Units', 'Name'])
        self.listParamTimeAnalysis.setHorizontalHeaderLabels(['Key', 'Ref','Units', 'Name'])
        self.paramListFreq.setHorizontalHeaderLabels(['Key', 'Ref','Units', 'Name'])
        self.listSecParamTimeAnalysis.setHorizontalHeaderLabels(['Key', 'Ref', 'Units', 'Name'])
        self.secondParamListFreq.setHorizontalHeaderLabels(['Key', 'Ref', 'Units', 'Name'])
        self.tableRMS.setHorizontalHeaderLabels(['Sensor', 'RMS', 'N0'])
        self.condSel.setHorizontalHeaderLabels(['Parameter', 'Condition', 'Value'])
        self.selectionPlotAllSignals.setHorizontalHeaderLabels(['Complete','Steady', 'Vibration'])
        self.selectionPlotAllSignals.setVerticalHeaderLabels(['Range 1', 'Range 2', 'Range 3'])
        self.selectionPlotAllSignals.horizontalHeader().setVisible(True)
        self.selectionPlotAllSignals.verticalHeader().setVisible(True)
        self.paramSel.horizontalHeader().setVisible(True)
        self.listParamTimeAnalysis.horizontalHeader().setVisible(True)
        self.paramListFreq.horizontalHeader().setVisible(True)
        self.listSecParamTimeAnalysis.horizontalHeader().setVisible(True)
        self.secondParamListFreq.horizontalHeader().setVisible(True)
        self.tableRMS.horizontalHeader().setVisible(True)
        self.condSel.horizontalHeader().setVisible(True)

        '''
        ################################################################################################################
        ################################################################################################################

                                                TIME ANALYSIS WINDOW

        ################################################################################################################
        ################################################################################################################

        '''

        '''
        ######################################
            Signal of Time Analysis Window
        ######################################
        '''
        # Signal when selection of parameterHullList changes
        self.listSecParamTimeAnalysis.itemClicked.connect(self.printSecondItemRMS)
        # Plotting Convex Hull
        self.buttonConvexHull.clicked.connect(self.plotConvexHull)
        # Plot RMS1
        self.buttonRMS1.clicked.connect(self.plotRMS1)
        # Plot RMS2
        self.buttonRMS2.clicked.connect(self.plotRMS2)
        # Plot Main Axes
        self.buttonMainAxes.clicked.connect(self.plotMainAxes)
        # Clear Time Analysis Window
        self.buttonClearAllTime.clicked.connect(self.timeAnalysis)
        # Export Convex Hull
        self.buttonExportHull.clicked.connect(self.exportConvexHull)
        # Signal when decimals of QSpinBox changes
        self.decimalsRMS.textChanged .connect(self.decimalsChanged)
        # Plotting same graph of Main Window when QRadioButton changes
        self.checkTime.clicked.connect(self.checkPlotTimeAnalysis)
        # Plot Main Axes when QRadioButton changes
        self.checkMainAxis.clicked.connect(self.plotMainAxes)
        # Plot Convex Hull when QRadioButton changes
        self.checkConvexHull.clicked.connect(self.plotConvexHull)
        # Save session
        self.buttonSaveUI.clicked.connect(self.saveSession)
        # Load session
        self.buttonLoadUI.clicked.connect(self.loadSession)

        '''
        ###############################################
            Attributes of Time Analysis Window
        ###############################################
        '''
        self.listSecParamTimeAnalysis.setMouseTracking(True)

        '''
        ################################################################################################################
        ################################################################################################################

                                                FREQUENCY ANALYSIS WINDOW

        ################################################################################################################
        ################################################################################################################

        '''

        '''
        ###############################################
            Signal of Frequency Analysis Window 
        ###############################################
        '''
        # Plot spectogram
        self.buttonSpectogram.clicked.connect(self.plotSpectrogramFreqWindow)
        # Plot PSD
        self.buttonPSD.clicked.connect(self.plotPSD)
        # Plot FFT
        self.buttonPlotFreq.clicked.connect(self.plotFFT)
        # Clear all Frequency Analysis Window
        self.buttonClearAllFreq.clicked.connect(self.clearAllFreq)
        # Export PSD
        self.buttonExportPlotPSD.clicked.connect(self.exportPSD)
        # Export FFT
        self.buttonExportPlotFFT.clicked.connect(self.exportFFT)
        # Signal when secondParamListFreq QTableWidget changes
        self.secondParamListFreq.itemClicked.connect(self.printSecondItemFreq)
        # Plot FFT when QRadioButton FFT sensor changes
        self.FFT1.clicked.connect(self.plotFFT)
        self.FFT2.clicked.connect(self.plotFFT)
        # Plotting FFT when range of FFT QRadioButton changes
        self.range1FFT.clicked.connect(self.plotFFT)
        self.range2FFT.clicked.connect(self.plotFFT)
        self.range3FFT.clicked.connect(self.plotFFT)
        self.range4FFT.clicked.connect(self.plotFFT)
        self.range5FFT.clicked.connect(self.plotFFT)
        self.range6FFT.clicked.connect(self.plotFFT)
        # Apply properties to freq
        self.buttonApplyPropFreq.clicked.connect(self.plotPSD)

        '''
        ###############################################
            Attributes of Frequency Analysis Window 
        ###############################################
        '''
        self.secondParamListFreq.setMouseTracking(True)

        '''
        ################################################################################################################
        ################################################################################################################
            
                                                    MULTIPLE PLOTS ANALYSIS
            
        ################################################################################################################
        ################################################################################################################ 
        '''

        '''
        ###############################################
            Signal of Multiple Plots Analysis
        ###############################################
        '''
        # Plotting plots when QRadioButton changes
        self.checkCompleteSignalMulti.clicked.connect(self.multiPlot)
        self.checkSteadySignalMulti.clicked.connect(self.multiPlot)
        self.checkVibrationsSignalMulti.clicked.connect(self.multiPlot)
        self.checkAllSignalsMulti.clicked.connect(self.multiPlot)
        self.checkPSDMulti.clicked.connect(self.multiPlot)
        self.checkDisplacementsMulti.clicked.connect(self.multiPlot)
        self.checkFollowModeNoMulti.clicked.connect(self.multiPlot)
        self.checkFollowModeYesMulti.clicked.connect(self.multiPlot)
        self.checkSameAxesTrue.clicked.connect(self.multiPlot)
        self.checkSameAxesFalse.clicked.connect(self.multiPlot)

    '''
    ################################################################################################################
    ################################################################################################################

                                                    MAIN WINDOW FUNCTIONS

    ################################################################################################################
    ################################################################################################################

    '''
    def exportAllPlots(self):
        '''
        Export a CSV and a JPG of every selected sensors in paramSel QTableWidget.
        '''
        logger.info('Exporting all selected plots...')
        path = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Export all selected sensors', os.getenv('HOME'))
        if path != '':
            # Saving all the indexes of selected rows. They will be unselected, so that there is no problem when plotting
            indexesParamSel = []
            for index in self.paramSel.selectedIndexes():
                indexesParamSel.append(index)
                sensorItem = self.paramSel.item(index.row(), 0)
                self.paramSel.setItemSelected(sensorItem, False)

            # Loop through all files selected in fileSelect QListWidget.
            for fileName in self.fileSelect.selectedItems():
                # Saving reference number and file name.
                indexSpace = fileName.text().find(' ')
                numberFile = fileName.text()[indexSpace + 3:]
                fileName = fileName.text()[:indexSpace]

                # Creating a new folder (if not exists) to save all plots and CSVs
                try:
                    logger.info('Creating path to save selected plots...')
                    logger.info('Path is:')
                    logger.info('{}{}{}'.format(path,os.path.sep,fileName))
                    os.mkdir('{}{}{}'.format(path,os.path.sep,fileName))
                except Exception as e:
                    logger.info('Directory to save all selected plots already created')
                # self.pathSavePlot -> attribute of Main Window to be able to save the figures of the plots.
                self.pathSavePlot = '{}{}{}'.format(path,os.path.sep,fileName)
                # self.pathSavePlot -> attribute to check if the figure have to be saved when plotting.
                self.savePlot = True
                # Loop through all row indexes from paramSel QTableWidget
                for index in indexesParamSel:
                    # Taking info of row
                    sensorItem = self.paramSel.item(index.row(), 0)
                    sensorName = sensorItem.text()
                    numberFileSensor = self.paramSel.item(index.row(), 1).text()
                    units = self.paramSel.item(index.row(), 2).text()
                    # Checking the source file of the sensor
                    if numberFile == numberFileSensor:
                        logger.info('Saving Sensor {}...'.format(sensorName))
                        # Changing row to selected, so in checkPlotMain() funtion detects what to save
                        self.paramSel.setItemSelected(sensorItem,True)
                        # Saving CSV and JPG
                        self.checkPlotMain()
                        # Changing row to unselected
                        self.paramSel.setItemSelected(sensorItem, False)
                        logger.info('Sensor {} has been saved correctly'.format(sensorName))
                logger.info('All selected plots have been saved in {}'.format(self.pathSavePlot))

        logger.info('Process of saving all plots finished correctly')
        logger.info('****************************************')
        # Changing attribute self.savePlot to its default value
        self.savePlot = False


    def referenceWindow(self):
        '''
        Funtion that opens the windowReference to find the refence of all CDFs
        '''
        logger.info('Looking for reference...')

        # Saving all CDFs that have been loaded to Main Window. They will be needed to open reference Window.
        cdfFiles = []
        for row in range(self.fileSelect.count()):
            cdfFiles.append(self.fileSelect.item(row).text())

        # Opening Reference Window
        dialog = referenceWindow(cdfFiles)
        dialog.exec_()

        # Returning paths of the reference
        referenceFiles = dialog.returnReferenceCDF()
        referenceTXT = dialog.returnReferenceTXT()

        if pd.isnull(referenceTXT):
            logger.info('No txt file used to apply reference.')
        else:
            self.dictReferenceTXT = {}
            logger.info('Applying reference with TXT file...')

            # Loop through all CDFs loaded
            for index in range(self.fileSelect.count()):
                indexSpace = self.fileSelect.item(index).text().find(' ')
                numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
                fileName = self.fileSelect.item(index).text()[:indexSpace]

                logger.info('File: {}...'.format(fileName))
                # Loop through all sensors of every CDF loaded
                countSensorsModified = 0
                for sensorName in self.testFlight.sensor.get(fileName).keys():
                    # If sensor name is in the dictionary referenceTXT, apply reference.
                    if sensorName in referenceTXT.keys():
                        logger.info('Sensor {} modified with value {}'.format(sensorName, referenceTXT[sensorName]))
                        self.dictReferenceTXT[sensorName] = referenceTXT[sensorName]

                        if '-' in  referenceTXT[sensorName]:
                            value = float(referenceTXT[sensorName][1:])
                            self.testFlight.sensor.get(fileName)[sensorName].data -= value
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial -= value
                        elif '/' in referenceTXT[sensorName]:
                            value = float(referenceTXT[sensorName][1:])
                            self.testFlight.sensor.get(fileName)[sensorName].data /= value
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial /= value
                        elif '*' in referenceTXT[sensorName]:
                            value = float(referenceTXT[sensorName][1:])
                            self.testFlight.sensor.get(fileName)[sensorName].data *= value
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial *= value
                        elif '+' in referenceTXT[sensorName]:
                            value = float(referenceTXT[sensorName][1:])
                            self.testFlight.sensor.get(fileName)[sensorName].data += value
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial += value
                        else:
                            value = float(referenceTXT[sensorName])
                            self.testFlight.sensor.get(fileName)[sensorName].data += value
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial += value
                        countSensorsModified += 1
                    else:
                        pass
                logger.info('Total of {} sensors have been modified'.format(countSensorsModified))
            self.test_flights_save = copy.deepcopy(self.testFlight)

        if pd.isnull(referenceFiles):
            logger.info('No CDFs used to apply reference.')
        else:
            logger.info('Modifying with CDF files selected. Mean of every sensors mean is going to be calculated.')
            # dictAux -> save the value of all sensor of every CDF that will be used to reference all CDFs
            dictAux = {}
            # Loop through all files that will be use as reference
            logger.info('CDFs used as reference are:')
            for fileName in referenceFiles:
                logger.info(fileName)
                dictAux[fileName] = {}
                # Loop throug all its sensors
                for sensorName in self.testFlight.sensor.get(fileName).keys():
                    # Saving time and data
                    y = copy.deepcopy(self.testFlight.sensor.get(fileName)[sensorName].data)
                    dictAux[fileName][sensorName] = y

            # Calculating the average of every sensor among all CDF files.
            self.dictReference = {}
            for index in range(len(referenceFiles)):
                for sensorName in self.testFlight.sensor.get(referenceFiles[index]).keys():
                    if sensorName == 'GMT':
                        pass
                    else:
                        if sensorName not in self.dictReference.keys():
                            self.dictReference[sensorName] = np.mean(dictAux[referenceFiles[0]][sensorName])/len(referenceFiles)
                        else:
                            self.dictReference[sensorName] += np.mean(dictAux[referenceFiles[0]][sensorName])/len(referenceFiles)

            # Applying calculated reference
            for index in range(self.fileSelect.count()):
                indexSpace = self.fileSelect.item(index).text().find(' ')
                numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
                fileName = self.fileSelect.item(index).text()[:indexSpace]
                logger.info('File: {}...'.format(fileName))
                # If a CDF file has been used to calculate reference, do not apply it
                if fileName in referenceFiles:
                    pass
                else:
                    for sensorName in self.testFlight.sensor.get(fileName).keys():
                        if sensorName in self.dictReference.keys():
                            valueReference = self.dictReference[sensorName]
                            logger.info('Sensor {} modified. Values used is: {:.4f}'.format(sensorName, valueReference))
                            self.testFlight.sensor.get(fileName)[sensorName].data -= valueReference
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial -= valueReference
                        else:
                            logger.info('Sensor {} was not found in referenced CDF.'.format(sensorName))

            logger.info('Reference applied correctly. If user want to delete it, please click button Delete Reference')
            # This reference will be applied always, unless user click on buttonDeleteReference.
            self.test_flights_save = copy.deepcopy(self.testFlight)

        # Plotting after having applied reference
        self.checkPlotMain()
        logger.info('****************************************')

    def searchDirectory(self):
        logger.info('Searching CDFs...')

        # Executing Search CDF Window
        dialog = searchCDFWindow()
        dialog.exec_()

        # Saving all paths added to QListWidget in Search CDF Window
        pathList = dialog.listPathCDF

        # Checking if same sample rate has to be applied to all sensors.
        self.boolSameSampleRate = dialog.boolSameSampleRate
        self.boolReadunits = dialog.boolReadUnits

        # pathUniqueValues: delete duplicated directories to write in fileSelectDirectory QListWidget the others
        pathUniqueValues = []

        # Vars that are going to be used to read all CDFs
        # self.nameCDFList: name of the CDF
        self.nameCDFList = []
        # self.pathFiles: path of the directory where every CDF is located
        self.pathFiles = []

        # Appending vars
        for path in pathList:
            indexPathName = path.rfind(os.path.sep)
            nameCDF = path[indexPathName+1:]
            pathDirectory = path[:indexPathName]

            pathUniqueValues.append(pathDirectory)
            self.nameCDFList.append(nameCDF)
            self.pathFiles.append(pathDirectory)

        # Writing unique values of directories to fileSelectDirectory QListWidget
        self.fileSelectDirectory.clear()
        self.paramSel.clearContents()
        logger.info('Directories with the CDFs searched are:')
        for path in list(set(pathUniqueValues)):
            logger.info(path)
            self.fileSelectDirectory.insertItem( 0, PyQt5.QtWidgets.QListWidgetItem(path))
        logger.info('And the CDFs are:')
        for fileName in self.nameCDFList:
            logger.info(fileName)
        logger.info('****************************************')

    def applyDirectoryTXT(self):
        '''
        Read all data from the CDFs using an input TXT, so that some names can be changed.
        '''
        logger.info('Reading data specified in the input TXT...')
        # Var used to save plots and CSVs
        self.savePlot = False
        # Clearing fileSelect
        self.fileSelect.clear()

        # Searching input TXT file to filter
        pathTXT = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, 'Search input TXT with sensor information', os.getenv('HOME'),
                                              filter='Text files (*.txt)')[0]

        if pathTXT != '':
            # parameterKey: list of all key parameters
            parameterKey = []
            # fullNameParameters: list of full (long) parameters name
            fullNameParameters = []
            # units: units of every parameter
            units = []

            # Reading input TXT
            fileTXT = open(pathTXT, 'r')
            readParamKey = False
            readFullName = False
            readUnits = False
            for fileLine in fileTXT.readlines():
                fileLine = fileLine.strip()

                if 'PARAMETERS_KEY' in fileLine:
                    readParamKey = True
                elif 'PARAMETERS_FULL_NAME' in fileLine:
                    readFullName = True
                elif 'UNITS' in fileLine:
                    readUnits = True
                else:
                    if readParamKey:
                        if '[end]' in fileLine:
                            readParamKey = False
                        else:
                            parameterKey.append(fileLine)
                    elif readFullName:
                        if '[end]' in fileLine:
                            readFullName = False
                        else:
                            fullNameParameters.append(fileLine)
                    elif readUnits:
                        if '[end]' in fileLine:
                            readUnits = False
                        else:
                            units.append(fileLine)
                    else:
                        pass

            # Saving in a dictionary all the vars that have been read in the input
            self.dictTXT = {}
            for fileName in self.nameCDFList:
                self.dictTXT[fileName] = {}
                for i in range(0,len(parameterKey)):
                    self.dictTXT[fileName][parameterKey[i]]= [fullNameParameters[i],units[i]]

            dictFiles = {}
            dictFiles['nameFiles'] = self.nameCDFList
            dictFiles['pathFiles'] = self.pathFiles
            dictFiles['sensorToReadList'] = parameterKey
            dictFiles['boolReadUnits'] = self.boolReadunits

            # Reading CDF specifying sensors
            self.testFlight = TestFlight(dictFiles)

            for fileName in self.nameCDFList:
                for sensorKey in self.testFlight.nameFiles[fileName].sensorNamesList:
                    self.testFlight.parameters[fileName][sensorKey][0] = self.dictTXT[fileName][sensorKey][0]
                    self.testFlight.parameters[fileName][sensorKey][1] = self.dictTXT[fileName][sensorKey][1]

            # Applying same sample rate to all sensors if user has checked it
            sampleRateMax = 0
            if self.boolSameSampleRate:
                logger.info('Same sample rate for all sensors button is checked:')
                for fileName in self.testFlight.sensor.keys():
                    for sensorName in self.testFlight.sensor[fileName].keys():
                        sampleRate = self.testFlight.sensor[fileName][sensorName].sampleRate
                        if sampleRate > sampleRateMax:
                            sampleRateMax = sampleRate
                        else:
                            pass

                logger.info('Maximum sample rate found was: {}'.format(int(sampleRateMax)))
                for fileName in self.testFlight.sensor.keys():
                    self.testFlight.nameFiles[fileName].sampleRate = int(sampleRateMax)
                    for sensorName in self.testFlight.sensor[fileName].keys():
                        self.testFlight.sensor[fileName][sensorName].resampleRate(int(sampleRateMax))

                logger.info('Resample applied correctly.')
            else:
                logger.info('Same sample rate for all sensors button is not checked.')

            self.test_flights_save = copy.deepcopy(self.testFlight)
            self.test_flights_save_no_reference = copy.deepcopy(self.testFlight)

            # Cdf file selection
            i = 0
            for fileName in self.testFlight.nameFiles.keys():
                cdfFileName = '{} - [{}]'.format(fileName, i)
                self.fileSelect.insertItem(0, PyQt5.QtWidgets.QListWidgetItem('{:s}'.format(cdfFileName)))
                i += 1
            logger.info('****************************************')

        else:
            logger.info('No TXT file selected.')
            logger.info('****************************************')

    def applyDirectory(self):
        logger.info('Reading all raw data from CDFs...')
        self.savePlot = False
        self.fileSelect.clear()

        # Dictionary that will be the input of the class TestFlight
        dictFiles = {}
        dictFiles['nameFiles'] = self.nameCDFList
        dictFiles['pathFiles'] = self.pathFiles
        dictFiles['sensorToReadList'] = 'all'
        dictFiles['boolReadUnits'] = self.boolReadunits

        # Reading data and making copies of original data
        # self.testFlight -> data that will be modified
        # self.test_flights_save -> used to return original data with reference applied
        # self.test_flights_save_no_reference -> used to return original data without reference
        self.testFlight = TestFlight(dictFiles)
        # ping same sample rate to all sensors if user has checked it
        # Applying same sample rate to all sensors if user has checked it
        sampleRateMax = 0
        if self.boolSameSampleRate:
            logger.info('Same sample rate for all sensors button is checked:')
            for fileName in self.testFlight.sensor.keys():
                for sensorName in self.testFlight.sensor[fileName].keys():
                    sampleRate = self.testFlight.sensor[fileName][sensorName].sampleRate
                    if sampleRate > sampleRateMax:
                        sampleRateMax = sampleRate
                    else:
                        pass
            logger.info('Maximum sample rate found was: {}'.format(int(sampleRateMax)))
            for fileName in self.testFlight.sensor.keys():
                self.testFlight.nameFiles[fileName].sampleRate = int(sampleRateMax)
                for sensorName in self.testFlight.sensor[fileName].keys():
                    self.testFlight.sensor[fileName][sensorName].resampleRate(int(sampleRateMax))

            logger.info('Resample applied correctly.')
        else:
            logger.info('Same sample rate for all sensors button is not checked.')

        self.test_flights_save = copy.deepcopy(self.testFlight)
        self.test_flights_save_no_reference = copy.deepcopy(self.testFlight)

        # Inserting name of CDF + reference number to fileSelect QListWidget
        i = 0
        for fileName in self.testFlight.nameFiles.keys():
            cdfFileName = '{} - [{}]'.format(fileName, i)
            self.fileSelect.insertItem(0, PyQt5.QtWidgets.QListWidgetItem('{:s}'.format(cdfFileName)))
            i += 1
        logger.info('****************************************')

    def saveSession(self):
        logger.info('Saving session:')
        pathDirectory = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Save session', os.getenv('HOME'))
        if pathDirectory != '':
            fullDate = datetime.now()
            nameSession = 'PYFAT_session_{}-{}-{}_{}-{}'.format(fullDate.year%100, fullDate.month, fullDate.day,
                                                                fullDate.hour, fullDate.minute)
            pathTXT = '{}\{}.txt'.format(pathDirectory, nameSession)
            logger.info('Session saved in: {}'.format(pathTXT))
            fileTXT = open(pathTXT, 'w')

            fileTXT.write('#######################################\n')
            fileTXT.write('Session of PYFAT tool saved on {}-{}-{} at {}:{}\n'.format(fullDate.year,fullDate.month, fullDate.day,
                                                                       fullDate.hour, fullDate.minute))
            fileTXT.write('#######################################\n')
            fileTXT.write('\n')
            fileTXT.write('# Directories of files:\n')
            for index in range(self.fileSelectDirectory.count()):
                fileTXT.write('{}\n'.format(self.fileSelectDirectory.item(index).text()))
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Same sample rate in all CDFs?:\n')
            if self.boolSameSampleRate:
                fileTXT.write('Yes\n')
            else:
                fileTXT.write('No\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# CDF files and their sensors:\n')
            for fileName in self.testFlight.nameFiles.keys():
                sensorList = []
                for sensorName in self.testFlight.parameters[fileName].keys():
                    if sensorName in self.test_flights_save_no_reference.sensor[fileName].keys():
                        sensorList.append(sensorName)
                fileTXT.write('{}: {}\n'.format(fileName, ','.join(sensorList)))
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Sample rate:\n')
            fileTXT.write('{}\n'.format(self.resampleValue.toPlainText()))
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Step:\n')
            fileTXT.write('{}\n'.format(self.stepMovingAvarage.toPlainText()))
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Overlap:\n')
            fileTXT.write('{}\n'.format(self.overlapMovingAvarge.toPlainText()))
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Filter:\n')
            fileTXT.write('Low freq: {}\n'.format(self.lowValue.toPlainText()))
            fileTXT.write('High freq: {}\n'.format(self.highValue.toPlainText()))
            fileTXT.write('Order: {}\n'.format(self.orderValue.toPlainText()))
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Sensor name in plots:\n')
            if self.checkKeyAxisName.isChecked():
                fileTXT.write('Key\n')
            else:
                fileTXT.write('Name\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Same axes in plot?:\n')
            if self.checkAxesYesMain.isChecked():
                fileTXT.write('Yes\n')
            else:
                fileTXT.write('No\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Select what to plot:\n')
            if self.checkCompleteSignalMain.isChecked():
                fileTXT.write('Complete\n')
            elif self.checkSteadySignalMain.isChecked():
                fileTXT.write('Steady\n')
            elif self.checkVibrationsMain.isChecked():
                fileTXT.write('Vibrations\n')
            elif self.checkDisplacement.isChecked():
                fileTXT.write('Displacement\n')
            elif self.checkAllSignalsMain.isChecked():
                fileTXT.write('C+S+V\n')
            else:
                fileTXT.write('Moving RMS\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Displacement frequencies:\n')
            fileTXT.write('Low freq : {}\n'.format(self.lowFreqDisp.toPlainText()))
            fileTXT.write('High freq : {}\n'.format(self.highFreqDisp.toPlainText()))
            fileTXT.write('# End\n')
            fileTXT.write('\n')

            # Ranges of time
            fileTXT.write('# Ranges of time:\n')
            for fileName in self.testFlight.nameFiles.keys():
                sensorName = list(self.testFlight.sensor.get(fileName).keys())[0]
                t = self.testFlight.sensor.get(fileName)[sensorName].time
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append('{:.2f}-{:.2f}'.format(timeSplitted[x][0], timeSplitted[x][-1]))

                fileTXT.write('{}: {}\n'.format(fileName, ','.join(rangesToCSV)))

            fileTXT.write('# End\n')
            fileTXT.write('\n')

            fileTXT.write('# Offsets applied with TXT:\n')
            try:
                for sensorName in self.dictReferenceTXT.keys():
                    value = self.dictReferenceTXT[sensorName]
                    fileTXT.write('{}:{}\n'.format(sensorName, value))
            except:
                fileTXT.write('NaN\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')

            fileTXT.write('# Offsets applied with CDFs:\n')
            try:
                for sensorName in self.dictReference.keys():
                    value = self.dictReference[sensorName]
                    fileTXT.write('{}:{}\n'.format(sensorName, value))
            except:
                fileTXT.write('NaN\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.write('# Data of sensors created by the user:\n')
            for fileName in self.testFlight.nameFiles.keys():
                for sensorName in self.testFlight.parameters[fileName].keys():
                    if sensorName in self.test_flights_save_no_reference.sensor[fileName].keys():
                        pass
                    else:
                        fileTXT.write('{}: {}\n'.format(fileName,sensorName))
                        data = self.testFlight.sensor[fileName][sensorName].data
                        dataString = ','.join(str(x) for x in data)

                        time = self.testFlight.sensor[fileName][sensorName].time
                        fileTXT.write('Time range: {}-{}\n'.format(time[0], time[-1]))
                        fileTXT.write('Units: {}\n'.format(self.testFlight.parameters[fileName][sensorName][1]))
                        fileTXT.write('FullName: {}\n'.format(self.testFlight.parameters[fileName][sensorName][0]))
                        fileTXT.write('Data: {}\n'.format(dataString))
                        fileTXT.write('****************************************************************\n')
            fileTXT.write('# End\n')
            fileTXT.write('\n')
            fileTXT.close()
        logger.info('****************************************')

    def loadSession(self):

        path = PyQt5.QtWidgets.QFileDialog.getOpenFileNames(self, 'Session TXT file', os.getenv('HOME'), filter='TXT files (*.txt)')[0]

        logger.info('Loading session {}'.format(path[0]))
        if path:
            path = path[0]
            fileTXT = open(path,'r')
            readDirectories = False
            readSameSampleRate = False
            readSensors = False
            readSampleRate = False
            readStep = False
            readOverlap = False
            readFilter = False
            readNamePlot = False
            readAxesPlot = False
            readWhatPlot = False
            readFreqDisp = False
            readOffsetTXT = False
            readOffsetCDF = False
            readCreadtedSensors = False
            readRangesTime = False
            for line in fileTXT:
                line = line.strip()
                if '# Directories of files:' in line:
                    readDirectories = True
                    directoriesList = []
                elif '# Same sample rate in all CDFs?:' in line:
                    readSameSampleRate = True
                elif '# CDF files and their sensors:' in line:
                    readSensors = True
                    sensorList = []
                    cdfList = []
                elif '# Sample rate:' in line:
                    readSampleRate = True
                elif '# Step:' in line:
                    readStep = True
                elif '# Overlap:' in line:
                    readOverlap = True
                elif '# Filter:' in line:
                    readFilter = True
                elif '# Sensor name in plots:' in line:
                    readNamePlot = True
                elif '# Same axes in plot?:' in line:
                    readAxesPlot = True
                elif '# Select what to plot:' in line:
                    readWhatPlot = True
                elif '# Displacement frequencies:' in line:
                    readFreqDisp = True
                elif '# Offsets applied with TXT:' in line:
                    readOffsetTXT = True
                    self.dictReferenceTXT = {}
                elif '# Offsets applied with CDFs:' in line:
                    readOffsetCDF = True
                    self.dictReference = {}
                elif '# Data of sensors created by the user:' in line:
                    readCreadtedSensors = True
                    createdSensorsDict = {}
                elif '# Ranges of time:' in line:
                    readRangesTime = True
                    rangesTimeDict = {}
                else:
                    line = line.strip()
                    if readDirectories:
                        if 'End' in line:
                            logger.info('Directories:')
                            for directory in directoriesList:
                                logger.info('- {}'.format(directory))
                            readDirectories = False
                        else:
                            if line not in directoriesList:
                                directoriesList.append(line)
                    elif readSameSampleRate:
                        if 'End' in line:
                            logger.info('Same sample rate to all CDFs? -> {}'.format(self.boolSameSampleRate))
                            readSameSampleRate = False
                        else:
                            line = line.replace(' ', '')
                            if line == 'Yes':
                                self.boolSameSampleRate = True
                            else:
                                self.boolSameSampleRate = False
                    elif readSensors:
                        if 'End' in line:
                            logger.info('CDFs loaded: {}'.format(','.join(cdfList)))
                            logger.info('Sensors loaded: {}'.format(','.join(sensorList)))
                            readSensors = False
                        else:
                            line = line.replace(' ', '')
                            lineSplitted = line.split(':')
                            CDF = lineSplitted[0]
                            cdfList.append(CDF)
                            sensors = lineSplitted[1].split(',')
                            for sensorName in sensors:
                                if sensorName not in sensorList:
                                    sensorList.append(sensorName)
                    elif readSampleRate:
                        if 'End' in line:
                            logger.info('Sample rate applied: {}'.format(sampleRate))
                            readSampleRate = False
                        else:
                            line = line.replace(' ', '')
                            sampleRate = line
                    elif readStep:
                        if 'End' in line:
                            logger.info('Step value [s]: {}'.format(step))
                            readStep = False
                        else:
                            line = line.replace(' ', '')
                            step = line
                    elif readOverlap:
                        if 'End' in line:
                            logger.info('Overlap value [s]: {}'.format(overlap))
                            readOverlap = False
                        else:
                            line = line.replace(' ', '')
                            overlap = line
                    elif readFilter:
                        if 'End' in line:
                            logger.info('Filter values: ')
                            logger.info('WARNING: they will be written in PYFAT tool, but not applied.')
                            logger.info('High pass frequency [hz]: {}'.format(lowFreq))
                            logger.info('Low pass frequency [hz]: {}'.format(highFreq))
                            logger.info('Order value: {}'.format(order))

                            readFilter = False
                        else:
                            line = line.replace(' ', '')
                            lineSplitted = line.split(':')
                            if 'Lowfreq' in lineSplitted[0]:
                                lowFreq = lineSplitted[1]
                            elif 'Highfreq' in lineSplitted[0]:
                                highFreq = lineSplitted[1]
                            else:
                                order = lineSplitted[1]
                    elif readNamePlot:
                        if 'End' in line:
                            logger.info('What names in plots? -> {}'.format(namePlot))
                            readNamePlot = False
                        else:
                            line = line.replace(' ', '')
                            namePlot = line

                    elif readAxesPlot:
                        if 'End' in line:
                            logger.info('Same axes in plots? -> {}'.format(axesPlot))
                            readAxesPlot = False
                        else:
                            line = line.replace(' ', '')
                            axesPlot = line
                    elif readWhatPlot:
                        if 'End' in line:
                            logger.info('What is going to be plotted?, {}'.format(whatPlot))
                            readWhatPlot = False
                        else:
                            line = line.replace(' ', '')
                            whatPlot = line
                    elif readFreqDisp:
                        if 'End' in line:
                            logger.info('Filter in displacements:')
                            logger.info('High pass filter [hz]: {}'.format(lowFreqDisp))
                            logger.info('Low pass filter [hz]: {}'.format(highFreqDisp))
                            readFreqDisp = False
                        else:
                            line = line.replace(' ', '')
                            lineSplitted = line.split(':')
                            if 'Lowfreq' in lineSplitted[0]:
                                lowFreqDisp = lineSplitted[1]
                            else:
                                highFreqDisp = lineSplitted[1]
                    elif readOffsetTXT:
                        if 'End' in line:
                            logger.info('Offset applied with input TXT:')
                            if self.dictReferenceTXT:
                                for sensorName in self.dictReferenceTXT.keys():
                                    logger.info('{}: {}'.format(sensorName, self.dictReferenceTXT[sensorName]))
                            else:
                                self.dictReferenceTXT = np.nan
                                logger.info('None')
                            readOffsetTXT = False
                        else:
                            line = line.replace(' ', '')
                            if 'NaN' in line:
                                readOffsetTXT = np.nan
                            else:
                                lineSplitted = line.split(':')
                                self.dictReferenceTXT[lineSplitted[0]] = lineSplitted[1]

                    elif readOffsetCDF:
                        if 'End' in line:
                            logger.info('Offset applied with input CDFs:')
                            if self.dictReference:
                                for sensorName in self.dictReference.keys():
                                    logger.info('{}: {}'.format(sensorName, self.dictReference[sensorName]))
                            else:
                                self.dictReference = np.nan
                                logger.info('None')
                            readOffsetCDF = False
                        else:
                            line = line.replace(' ', '')
                            if 'NaN' in line:
                                readOffsetCDF = np.nan
                            else:
                                lineSplitted = line.split(':')
                                self.dictReference[lineSplitted[0]] = lineSplitted[1]

                    elif readCreadtedSensors:
                        if 'End' in line:
                            logger.info('Created sensors:')
                            if createdSensorsDict:
                                for sensorName in createdSensorsDict.keys():
                                    logger.info(sensorName)
                            else:
                                logger.info('None')
                            readCreadtedSensors = False
                        else:
                            line = line.replace(' ', '')
                            if 'Data' in line:
                                lineSplitted = line.split(':')
                                data = lineSplitted[1].split(',')
                                data = np.asarray(data).astype(float)
                            elif 'Timerange' in line:
                                lineSplitted = line.split(':')
                                rangeTime = lineSplitted[1].split('-')
                                rangeTime = list(map(float, rangeTime))
                            elif 'Units' in line:
                                lineSplitted = line.split(':')
                                units = lineSplitted[1]
                            elif 'FullName' in line:
                                lineSplitted = line.split(':')
                                fullName = lineSplitted[1]
                            elif '****' in line:
                                createdSensorsDict[nameSensorCreated] = {
                                    'FileName': fileName,
                                    'Data': data,
                                    'Range': rangeTime,
                                    'Units': units,
                                    'FullName': fullName
                                }
                            else:
                                nameSensorCreated = line.split(':')[1]
                                fileName = line.split(':')[0]
                    elif readRangesTime:
                        if 'End' in line:
                            logger.info('Ranges of time:')
                            for fileName in rangesTimeDict.keys():
                                logger.info('CDF {}: {}'.format(fileName, rangesTimeDict[fileName]))
                            readRangesTime = False
                        else:
                            line = line.replace(' ', '')
                            lineSplitted = line.split(':')
                            cdfName = lineSplitted[0]
                            rangeTime = list(map(lambda x: x.split('-'), lineSplitted[1].split(',')))

                            rangesTimeDict[cdfName] = rangeTime
                    else:
                        pass

            # Clearing all widgets of main window
            self.fileSelect.clear()
            self.fileSelectDirectory.clear()
            self.paramSel.clearContents()

            # Loading all CDFs of loaded session
            logger.info('Reading data from CDFs...')
            self.savePlot = False

            globalPathList = []
            #Saving in a list the paths corresponding to each CDF. They are sorted.
            for CDF_name in cdfList:
                for dirPath in directoriesList:
                    if CDF_name in os.listdir(dirPath):
                        globalPathList.append(dirPath)
                    else:
                        pass

            for path in list(directoriesList):
                self.fileSelectDirectory.insertItem(0, PyQt5.QtWidgets.QListWidgetItem(path))

            # Dictionary that will be the input of the class TestFlight
            dictFiles = {}
            dictFiles['nameFiles'] = cdfList
            dictFiles['pathFiles'] = globalPathList
            dictFiles['sensorToReadList'] = sensorList
            dictFiles['boolReadUnits'] = self.boolReadunits

            # Reading data and making copies of original data
            # self.testFlight -> data that will be modified
            # self.test_flights_save -> used to return original data with reference applied
            # self.test_flights_save_no_reference -> used to return original data without reference
            self.testFlight = TestFlight(dictFiles)
            # Applying same sample rate to all sensors if user has checked it
            # Applying same sample rate to all sensors if user has checked it
            sampleRateMax = 0
            if self.boolSameSampleRate:
                logger.info('Same sample rate for all sensors button is checked:')
                for fileName in self.testFlight.sensor.keys():
                    for sensorName in self.testFlight.sensor[fileName].keys():
                        sampleRate = self.testFlight.sensor[fileName][sensorName].sampleRate
                        if sampleRate > sampleRateMax:
                            sampleRateMax = sampleRate
                        else:
                            pass
                logger.info('Maximum sample rate found was: {}'.format(int(sampleRateMax)))
                for fileName in self.testFlight.sensor.keys():
                    self.testFlight.nameFiles[fileName].sampleRate = int(sampleRateMax)
                    for sensorName in self.testFlight.sensor[fileName].keys():
                        self.testFlight.sensor[fileName][sensorName].resampleRate(int(sampleRateMax))

                logger.info('Resample applied correctly.')
            else:
                logger.info('Same sample rate for all sensors button was not checked.')

            self.test_flights_save = copy.deepcopy(self.testFlight)
            self.test_flights_save_no_reference = copy.deepcopy(self.testFlight)

            # Cdf file selection
            i = 0
            for fileName in self.testFlight.nameFiles.keys():
                cdfFileName = '{} - [{}]'.format(fileName, i)
                self.fileSelect.insertItem(0, PyQt5.QtWidgets.QListWidgetItem('{:s}'.format(cdfFileName)))
                i += 1

            # Offset applied with CDF
            if pd.isnull(self.dictReference):
                logger.info('No CDF file used to apply reference.')
            else:
                logger.info('Applying offset with CDF reference')
                # Applying calculated reference
                for fileName in self.testFlight.nameFiles.keys():
                    logger.info('File: {}...'.format(fileName))
                    for sensorName in self.testFlight.sensor[fileName].keys():
                        if sensorName in self.dictReference.keys():
                            valueReference = float(self.dictReference[sensorName])
                            logger.info(
                                '- Sensor {} modified. Values used is: {}'.format(sensorName, valueReference))
                            self.testFlight.sensor.get(fileName)[sensorName].data -= valueReference
                            self.testFlight.sensor.get(fileName)[sensorName].dataInitial -= valueReference
                        else:
                            logger.info('- Sensor {} was not found in referenced CDF.'.format(sensorName))

            # Loop through all CDFs loaded
            if pd.isnull(self.dictReferenceTXT):
                logger.info('No TXT file used to apply reference.')
            else:
                logger.info('Applying offset with input TXT ')
                for fileName in self.testFlight.nameFiles.keys():
                    logger.info('File: {}...'.format(fileName))
                    # Loop through all sensors of every CDF loaded
                    countSensorsModified = 0
                    for sensorName in self.testFlight.sensor[fileName].keys():
                        # If sensor name is in the dictionary referenceTXT, apply reference.
                        if sensorName in self.dictReferenceTXT.keys():
                            logger.info('- Sensor {} modified with value {}'.format(sensorName, self.dictReferenceTXT[sensorName]))

                            if '-' in self.dictReferenceTXT[sensorName]:
                                value = float(self.dictReferenceTXT[sensorName][1:])
                                self.testFlight.sensor.get(fileName)[sensorName].data -= value
                                self.testFlight.sensor.get(fileName)[sensorName].dataInitial -= value
                            elif '/' in self.dictReferenceTXT[sensorName]:
                                value = float(self.dictReferenceTXT[sensorName][1:])
                                self.testFlight.sensor.get(fileName)[sensorName].data /= value
                                self.testFlight.sensor.get(fileName)[sensorName].dataInitial /= value
                            elif '*' in self.dictReferenceTXT[sensorName]:
                                value = float(self.dictReferenceTXT[sensorName][1:])
                                self.testFlight.sensor.get(fileName)[sensorName].data *= value
                                self.testFlight.sensor.get(fileName)[sensorName].dataInitial *= value
                            elif '+' in self.dictReferenceTXT[sensorName]:
                                value = float(self.dictReferenceTXT[sensorName][1:])
                                self.testFlight.sensor.get(fileName)[sensorName].data += value
                                self.testFlight.sensor.get(fileName)[sensorName].dataInitial += value
                            else:
                                value = float(self.dictReferenceTXT[sensorName])
                                self.testFlight.sensor.get(fileName)[sensorName].data += value
                                self.testFlight.sensor.get(fileName)[sensorName].dataInitial += value
                            countSensorsModified += 1
                        else:
                            pass
                    logger.info('Total of {} sensors have been modified'.format(countSensorsModified))

                self.test_flights_save = copy.deepcopy(self.testFlight)


            # Sample rate
            self.resampleValue.setPlainText(str(sampleRate))
            self.resample()

            # Step
            self.stepMovingAvarage.setPlainText(step)
            # Overlap
            self.overlapMovingAvarge.setPlainText(overlap)

            # Filter
            self.lowValue.setPlainText(lowFreq)
            self.highValue.setPlainText(highFreq)
            self.orderValue.setPlainText(order)

            # Ranges of time
            for fileName in self.testFlight.nameFiles.keys():
                rangeTime = rangesTimeDict[fileName]
                # Converting string numbers to float
                rangeTime = [[float(x) for x in lst] for lst in rangeTime]
                for sensorName in self.testFlight.sensor[fileName].keys():
                    self.testFlight.sensor[fileName][sensorName].cut_data(rangeTime)


            # What to plot
            if whatPlot == 'Key':
                self.checkKeyAxisName.setChecked(True)
            else:
                self.checkNameAxisName.setChecked(True)

            # Same axes?
            if axesPlot == 'Yes':
                self.checkAxesYesMain.setChecked(True)
            else:
                self.checkAxesNoMain.setChecked(True)

            # What to plot
            if whatPlot == 'Complete':
                self.checkCompleteSignalMain.setChecked(True)
            elif whatPlot == 'Steady':
                self.checkSteadySignalMain.setChecked(True)
            elif whatPlot == 'Vibrations':
                self.checkVibrationsMain.setChecked(True)
            elif whatPlot == 'Displacements':
                self.checkDisplacement.setChecked(True)
            elif whatPlot == 'C+S+V':
                self.checkAllSignalsMain.setChecked(True)
            else:
                self.checkMovingRMS.setChecked(True)

            # Inserting created sensors
            # Appending new sensor to CDF class (CdfFileData) of testFlight
            for flightClass in [self.testFlight, self.test_flights_save]:
                for newSensorName in createdSensorsDict.keys():
                    fileName = createdSensorsDict[newSensorName]['FileName']
                    data = createdSensorsDict[newSensorName]['Data']
                    rangeTime = createdSensorsDict[newSensorName]['Range']
                    time = np.linspace(rangeTime[0], rangeTime[1], data.shape[0])
                    units = createdSensorsDict[newSensorName]['Units']
                    sampleRate = 1/(time[1]-time[0])
                    fullName = createdSensorsDict[newSensorName]['FullName']


                    flightClass.nameFiles[fileName].sensorNamesList.append(newSensorName)
                    flightClass.nameFiles[fileName].units[newSensorName] = units
                    flightClass.nameFiles[fileName].data.append(data)
                    flightClass.nameFiles[fileName].dataInitial.append(data)
                    # Appending new sensor to testFlight class
                    flightClass.sensor[fileName][newSensorName] = Sensor(flightClass.nameFiles[fileName], newSensorName)
                    flightClass.sensor[fileName][newSensorName].sampleRate = sampleRate
                    cdfPos = flightClass.nameFiles[fileName].CDFpos(newSensorName)
                    flightClass.parameters[fileName][newSensorName] = [fullName, units, cdfPos]
                    # Changing value of time so that it has same sample rate of the CDF file.
                    flightClass.sensor[fileName][newSensorName].time = time
                    flightClass.sensor[fileName][newSensorName].timeInitial = copy.deepcopy(time)


        logger.info('****************************************')


    def fileSelected(self):
        '''
        Method that will be applied when user click some of the CDF files of fileSelect QListWidget -> It means that user
        has selected some of them (at least one)
        '''

        # Clearing paramSel QListWidget before inserting names
        self.paramSel.clearContents()

        # Counting number of rows that will be needed in paramSel QListWidget:
        # It is: NumberOfFiles * NumberOfSensors
        numberRows = 0
        for fileClass in self.fileSelect.selectedItems():
            indexSpace = fileClass.text().find(' ')
            fileName = fileClass.text()[:indexSpace]

            numberRows += len(self.testFlight.sensor[fileName].keys())
        self.paramSel.setRowCount(numberRows)

        # Creating a dictionary attribute that will be used to link the reference number
        # and the file name
        i = 0
        self.fileSelectedDict = {}
        for fileClass in self.fileSelect.selectedItems():
            indexSpace = fileClass.text().find(' ')
            numberFile = fileClass.text()[indexSpace + 3:]
            fileName = fileClass.text()[:indexSpace]

            logger.info('File {} has been selected.'.format(fileName))
            self.fileSelectedDict[numberFile] = fileName

            # Inserting all sensors of all CDFs selected to paramSel QTableWidget
            for sensor_name in self.testFlight.sensor.get(fileName).keys():
                fullName = self.testFlight.parameters[fileName][sensor_name][0]
                units = self.testFlight.parameters[fileName][sensor_name][1]

                self.paramSel.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(sensor_name))
                self.paramSel.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(units))
                self.paramSel.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(numberFile))
                self.paramSel.setItem(i, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName))
                i += 1

            # Resizing paramSel
            self.paramSel.resizeColumnToContents(0)
            self.paramSel.resizeColumnToContents(1)
            self.paramSel.resizeColumnToContents(2)
            self.paramSel.resizeColumnToContents(3)

            # Inserting sampleRate to resampleValue QTextEdit and aligning to center
            self.resampleValue.setPlainText('{:.0f}'.format(self.testFlight.nameFiles[fileName].sampleRate))
            self.resampleValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
            logger.info('****************************************')

    def createSensorCond(self):
        logger.info('Creating new parameter...')
        # Counting number of sensors that are going to be plotted
        numberOfSensors = len(self.paramSel.selectedItems())

        # Loop through all selected sensors...
        for i in range(numberOfSensors):
            # Reading characteristics of every sensor
            index = self.paramSel.selectedIndexes()[i]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]
            sampleRate = self.testFlight.sensor[fileName][sensorName].sampleRate

            # Saving data, time(with nan values), and time initial (without nan values)

            timeSensor = copy.deepcopy(self.testFlight.sensor[fileName][sensorName].time)
            timeSplitted = [timeSensor[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(timeSensor))]
            dataSensor = copy.deepcopy(self.testFlight.sensor[fileName][sensorName].data)
            dataSplitted = [dataSensor[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(timeSensor))]

            for rangeIndex in range(len(timeSplitted)):
                dataSensor = dataSplitted[rangeIndex]
                timeSensor = timeSplitted[rangeIndex]
                # Creating name of the sensor of every ranges
                n = 1
                newSensorName = '{}_{}'.format(sensorName, n)
                while newSensorName in self.testFlight.sensor[fileName].keys():
                    n += 1
                    newSensorName = '{}_{}'.format(sensorName, n)
                logger.info('Name of new parameter is: {}'.format(newSensorName))

                # Appending new sensor to CDF class (CdfFileData) of testFlight
                for flightClass in [self.testFlight, self.test_flights_save]:
                    flightClass.nameFiles[fileName].sensorNamesList.append(newSensorName)
                    flightClass.nameFiles[fileName].units[newSensorName] = units
                    dataSensor[np.isnan(timeSensor)] = np.nan
                    flightClass.nameFiles[fileName].data.append(dataSensor)
                    flightClass.nameFiles[fileName].dataInitial.append(dataSensor)
                    # Appending new sensor to testFlight class
                    flightClass.sensor[fileName][newSensorName] = Sensor(flightClass.nameFiles[fileName], newSensorName)
                    flightClass.sensor[fileName][newSensorName].sampleRate = sampleRate
                    cdfPos = flightClass.nameFiles[fileName].CDFpos(newSensorName)
                    flightClass.parameters[fileName][newSensorName] = [fullName, units, cdfPos]
                    # Changing value of time so that it has same sample rate of the CDF file.
                    flightClass.sensor[fileName][newSensorName].time = timeSensor
                    flightClass.sensor[fileName][newSensorName].timeInitial = copy.deepcopy(timeSensor)
        logger.info('****************************************')
        self.fileSelected()

    def deleteCreatedSensors(self):
        logger.info('Created sensors deleted')

        for index in range(self.fileSelect.count()):
            indexSpace = self.fileSelect.item(index).text().find(' ')
            numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index).text()[:indexSpace]
            for sensorName in list(self.testFlight.sensor[fileName].keys()):
                if sensorName in self.test_flights_save_no_reference.sensor[fileName].keys():
                    pass
                else:
                    logger.info('Deleting sensor: {}'.format(sensorName))
                    for flightClass in [self.testFlight, self.test_flights_save]:
                        cdfPos = flightClass.nameFiles[fileName].CDFpos(sensorName)
                        flightClass.nameFiles[fileName].sensorNamesList.remove(sensorName)
                        del flightClass.nameFiles[fileName].units[sensorName]
                        flightClass.nameFiles[fileName].data.pop(cdfPos)
                        flightClass.nameFiles[fileName].dataInitial.pop(cdfPos)
                        # Appending new sensor to testFlight class
                        del flightClass.sensor[fileName][sensorName]
                        del flightClass.parameters[fileName][sensorName]
        logger.info('****************************************')
        self.fileSelected()

    def checkPlotMain(self):
        '''
        This method has been created so that every time a plot is needed in main window, it checks what plot has to be done
        depending on what has the user selected. The options are: Complete Signal, Steady Sgnal, Vibrations,
        Displacement, C+S+V (Complete + Steady + Vibration) or Moving RMS
        '''

        # Problem when one item of paramSel QTableWidget is unselected, this If statement avoid that.
        if len(self.paramSel.selectedItems()) > 0:
            if self.checkCompleteSignalMain.isChecked():
                # Plotting complete signal in main window
                self.plotCompleteSignalMainWindow()
            elif self.checkSteadySignalMain.isChecked():
                # Plotting steady signal in main window
                self.plotSteadySignalMainWindow()
            elif self.checkVibrationsMain.isChecked():
                # Plotting vibration signal in main window
                self.plotVibrationsMainWindow()
            elif self.checkAllSignalsMain.isChecked():
                # Plotting C+S+V in main window
                self.plotAllSignalsMainWindow()
            elif self.checkMovingRMS.isChecked():
                # Plotting moving RMS in main window
                self.plotMovingRMSMainWindow()
            else:
                # Plotting displacements in main window
                self.plotDisplacementMainWindow()
        else:
            self.MplWidget.removePlot()

    def selectTabBarIndex(self):
        '''
        This method applies some functions depending on what tab has clicked the user. There are 4 possibilites:
        self.tabWidget == 1 -> Time Analysis tab
        self.tabWidget == 2 -> Freq Analysis tab
        self.tabWidget == 3 -> Multiple Plots tab
        '''

        if self.tabWidget.currentIndex() == 1:
            logger.info('Tab Time Analysis selected')
            self.timeAnalysis()
            logger.info('****************************************')
        elif self.tabWidget.currentIndex() == 2:
            logger.info('Tab Freq Analysis selected')
            logger.info('****************************************')
            self.freqAnalysis()

        elif self.tabWidget.currentIndex() == 3:
            logger.info('Tab Multiple Plots selected')
            logger.info('****************************************')
            self.multiPlot()

        elif self.tabWidget.currentIndex() == 0:
            logger.info('Tab Data View and Preprocessing selected')
            logger.info('****************************************')

        else:
            pass

    def changeParameterSelection(self):
        '''
        This method runs when buttonCahngeParameters QPushButon is clicked (Select Parameters).
        When there are a lot of sensors ans user only want to study some of them, this method clear all the
        sensors that there were in paramSel QTableWidget and writes only the ones that were selected.
        '''
        paramSelList = []
        numberFileList = []
        fullNameList = []
        unitsList = []

        # Reading all selected sensor from paramSel QTableWidget
        for index in self.paramSel.selectedIndexes():
            sensorName = self.paramSel.item(index.row(),0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()

            paramSelList.append(sensorName)
            fullNameList.append(fullName)
            numberFileList.append(numberFile)
            unitsList.append(units)

        # Clearing paramSel QTableWidget and counting and setting the number of rows of it.
        self.paramSel.clearContents()
        numberRows = len(paramSelList)
        self.paramSel.setRowCount(numberRows)

        # Writting all the elements in paramSel QTableWidget
        logger.info('User has selected some sensors, the other will be deleted from PYFAT tool. ')
        logger.info('Sensors are:')
        for i in range(len(paramSelList)):
            logger.info('- {}'.format(paramSelList[i]))
            self.paramSel.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(paramSelList[i]))
            self.paramSel.setItem(i, 3, PyQt5.QtWidgets.QTableWidgetItem(fullNameList[i]))
            self.paramSel.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(numberFileList[i]))
            self.paramSel.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(unitsList[i]))
        logger.info('****************************************')

    def unselectParameterSelection(self):
        '''
        This method runs when buttonUnselParameters QPushButon is clicked (Unselect Parameters).
        '''

        logger.info('Parameters unselected.')

        # Clearing paramSel QTableWidget and counting and setting the number of rows of it.
        self.paramSel.clearContents()
        # Counting number of rows that will be needed in paramSel QListWidget:
        # It is: NumberOfFiles * NumberOfSensors
        numberRows = 0
        for fileClass in self.fileSelect.selectedItems():
            indexSpace = fileClass.text().find(' ')
            fileName = fileClass.text()[:indexSpace]

            numberRows += len(self.testFlight.sensor[fileName].keys())
        self.paramSel.setRowCount(numberRows)

        # Writting all the elements in paramSel QTableWidget
        logger.info('Unselecting all sensors...')
        i = 0
        for fileClass in self.fileSelect.selectedItems():
            indexSpace = fileClass.text().find(' ')
            numberFile = fileClass.text()[indexSpace + 3:]
            fileName = fileClass.text()[:indexSpace]

            # Inserting all sensors of all CDFs selected to paramSel QTableWidget
            for sensorName in self.testFlight.sensor[fileName].keys():
                fullName = self.testFlight.parameters[fileName][sensorName][0]
                units = self.testFlight.parameters[fileName][sensorName][1]

                self.paramSel.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName))
                self.paramSel.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(units))
                self.paramSel.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(numberFile))
                self.paramSel.setItem(i, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName))
                i += 1
        logger.info('****************************************')

    def plotMovingRMSMainWindow(self):
        '''
        PLOTING MOVING RMS
        '''

        # Creating the figure
        figure = Figure()
        figure.set_constrained_layout(True)
        ax1 = figure.add_subplot(111)

        # Hidding groupSelectionPlotAll QTableWidget -> Ranges of plotAllSignalsMain
        self.groupSelectionPlotAll.setHidden(True)
        self.filterDisplacementFrame.setHidden(True)

        # Counting number of selected items. Maximum 2.
        numberSelectedItems = self.paramSel.selectedItems()

        # Selecting step and overlap from QPlainText
        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Loop through all items selected in paramSel QTableWidget
        lines = []
        for i in range(len(numberSelectedItems)):
            # Saving name, full name, file name...
            index = self.paramSel.selectedIndexes()[i]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Time of selected sensor
            t = copy.deepcopy(self.testFlight.sensor.get(fileName)[sensorName].time)

            # Calculating moving RMS
            movingRMS = self.testFlight.sensor[fileName][sensorName].movingRMS(overlap, step)

            # Checking if user want to write full name in plots
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # If every sensor is plotted in different axes...
            if self.checkAxesYesMain.isChecked():
                # Always the same axes
                axesToPlot = ax1

                # Plotting moving RMS...
                colorPlot = color='C{}'.format(i)
                labelPlot = '{} {} [{}]'.format(nameToPlot, numberFile, units)
                p, = axesToPlot.plot(t, movingRMS,colorPlot ,label= labelPlot)
                # To write axes in the end, all lines are going to be saved
                lines.append(p)
                axesToPlot.set_xlabel('Time [s]')
                yLabel = 'Moving RMS'
                axesToPlot.set_ylabel(yLabel)

            # If user want different axes...
            else:
                # All axes are going to be twin of the first axes
                if i==0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                    axesToPlot.spines['right'].set_position(('axes', 0.9+0.1*i))

                colorPlot = 'C{}'.format(i)
                labelPlot = '{} {} [{}]'.format(nameToPlot, numberFile, units)
                p, = axesToPlot.plot(t, movingRMS, color=colorPlot, label=labelPlot)
                lines.append(p)

                # Changing color properties of the plot
                axesToPlot.yaxis.label.set_color(p.get_color())
                tkw = dict(size=4, width=1.5)
                axesToPlot.tick_params(axis='y', colors=p.get_color(), **tkw)

                axesToPlot.set_xlabel('Time [s]')
                yLabel = 'RMS of {} [{}]'.format(nameToPlot, units)
                axesToPlot.set_ylabel(yLabel)

            # If user wants to export selected data
            if self.savePlot:
                # Adding sup title
                figure.suptitle('Moving RMS', fontsize=13)
                title = 'Moving RMS. Step = {} [s]. Overlap = {} [%].'.format(step, overlap)
                axesToPlot.set_title(title)
                axesToPlot.legend()

                titleSave = 'Moving_RMS_{}'.format(sensorName)

                # Exporting graph
                path = '{}{}{}.jpg'.format(self.pathSavePlot,os.path.sep, titleSave)
                logger.info('Saving JPG of moving RMS. Title is {}.jpg'.format(titleSave))
                figure.savefig(path)

                # Exporting CSV
                # Creating list to append them to the CSV
                # It is going to be checked if there are different ranges. If there are, it is going to be written
                # columns with raw data and data splitted.

                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]

                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append([timeSplitted[x][0], timeSplitted[x][-1]])


                # With no ranges
                if not np.isnan(np.sum(t)):
                    timeToCSV = ['Time - {}'.format(sensorName)]
                    timeToCSV.extend(t)
                    dataToCSV = ['Moving RMS - {}'.format(sensorName)]
                    dataToCSV.extend(movingRMS)
                    # Aggregating lists...
                    rows = zip(timeToCSV, dataToCSV)

                # With ranges
                else:
                    rawTime = self.testFlight.sensor.get(fileName)[sensorName].timeInitial
                    timeToCSV = ['Time']
                    timeToCSV.extend(rawTime)
                    dataToCSV = ['Moving RMS']
                    dataToCSV.extend(movingRMS)
                    dataRangeToCSV = ['Moving RMS with Range']
                    movingRMS = movingRMS.astype(object)
                    movingRMS[np.where(np.isnan(t))] = ''
                    dataRangeToCSV.extend(movingRMS)
                    # Aggregating lists...
                    rows = zip(timeToCSV, dataToCSV, dataRangeToCSV)

                path = '{}\{}.csv'.format(self.pathSavePlot, titleSave)
                logger.info('Saving CSV of moving RMS. Title is {}.csv'.format(titleSave))
                with open(path, 'w', newline='') as csvFile:
                    # Writting lines in the CSV
                    csvFile.write('################################################\n')
                    csvFile.write('# File: {}\n'.format(fileName))
                    csvFile.write('# Sensor: {}\n'.format(sensorName))
                    try:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(self.dictReference[sensorName]))
                    except:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(np.nan))
                    try:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(self.dictReferenceTXT[sensorName]))
                    except:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(np.nan))
                    csvFile.write('# Step: {}\n'.format(step))
                    csvFile.write('# Overlap: {}\n'.format(overlap))
                    for m in range(len(rangesToCSV)):
                        csvFile.write('# Range {} [s]: [{:.2f}-{:.2f}]\n'.format(m, rangesToCSV[m][0], rangesToCSV[m][1]))

                    timeFlight = self.testFlight.nameFiles[fileName].time_year
                    timeFlight1 = timeFlight[~np.isnan(timeFlight)][0]
                    timeFlight2 = timeFlight[~np.isnan(timeFlight)][-1]
                    csvFile.write('# Time of Flight: {}-{} [s]\n'.format(timeFlight1, timeFlight2))
                    csvFile.write('################################################\n')
                    writer = csv.writer(csvFile, delimiter=',')
                    for row in rows:
                        writer.writerow(row)
                csvFile.close()
                logger.info('****************************************')
            else:
                pass
        if not self.savePlot:
            if len(numberSelectedItems) >= 1:
                # Adding title
                title = 'Moving RMS. Step = {} [s]. Overlap = {} [%].'.format(step, overlap)
                axesToPlot.set_title(title)
                # Adding sup title
                figure.suptitle('Moving RMS', fontsize=13)
                # Adding legend
                ax1.legend(lines, [l.get_label() for l in lines])

            self.MplWidget.removePlot()
            self.MplWidget.addPlot(figure)
        else:
            pass

    def  resetParametersSelection(self):
        '''
        Adding original data to paramSel QTableWidget. All the parameters are going to be reset, but
        reference will be kept (if it was applied)
        '''

        logger.info('Reseting parameters:')
        logger.info('- Resample deleted')
        logger.info('- Filter deleted')
        logger.info('- Ranges of time deleted')
        logger.info('- Conditional deleted')
        logger.info('- Offset NOT deleted')
        logger.info('- Parameters NOT unselected')
        logger.info('****************************************')

        # Using one of the copies that was done of all the parameters.
        self.testFlight = copy.deepcopy(self.test_flights_save)

        if len(self.fileSelect.selectedItems()) >= 1:
            indexSpace = self.fileSelect.selectedItems()[0].text().find(' ')
            fileNumber = self.fileSelect.selectedItems()[0].text()[indexSpace + 3:]
            fileName = self.fileSelect.selectedItems()[0].text()[:indexSpace]
            self.resampleValue.setPlainText('{:.0f}'.format(self.testFlight.nameFiles[fileName].sampleRate))
            self.resampleValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        else:
            pass

        self.lowTimeValue1.setPlainText('')
        self.lowTimeValue1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highTimeValue1.setPlainText('')
        self.highTimeValue1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.lowTimeValue2.setPlainText('')
        self.lowTimeValue2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highTimeValue2.setPlainText('')
        self.highTimeValue2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.lowTimeValue3.setPlainText('')
        self.lowTimeValue3.setAlignment(v.QtCore.Qt.AlignCenter)
        self.highTimeValue3.setPlainText('')
        self.highTimeValue3.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.lowFreqDisp.setPlainText('10')
        self.lowFreqDisp.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highFreqDisp.setPlainText('250')
        self.highFreqDisp.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.lowValue.setPlainText('High pass')
        self.lowValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highValue.setPlainText('Low pass')
        self.highValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.orderValue.setPlainText('n')
        self.orderValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # Setting step QTextEdit to 1
        self.stepMovingAvarage.setPlainText('1')
        self.stepMovingAvarage.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        # Setting overlap QTextEdit to 0
        self.overlapMovingAvarge.setPlainText('0')
        self.overlapMovingAvarge.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # Clearing condSel QtableWidget and condSelParList QListWidget
        self.condSelParList.clear()
        self.condSel.clearContents()
        self.groupCondSel.setHidden(True)
        self.manualTime = False
        self.condSelParList.clear()

        # Calling plot meth
        self.checkPlotMain()

    def deleteReference(self):
        '''
        Method that returns the original data, deleting de reference if it was applied.
        '''
        logger.info('Reseting parameters:')
        logger.info('- Deleting offset.')
        logger.info('- Resample NOT deleted')
        logger.info('- Ranges of time NOT deleted')
        logger.info('- Filters NOT deleted')
        logger.info('- Conditional NOT deleted')
        logger.info('****************************************')

        listSensorsWithOffset = []
        try:
            listSensorsWithOffset += list(self.dictReferenceTXT.keys())
        except:
            pass
        try:
            listSensorsWithOffset += list(self.dictReference.keys())
        except:
            pass

        listSensorsWithOffset = list(set(listSensorsWithOffset))
        for index in range(self.fileSelect.count()):
            indexSpace = self.fileSelect.item(index).text().find(' ')
            numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index).text()[:indexSpace]
            for sensorName in listSensorsWithOffset:
                if sensorName in self.testFlight.sensor[fileName].keys():
                    sampleRate = self.testFlight.sensor[fileName][sensorName].sampleRate
                    self.testFlight.sensor[fileName][sensorName] = copy.deepcopy(
                        self.test_flights_save_no_reference.sensor[fileName][sensorName])
                    self.testFlight.sensor[fileName][sensorName].resampleRate(sampleRate)


            self.test_flights_save = copy.deepcopy(self.testFlight)
            self.dictReferenceTXT = np.nan
            self.dictReference = np.nan
        self.checkPlotMain()


    def plotCompleteSignalMainWindow(self):
        '''
        PLOTTING COMPLETE SIGNAL
        '''

        figure = Figure()
        #figure.set_constrained_layout(True)
        ax1 = figure.add_subplot(111)

        #Hidding groupSelectionPlotAll QTableWidget -> Ranges of plotAllSignalsMain
        self.groupSelectionPlotAll.setHidden(True)
        self.filterDisplacementFrame.setHidden(True)

        # Counting number of sensors that are going to be plotted
        numberOfSensors = len(self.paramSel.selectedItems())

        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Loop through all sensors...
        lines = []
        for i in range(numberOfSensors):
            # Reading characteristics of every sensor
            index = self.paramSel.selectedIndexes()[i]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Saving time, data, step, overlap and steadyData
            t = self.testFlight.sensor.get(fileName)[sensorName].time
            y = self.testFlight.sensor.get(fileName)[sensorName].data

            # Calculating steady data
            steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

            # Checking what name is going to be used in the title and the legend
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Selecting axes to plot, colors of every sensor and the place of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                p1, = axesToPlot.plot(t, y, label='Complete {} {} [{}]'.format(nameToPlot, numberFile, units))
                p2, = axesToPlot.plot(t, steadyData, label='Steady {} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p1)
                lines.append(p2)
                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Complete and steady signal')

            else:
                if i == 0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                    axesToPlot.spines['right'].set_position(('axes', 0.9 + 0.1 * i))

                p1, = axesToPlot.plot(t, y, color='C{}'.format(i * 2),
                                      label='Complete {} {} [{}]'.format(nameToPlot, numberFile, units))
                p2, = axesToPlot.plot(t, steadyData, color='C{}'.format(i * 2 + 1),
                                      label='Steady {} {} [{}]'.format(nameToPlot, numberFile, units))

                lines.append(p1)
                lines.append(p2)

                # Changing color properties of the plot
                axesToPlot.yaxis.label.set_color(p1.get_color())
                tkw = dict(size=4, width=1.5)
                axesToPlot.tick_params(axis='y', colors=p1.get_color(), **tkw)

                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('{} [{}]'.format(nameToPlot, units))

            figure.suptitle('Complete signal', fontsize=13)

            if self.savePlot:
                title = 'Complete signal - Time [s]'
                axesToPlot.set_title(title)
                axesToPlot.legend()
                logger.info('Saving selected sensors...')

                # Exporting graph
                titleSave = 'Complete_Steady_{}'.format(sensorName)
                path = '{}{}{}.jpg'.format(self.pathSavePlot,os.path.sep, titleSave)
                logger.info('Saving JPG of complete signal. Title is {}.jpg'.format(titleSave))
                figure.savefig(path)

                # Exporting CSV
                # Taking into account if ranges have been applied
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append([timeSplitted[x][0], timeSplitted[x][-1]])
                if not np.isnan(np.sum(t)):
                    timeToCSV = ['Time']
                    timeToCSV.extend(t)
                    totalSignal = ['Total Signal']
                    totalSignal.extend(y)
                    steadySignal = ['Steady Signal']
                    steadySignal.extend(steadyData)
                    rows = zip(timeToCSV, totalSignal, steadySignal)
                else:
                    timeRaw = self.testFlight.sensor.get(fileName)[sensorName].timeInitial
                    timeToCSV = ['Time']
                    timeToCSV.extend(timeRaw)
                    totalSignal = ['Total Signal']
                    totalSignal.extend(y)
                    steadySignal = ['Steady Signal']
                    steadySignal.extend(steadyData)
                    totalSignalRange = ['Total Signal with range']
                    y = y.astype(object)
                    y[np.where(np.isnan(t))] = ''
                    totalSignalRange.extend(y)
                    steadySignalRange = ['Steady Signal with range']
                    steadyData = steadyData.astype(object)
                    steadyData[np.where(np.isnan(t))] = ''
                    steadySignalRange.extend(steadyData)
                    rows = zip(timeToCSV, totalSignal, steadySignal, totalSignalRange, steadySignalRange)


                path = '{}{}{}.csv'.format(self.pathSavePlot,os.path.sep, titleSave)
                logger.info('Saving CSV of complete signal. Title is {}.csv'.format(titleSave))

                with open(path, 'w', newline='') as csvFile:
                    csvFile.write('################################################\n')
                    csvFile.write('# File: {}\n'.format(fileName))
                    csvFile.write('# Sensor: {}\n'.format(sensorName))
                    try:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(self.dictReference[sensorName]))
                    except:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(np.nan))
                    try:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(self.dictReferenceTXT[sensorName]))
                    except:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(np.nan))
                    csvFile.write('# Step: {}\n'.format(step))
                    csvFile.write('# Overlap: {}\n'.format(overlap))
                    for m in range(len(rangesToCSV)):
                        csvFile.write(
                            '# Range {} [s]: [{:.2f}-{:.2f}]\n'.format(m, rangesToCSV[m][0], rangesToCSV[m][1]))
                    timeFlight = self.testFlight.nameFiles[fileName].time_year
                    timeFlight1 = timeFlight[~np.isnan(timeFlight)][0]
                    timeFlight2 = timeFlight[~np.isnan(timeFlight)][-1]
                    csvFile.write('# Time of Flight: {}-{} [s]\n'.format(timeFlight1, timeFlight2))
                    csvFile.write('################################################\n')
                    writer = csv.writer(csvFile, delimiter=',')
                    for row in rows:
                        writer.writerow(row)
                logger.info('****************************************')
            else:
                pass

        if not self.savePlot:
            if numberOfSensors >= 1:
                title = 'Complete signal - Time [s]'
                axesToPlot.set_title(title)
                figure.suptitle('Complete signal', fontsize=13)
                ax1.legend(lines, [l.get_label() for l in lines])
            self.MplWidget.removePlot()
            self.MplWidget.addPlot(figure)


        else:
            pass

    def selectRangeDynamically(self):
        self.condSelParList.clear()
        self.groupCondSel.setHidden(False)
        self.manualTime = False
        figure = self.MplWidget.canvas.figure
        self.MplWidget.selectPointPlot(figure, self.condSelParList)

    def currentView(self):
        '''
        Selecting current x axes directly from plot. The limits will be written in the cut data frame
        so the user could click on apply and cut all data from all the CDFs.
        '''

        self.manualTime = True
        self.groupCondSel.setHidden(True)
        self.manualSelectTimeFrame.setHidden(False)
        # Reading X limits
        xlbl = self.MplWidget.canvas.figure.axes[0].get_xlim()
        lowTimeValue = xlbl[0]
        highTimeValue = xlbl[1]

        logger.info('Limits of current plot window has been written in Range1-ti and Range2-te')
        logger.info('Min x: {0:.2f}'.format(lowTimeValue))
        logger.info('Max x: {0:.2f}'.format(highTimeValue))
        logger.info('****************************************')

        # Printing them in lowTimeValue1 and highTimeValue1 QTextEdit
        self.lowTimeValue1.setPlainText(str("{0:.2f}".format(lowTimeValue)))
        self.highTimeValue1.setPlainText(str("{0:.2f}".format(highTimeValue)))

    def exportAllData(self):
        '''
        Export all raw data of every CDF that has been loaded in format CSV
        '''

        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        pathDirectory = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Save CSV with all data', os.getenv('HOME'))
        if pathDirectory != '':
            logger.info('Exporting raw data and RMS values of all sensors to {}'.format(pathDirectory))
            logger.info('- Sensors are exported without resample, ranges of time, conditional...')
            logger.info('- Only offset will be applied in written data (if it was applied)')
            logger.info('Please wait until the process is finished...')

            # Loop through all selected CDF files
            totalFilesCount = self.fileSelect.count()
            for index in range(totalFilesCount):
                logger.info('Total percentage completed: {:.2f}%'.format(index/totalFilesCount*100))
                indexSpace = self.fileSelect.item(index).text().find(' ')
                numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
                fileName = self.fileSelect.item(index).text()[:indexSpace]

                # Making the sensor GMT the first value in the list, so it is the first column in the CSV
                listNameSensors = list(self.test_flights_save.sensor[fileName].keys())
                try:
                    listNameSensors.remove('GMT')
                except:
                    pass
                listNameSensors.insert(0, 'GMT')

                pathRMS = '{}\RMS_{}.csv'.format(pathDirectory, fileName[:-4])
                with open(pathRMS, 'w', newline='') as csvFile:
                    # Writing header of the CSV
                    writer = csv.writer(csvFile)
                    sample = self.testFlight.nameFiles[fileName].sampleRate
                    writer.writerow(['##################'])
                    writer.writerow(['## File name: {}'.format(fileName)])
                    writer.writerow(['## Sample: {}'.format(sample)])
                    writer.writerow(['## Step: {} s'.format(step)])
                    writer.writerow(['## Overlap: {} s'.format(overlap)])
                    writer.writerow(['##################'])

                    # Saving RMS.
                    RMSData = []
                    sensorList = []
                    for sensorName in listNameSensors:
                        data = self.test_flights_save.sensor.get(fileName)[sensorName].data
                        if data.shape[0] == 0:
                            pass
                        else:
                            sensorList.append(sensorName)
                            RMS, N0 = self.test_flights_save.RMS_loads(fileName, sensorName, overlap, step)
                            RMSData.append(RMS)
                    writer.writerow(sensorList)
                    writer.writerow(RMSData)
                csvFile.close()

                pathRawData = '{}\{}.csv'.format(pathDirectory, fileName[:-4])
                with open(pathRawData, 'w', newline='') as csvFile:
                    # Writing header of the CSV
                    writer = csv.writer(csvFile)
                    sample = self.testFlight.nameFiles[fileName].sampleRate
                    writer.writerow(['##################'])
                    writer.writerow(['## File name: {}'.format(fileName)])
                    writer.writerow(['## Sample: {}'.format(sample)])
                    writer.writerow(['##################'])

                    # Saving in a list all data from every sensor.
                    sensorRawData = []
                    sensorList = []
                    for sensorName in listNameSensors:
                        if sensorName == 'GMT':
                            sensorList.append(sensorName)
                            data = self.test_flights_save.sensor.get(fileName)[sensorName].time
                            sensorRawData.append(data)
                        else:
                            data = self.test_flights_save.sensor.get(fileName)[sensorName].data
                            if data.shape[0] == 0:
                                pass
                            else:
                                sensorList.append(sensorName)
                                sensorRawData.append(data)
                    writer.writerow(sensorList)
                    # Aggregating data and writing it.
                    zipSensorRawData = zip(*sensorRawData)
                    for line in zipSensorRawData:
                        writer.writerow(line)

                csvFile.close()
            logger.info('Process finished correctly.')
            logger.info('****************************************')

    def writeConditionalCSV(self):
        logger.info('Exporting conditional table to CSV...')
        path = PyQt5.QtWidgets.QFileDialog.getSaveFileName(self,'Export conditional CSV',os.getenv('HOME', '.csv'),filter='CSV files (*.csv)')[0]
        logger.info('CSV saved in {}'.format(path))
        if path != '':
            with open(path,'w', newline='') as csvFile:
                writer= csv.writer(csvFile,delimiter = ';')
                # Reading and writing all elements of condSel QTableWidget
                for row in range(self.condSel.rowCount()):
                    rowData = []
                    for column in range(self.condSel.columnCount()):
                        item = self.condSel.item(row,column)
                        if item is not None:
                            rowData.append(item.text())
                        else:
                            rowData.append('')
                    writer.writerow(rowData)
        logger.info('****************************************')

    def readConditionalCSV(self):
        logger.info('Reading conditional from CSV')
        path = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self,'Import conditional CSV',os.getenv('HOME'), filter='CSV files (*.csv)')[0]
        if path != '':
            with open(path,newline='') as csvFile:
                myFile = csv.reader(csvFile,delimiter = ';')
                row = 0
                for rowData in myFile:
                    for column, stuff in enumerate(rowData):
                        if column > 3:
                            pass
                        else:
                            self.condSel.setItem(row, column, PyQt5.QtWidgets.QTableWidgetItem(stuff))
                    row += 1
        logger.info('****************************************')

    def clearConditional(self):
        logger.info('Clearing conditional table and deleting changes made in sensors.')
        logger.info('- Ranges of time deleted')
        logger.info('- Resamples deleted')
        logger.info('- Conditional deleted')
        logger.info('- Filters deleted')
        logger.info('- Offset NOT deleted')

        # Clearing main plot
        self.clearPlotMainWindow()
        # Using original data with reference (if it was applied)
        self.testFlight = copy.deepcopy(self.test_flights_save)

        # Clearing condSel QtableWidget and condSelParList QListWidget
        self.condSelParList.clear()
        self.condSel.clearContents()

        # Using original data
        self.testFlight.mask = self.test_flights_save.mask
        logger.info('****************************************')

    def conditionalPlot(self):
        logger.info('Applying conditinal to all CDF files selected...')

        # Reading limits of condSel QTableWidget
        columnCount = self.condSel.columnCount()
        rowCount = self.condSel.rowCount()

        parameters = []
        conditions = []
        values = []

        for col in range(columnCount):
            for row in range(rowCount):
                # If some item of the first row is empty
                if (self.condSel.item(row, col) is None) or (self.condSel.item(row, col).text()== ''):
                    break
                else:
                    # Reading data
                    item = self.condSel.item(row, col)
                    itemText = item.text()
                    # Depending on column it will be a different item

                    if col == 0:
                        # Col = 0 -> the parameter that is going to be filtered by the conditional
                        # Format : string with name of sensor
                        sensorName = itemText
                        parameters.append(sensorName)

                    elif col == 1:
                        # Col = 1 -> symbol >, < or ==
                        conditions.append(itemText)
                    else:
                        # Col = 2 -> value
                        values.append(itemText)

        # Loop through all elements that user want to use as a filter
        # A mask is going to be created so that all the conditionals are applied at the same time
        logger.info('CDFs modified are:')
        for index in self.fileSelect.selectedIndexes():
            indexSpace = self.fileSelect.item(index.row()).text().find(' ')
            numberFile = self.fileSelect.item(index.row()).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index.row()).text()[:indexSpace]
            logger.info(fileName)

            countSensor = 0
            for index in range(len(parameters)):
                sensorName = parameters[index]
                if countSensor == 0:
                    mask = np.ones(self.testFlight.sensor[fileName][sensorName].data.shape[0])
                data = self.testFlight.sensor.get(fileName)[sensorName].data
                if conditions[index] == '<':
                    maskAux = (data < float(values[index])).astype(bool)
                elif conditions[index] == '>':
                    maskAux = (data > float(values[index])).astype(bool)
                else:
                    maskAux = (data == float(values[index])).astype(bool)

                mask = mask * maskAux
                mask = mask.astype(bool)

                countSensor += 1

            for sensorName in self.testFlight.sensor[fileName].keys():
                try:
                    timeSensor = self.testFlight.sensor[fileName][sensorName].time
                    timeSensor[mask==False] = np.nan
                    self.testFlight.sensor.get(fileName)[sensorName].time = timeSensor
                except:
                    logger.info('There was a problem applying conditional to sensor {} of file {}'.format(sensorName, fileName))
        self.groupCondSel.setHidden(True)
        self.filterDisplacementFrame.setHidden(True)
        # Applying plot to Main Window
        self.checkPlotMain()
        logger.info('****************************************')

    def clearPlotMainWindow(self):
        '''
        Clear the figure of Main Window
        '''
        logger.info('Plot cleared')
        self.MplWidget.removePlot()

    def resample(self):
        '''
        Applying resample to all the sensors of selected CDF files
        '''
        # Value of the resample
        resampleValue = int(float(self.resampleValue.toPlainText()))
        logger.info('Applying resample of {} hz to all data'.format(resampleValue))
        logger.info('- Warning: if some range of time or conditional was applied, it will be deleted.')

        # Saving all selected CDFs
        for index in self.fileSelect.selectedIndexes():
            indexSpace = self.fileSelect.item(index.row()).text().find(' ')
            numberFile = self.fileSelect.item(index.row()).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index.row()).text()[:indexSpace]
            self.testFlight.nameFiles[fileName].sampleRate = int(resampleValue)
            for sensorName in self.testFlight.sensor[fileName].keys():
                self.testFlight.sensor[fileName][sensorName].resampleRate(resampleValue)

        # Applying plot
        self.checkPlotMain()

    def selectManRangeTime(self):
        self.manualSelectTimeFrame.setHidden(False)
        self.manualTime = True
        self.groupCondSel.setHidden(True)


    def applyRangeTime(self):
        '''
        Applying cut data to selected CDFs files
        '''
        self.manualSelectTimeFrame.setHidden(True)
        self.groupCondSel.setHidden(True)
        logger.info('Cutting Data...')

        rangeTime = []

        # Saving all selected CDFs
        fileNameList = []
        for index in self.fileSelect.selectedIndexes():
            indexSpace = self.fileSelect.item(index.row()).text().find(' ')
            numberFile = self.fileSelect.item(index.row()).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index.row()).text()[:indexSpace]
            fileNameList.append(fileName)

        if self.manualTime:
            # Loop through all selected files
            for fileName in fileNameList:

                # Reading values of Range 1 of QPlainText.
                lowTimeValue1 = self.lowTimeValue1.toPlainText()
                highTimeValue1 = self.highTimeValue1.toPlainText()
                # If end, last time value is calculated and applied as highTimeValue1
                if highTimeValue1 == 'end':
                    time = self.testFlight.sensor.get(fileName)['GMT'].data-self.testFlight.sensor.get(fileName)['GMT'].data[0]
                    values = copy.deepcopy(time[~np.isnan(time)])
                    highTimeValue1 = values[-1]
                else:
                    pass

                logger.info('Range 1: {}-{} [s]'.format(lowTimeValue1, highTimeValue1))

                # Changing to float both times. Attribute self.ranteTime is created so it could have been used in other methods
                lowTimeValue1 = float(lowTimeValue1)
                highTimeValue1 = float(highTimeValue1)
                rangeTime1 = [lowTimeValue1, highTimeValue1]
                rangeTime.append(rangeTime1)

                # Reading values of Range 2 of QPlainText.
                lowTimeValue2 = self.lowTimeValue2.toPlainText()
                highTimeValue2 = self.highTimeValue2.toPlainText()

                # If one of both values are empty, pass.
                if (highTimeValue2 == '') or (lowTimeValue2==''):
                    pass
                else:
                    # If end, last time value is calculated and applied as highTimeValue2
                    if highTimeValue2 == 'end':
                        time = self.testFlight.sensor.get(fileName)['GMT'].data-self.testFlight.sensor.get(fileName)['GMT'].data[0]
                        values = copy.deepcopy(time[~np.isnan(time)])
                        highTimeValue2 = values[-1]
                    else:
                        pass
                    # Changing to float both times. Attribute self.ranteTime is created so it could have been used in other methods
                    lowTimeValue2 = float(lowTimeValue2)
                    highTimeValue2 = float(highTimeValue2)
                    rangeTime2 = [lowTimeValue2, highTimeValue2]
                    rangeTime.append(rangeTime2)

                    logger.info('Range 2: {}-{} [s]'.format(lowTimeValue2, highTimeValue2))

                # Reading values of Range 3 of QPlainText.
                lowTimeValue3 = self.lowTimeValue3.toPlainText()
                highTimeValue3 = self.highTimeValue3.toPlainText()

                # If one of both values are empty, pass.
                if (highTimeValue3 == '') or (lowTimeValue3 == ''):
                    pass
                else:
                    # If end, last time value is calculated and applied as highTimeValue3
                    if highTimeValue3 == 'end':
                        time = self.testFlight.sensor.get(fileName)['GMT'].data-self.testFlight.sensor.get(fileName)['GMT'].data[0]
                        values = copy.deepcopy(time[~np.isnan(time)])
                        highTimeValue3 = values[-1]
                    else:
                        pass
                    # Changing to float both times. Appending to attribute self.ranteTime so it could have been used in other methods
                    lowTimeValue3 = float(lowTimeValue3)
                    highTimeValue3 = float(highTimeValue3)
                    rangeTime3 = [lowTimeValue3, highTimeValue3]
                    rangeTime.append(rangeTime3)
                    logger.info('Range 3: {}-{} [s]'.format(lowTimeValue3, highTimeValue3))

        else:
            for index in range(self.condSelParList.count()):
                lineText = self.condSelParList.item(index).text()
                lineText = lineText.replace(' ', '')
                lineText = lineText.split(':')[1]
                time1, time2 = lineText.split('-')
                whereUnit = time2.find('[')
                time2 = time2[:whereUnit]
                time1 = float(time1)
                time2 = float(time2)
                rangeOfTime = [time1, time2]
                rangeTime.append(rangeOfTime)

        # Cutting data with rangeTime
        # Data is changed from testFlights.sensor
        for sensorName in self.testFlight.sensor[fileName].keys():
            self.testFlight.sensor[fileName][sensorName].cut_data(rangeTime)

        # Plotting data
        self.checkPlotMain()
        logger.info('Process finished correctly')
        logger.info('****************************************')

    def filterFreq(self):
        '''
        Applying filter of frequency to selected sensors
        '''
        logger.info('Applying filter to selected sensors...')

        # Saving selected sensors and their number reference
        sensorNameList = []
        fileNumberList = []
        for index in self.paramSel.selectedIndexes():
            sensorNameList.append(self.paramSel.item(index.row(), 0).text())
            fileNumberList.append(self.paramSel.item(index.row(), 1).text())

        # Saving file name taking into account the number reference
        fileNameList = []
        for fileNumber in fileNumberList:
            fileNameList.append(self.fileSelectedDict[fileNumber])

        # Reading values of filter
        lowValue = self.lowValue.toPlainText()
        highValue = self.highValue.toPlainText()
        orderValue = self.orderValue.toPlainText()

        for index in range(len(sensorNameList)):
            sensorName = sensorNameList[index]
            fileName = fileNameList[index]
            self.testFlight.sensor[fileName][sensorName].applyFilter(highValue, lowValue, orderValue)

            logger.info('Process finished correctly')
        logger.info('****************************************')

        self.checkPlotMain()

    def clearAll(self):
        '''
        Reset all parameters as they were when the CDFs were loaded. Reference is applied yet, if user wants to delete it,
        please, apply function self.clearReference()
        '''
        logger.info('Reseting main tab:')
        logger.info('- Resample deleted')
        logger.info('- Filters deleted')
        logger.info('- Ranges of time deleted')
        logger.info('- Conditionals deleted')
        logger.info('- Offset deleted')
        logger.info('- Created sensors deleted')

        # Clearing main window plot
        self.clearPlotMainWindow()

        # Clearing paramSel QTableWidget content
        self.paramSel.clearContents()

        # Setting step QTextEdit to 1
        self.stepMovingAvarage.setPlainText('1')
        self.stepMovingAvarage.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        # Setting overlap QTextEdit to 0
        self.overlapMovingAvarge.setPlainText('0')
        self.overlapMovingAvarge.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        # Setting values of QTextEdit of Filter QFrame
        self.lowValue.setPlainText('High pass')
        self.lowValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highValue.setPlainText('Low pass')
        self.highValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.orderValue.setPlainText('n')
        self.orderValue.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        # Saving initial data, with reference applied if user applied it.
        self.testFlight = copy.deepcopy(self.test_flights_save)
        # Setting values of QTextEdit of Specify time QFrame
        self.lowTimeValue1.setPlainText('')
        self.lowTimeValue1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highTimeValue1.setPlainText('')
        self.highTimeValue1.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.lowTimeValue2.setPlainText('')
        self.lowTimeValue2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highTimeValue2.setPlainText('')
        self.highTimeValue2.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.lowTimeValue3.setPlainText('')
        self.lowTimeValue3.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highTimeValue3.setPlainText('')
        self.highTimeValue3.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.lowFreqDisp.setPlainText('10')
        self.lowFreqDisp.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.highFreqDisp.setPlainText('250')
        self.highFreqDisp.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        # Clearing all the modifications
        self.testFlight = copy.deepcopy(self.test_flights_save_no_reference)
        self.test_flights_save = copy.deepcopy(self.test_flights_save_no_reference)

        self.dictReferenceTXT = np.nan
        self.dictReference = np.nan

        self.groupCondSel.setHidden(True)
        self.manualTime = False
        self.condSelParList.clear()

        # Setting number of rows of paramSel QTableWidget
        numberRows = 0
        for index in self.fileSelect.selectedIndexes():
            index = index.row()
            indexSpace = self.fileSelect.item(index).text().find(' ')
            numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index).text()[:indexSpace]
            numberRows += len(self.testFlight.sensor.get(fileName).keys())
        self.paramSel.setRowCount(numberRows)

        # Inserting all sensors of selected CDF files in paramSel QTableWidget
        i = 0
        # Loop through all selected CDFs
        for index in self.fileSelect.selectedIndexes():
            index = index.row()
            indexSpace = self.fileSelect.item(index).text().find(' ')
            numberFile = self.fileSelect.item(index).text()[indexSpace + 3:]
            fileName = self.fileSelect.item(index).text()[:indexSpace]

            # Loop through all sensors in every CDF
            for sensor_name in self.testFlight.sensor.get(fileName).keys():
                fullName = self.testFlight.parameters[fileName][sensor_name][0]
                units = self.testFlight.parameters[fileName][sensor_name][1]

                self.paramSel.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(sensor_name))
                self.paramSel.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(units))
                self.paramSel.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(numberFile))
                self.paramSel.setItem(i, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName))
                i += 1

        # Clearing condSel QtableWidget and condSelParList QListWidget
        self.condSelParList.clear()
        self.condSel.clearContents()
        self.savePlot = False
        logger.info('Process finished correctly')
        logger.info('****************************************')

    def condSel_cell_changed(self, row, col):
        '''
        Method to check if text written in colum == 2 of condSel QTableWidget is a float
        '''
        # Checking if is col == 2
        if col == 2:
            row = self.condSel.currentRow()
            col = self.condSel.currentColumn()
            temp = self.condSel.item(row, col)
            # Checking if the text written could be set as float
            try:
                float(temp.text())
            except ValueError:
                self.condSel.setItem(row, col, PyQt5.QtWidgets.QTableWidgetItem(''))
            except AttributeError:
                pass


    def condSel_single_click(self, row, col):
        '''
        Method to do different actions when single clicking in col == 0 or col == 1 of condSel QTableWidget
        '''
        # Clearing condSelParList QListWidget (where all the possibilities to choose appear)
        self.condSelParList.clear()
        # If first column clicked...
        if col == 0:
            # groupCondSel QFrame appears
            self.groupCondSel.setHidden(False)
            # All sensors that are displayed in paramSel QTableWidget are possibilities to chose, so they will appear in
            # conSelParList QListWidget
            sensorToAdd = []
            for fileName in self.fileSelect.selectedItems():
                indexSpace = fileName.text().find(' ')
                fileNumber = fileName.text()[indexSpace + 3:]
                fileName = fileName.text()[:indexSpace]
                for sensorName in self.testFlight.sensor.get(fileName).keys():
                    if sensorName not in sensorToAdd:
                        sensorToAdd.append(sensorName)
                        self.condSelParList.insertItem(0, PyQt5.QtWidgets.QListWidgetItem(sensorName))
            self.condSel.setEnabled(False)

        # If second column clicked...
        elif col == 1:
            # groupCondSel QFrame appears
            self.groupCondSel.setHidden(False)
            # Adding all the possibilities of comparing
            self.condSelParList.insertItem(0, PyQt5.QtWidgets.QListWidgetItem('{:s}'.format('>')))
            self.condSelParList.insertItem(1, PyQt5.QtWidgets.QListWidgetItem('{:s}'.format('<')))
            self.condSelParList.insertItem(2, PyQt5.QtWidgets.QListWidgetItem('{:s}'.format('==')))
            self.condSel.setEnabled(False)

        else:
            pass

    def condSelParList_single_click(self,X):
        '''
        Method to select elements of conSelParList QListWidget
        '''
        row = self.condSel.currentRow()
        col = self.condSel.currentColumn()
        self.condSel.setItem(row, col, PyQt5.QtWidgets.QTableWidgetItem(X.text()))
        self.groupCondSel.setHidden(False)
        self.condSel.setEnabled(True)

    def plotSteadySignalMainWindow(self):
        '''
        Plotting STEADY SIGNAL in main window
        '''

        figure = Figure(constrained_layout= True)
        ax1 = figure.add_subplot(111)

        # Hidding groupSelectionPlotAll QTableWidget -> Ranges of plotAllSignalsMain
        self.groupSelectionPlotAll.setHidden(True)
        self.filterDisplacementFrame.setHidden(True)

        # Counting number of sensors
        numberOfSensors = len(self.paramSel.selectedItems())

        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Loop through all sensors...
        lines = []
        for i in range(numberOfSensors):
            # Reading characteristics of every sensor
            index = self.paramSel.selectedIndexes()[i]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Saving time, step, overlap and steady signal
            t = self.testFlight.sensor.get(fileName)[sensorName].time
            steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

            # Checking names that are going to be used in title, legend...
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Taking into account what axes is going to be used and the position of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                # Plotting
                figure.suptitle('Steady signal', fontsize=13)
                p, = axesToPlot.plot(t, steadyData, color='C{}'.format(i),
                                     label='{} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p)

                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Steady signal')
            else:
                if i==0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                    axesToPlot.spines['right'].set_position(('axes', 0.9 + 0.1 * i))

                # Plotting
                figure.suptitle('Steady signal', fontsize=13)
                p, = axesToPlot.plot(t, steadyData, color='C{}'.format(i),
                                     label='{} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p)

                # Changing color properties of the plot
                axesToPlot.yaxis.label.set_color(p.get_color())
                tkw = dict(size=4, width=1.5)
                axesToPlot.tick_params(axis='y', colors=p.get_color(), **tkw)

                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Steady signal of {} - [{}]'.format(nameToPlot,units))

            # If user want to export data...
            if self.savePlot:
                title = 'Steady signal - Time [s]. Step = {}s. Overlap = {}%'.format(step, overlap)
                axesToPlot.set_title(title)
                axesToPlot.legend()
                titleSave = 'Steady_{}'.format(sensorName)

                # Exporting graph...
                path = '{}{}{}.jpg'.format(self.pathSavePlot,os.path.sep, titleSave)
                logger.info('Saving JPG of steady signal. Title is {}.jpg'.format(titleSave))
                figure.savefig(path)

                # Exporting CSV...
                # Taking into account if there are ranges of time

                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append([timeSplitted[x][0], timeSplitted[x][-1]])
                if not np.isnan(np.sum(t)):
                    timeToCSV = ['Time']
                    steadySignal = ['Steady Signal']
                    timeToCSV.extend(t)
                    steadySignal.extend(steadyData)
                    rows = zip(timeToCSV, steadySignal)
                else:
                    rawTime = self.testFlight.sensor.get(fileName)[sensorName].timeInitial
                    timeToCSV = ['Time']
                    timeToCSV.extend(rawTime)
                    steadySignal = ['Steady Signal']
                    steadySignal.extend(steadyData)
                    steadySignalRange = ['Steady Signal with range']
                    steadyData = steadyData.astype(object)
                    steadyData[np.where(np.isnan(t))] = ''
                    steadySignalRange.extend(steadyData)
                    rows = zip(timeToCSV, steadySignal, steadySignalRange)


                path = '{}\{}.csv'.format(self.pathSavePlot, titleSave)
                logger.info('Saving CSV of steady signal. Title is {}.csv'.format(titleSave))

                with open(path, 'w', newline='') as csvFile:
                    csvFile.write('################################################\n')
                    csvFile.write('# File: {}\n'.format(fileName))
                    csvFile.write('# Sensor: {}\n'.format(sensorName))
                    try:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(self.dictReference[sensorName]))
                    except:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(np.nan))
                    try:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(self.dictReferenceTXT[sensorName]))
                    except:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(np.nan))
                    csvFile.write('# Step: {}\n'.format(step))
                    csvFile.write('# Overlap: {}\n'.format(overlap))
                    for m in range(len(rangesToCSV)):
                        csvFile.write(
                            '# Range {} [s]: [{:.2f}-{:.2f}]\n'.format(m, rangesToCSV[m][0], rangesToCSV[m][1]))
                    timeFlight = self.testFlight.nameFiles[fileName].time_year
                    timeFlight1 = timeFlight[~np.isnan(timeFlight)][0]
                    timeFlight2 = timeFlight[~np.isnan(timeFlight)][-1]
                    csvFile.write('# Time of Flight: {}-{} [s]\n'.format(timeFlight1, timeFlight2))
                    csvFile.write('################################################\n')
                    writer = csv.writer(csvFile, delimiter=',')
                    for row in rows:
                        writer.writerow(row)
                logger.info('****************************************')
            else:
                pass

        if not self.savePlot:
            if numberOfSensors >= 1:
                title = 'Steady signal - Time [s]. Step = {}s. Overlap = {}%'.format(step, overlap)
                axesToPlot.set_title(title)
                axesToPlot.legend(lines, [l.get_label() for l in lines])
            self.MplWidget.removePlot()
            self.MplWidget.addPlot(figure)
        else:
            pass

    def plotDisplacementMainWindow(self):
        '''
        Plotting DISPLACEMENTS in main window
        '''
        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Hidding groupSelectionPlotAll QTableWidget -> Ranges of plotAllSignalsMain
        self.groupSelectionPlotAll.setHidden(True)
        self.filterDisplacementFrame.setHidden(False)

        # Counting number of sensors
        numberOfSensors = len(self.paramSel.selectedItems())

        lowFreqDisp = float(self.lowFreqDisp.toPlainText())
        highFreqDisp = float(self.highFreqDisp.toPlainText())
        windowFun = self.boxWindowFunDisp.currentText().lower()

        # Loop through all sensors...
        lines = []
        for i in range(numberOfSensors):
            # Reading characteristics of every sensor
            index = self.paramSel.selectedIndexes()[i]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Calculating time and displacements
            t = self.testFlight.sensor.get(fileName)[sensorName].time
            displacements = self.testFlight.sensor[fileName][sensorName].displacements(lowFreqDisp, highFreqDisp,
                                                                                       win=windowFun)

            # Checking what names are going to be used in the title and the legend
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName

            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Taking into account what axes are going to be used and the place of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                # Plotting
                figure.suptitle('Displacements', fontsize=13)
                p, = axesToPlot.plot(t, displacements, color='C{}'.format(i),
                                     label='{} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p)

                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Displacements [mm]')
            else:
                if i==0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                    axesToPlot.spines['right'].set_position(('axes', 0.9 + 0.1 * i))

                # Plotting
                figure.suptitle('Displacements', fontsize=13)
                p, = axesToPlot.plot(t, displacements, color='C{}'.format(i),
                                     label='{} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p)

                # Changing color properties of the plot
                axesToPlot.yaxis.label.set_color(p.get_color())
                tkw = dict(size=4, width=1.5)
                axesToPlot.tick_params(axis='y', colors=p.get_color(), **tkw)

                title = 'Displacements [mm] - Time [s]'
                axesToPlot.set_title(title)
                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Displacements [mm] of {}'.format(nameToPlot))

            # If user want to export data...
            if self.savePlot:
                title = 'Displacements [mm] - Time [s]'
                axesToPlot.set_title(title)
                axesToPlot.legend()
                titleSave = 'Displacements_{}'.format(sensorName)

                # Exporting graph...
                path = '{}{}{}.jpg'.format(self.pathSavePlot,os.path.sep, titleSave)
                logger.info('Saving JPG of displacements. Title is {}.jpg'.format(titleSave))
                figure.savefig(path)

                # Exporting CSV...
                # Checking if there are ranges of time
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append([timeSplitted[x][0], timeSplitted[x][-1]])
                if not np.isnan(np.sum(t)):
                    timeToCSV = ['Time']
                    timeToCSV.extend(t)
                    displacementToCSV = ['Displacements']
                    displacementToCSV.extend(displacements)
                    rows = zip(timeToCSV, displacementToCSV)
                else:
                    rawTime = self.testFlight.sensor.get(fileName)[sensorName].timeInitial
                    timeToCSV = ['Time']
                    timeToCSV.extend(rawTime)
                    displacementToCSV = ['Displacements']
                    displacementToCSV.extend(displacements)
                    displacementToCSVRange = ['Displacements with range']
                    displacements = displacements.astype(object)
                    displacements[np.where(np.isnan(t))] = ''
                    displacementToCSVRange.extend(displacements)
                    rows = zip(timeToCSV, displacementToCSV, displacementToCSVRange)

                path = '{}\{}.csv'.format(self.pathSavePlot, titleSave)
                logger.info('Saving CSV of displacements. Title is {}.csv'.format(titleSave))

                with open(path, 'w', newline='') as csvFile:
                    csvFile.write('################################################\n')
                    csvFile.write('# File: {}\n'.format(fileName))
                    csvFile.write('# Sensor: {}\n'.format(sensorName))
                    try:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(self.dictReference[sensorName]))
                    except:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(np.nan))
                    try:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(self.dictReferenceTXT[sensorName]))
                    except:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(np.nan))
                    csvFile.write('# Step: {}\n'.format(np.nan))
                    csvFile.write('# Overlap: {}\n'.format(np.nan))
                    for m in range(len(rangesToCSV)):
                        csvFile.write(
                            '# Range {} [s]: [{:.2f}-{:.2f}]\n'.format(m, rangesToCSV[m][0], rangesToCSV[m][1]))
                    timeFlight = self.testFlight.nameFiles[fileName].time_year
                    timeFlight1 = timeFlight[~np.isnan(timeFlight)][0]
                    timeFlight2 = timeFlight[~np.isnan(timeFlight)][-1]
                    csvFile.write('# Time of Flight: {}-{} [s]\n'.format(timeFlight1, timeFlight2))
                    csvFile.write('################################################\n')
                    writer = csv.writer(csvFile, delimiter=',')
                    for row in rows:
                        writer.writerow(row)
                logger.info('****************************************')
            else:
                pass

        if not self.savePlot:
            if numberOfSensors >= 1:
                title = 'Displacements [mm] - Time [s]'
                axesToPlot.set_title(title)
                axesToPlot.legend(lines, [l.get_label() for l in lines])
            self.MplWidget.removePlot()
            self.MplWidget.addPlot(figure)
        else:
            pass

    def plotVibrationsMainWindow(self):
        '''
            Plotting VIBRATIONS in main window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Hidding groupSelectionPlotAll QTableWidget -> Ranges of plotAllSignalsMain
        self.groupSelectionPlotAll.setHidden(True)
        self.filterDisplacementFrame.setHidden(True)

        # Counting number of sensors
        numberOfSensors = len(self.paramSel.selectedItems())

        # Saving time, step, overlap and vibrations
        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Loop through all sensors...
        lines = []
        for i in range(numberOfSensors):
            # Reading characteristics of every sensor
            index = self.paramSel.selectedIndexes()[i]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]


            t = self.testFlight.sensor.get(fileName)[sensorName].time
            vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)

            # Checking what names are going to be used in the title and the legend
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Checking what axes are going to be used and the place of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                # Plotting
                figure.suptitle('Vibrations', fontsize=13)
                p, = axesToPlot.plot(t, vibrations, 'C{}'.format(i),
                                     label='{} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p)

                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Vibration')
            else:
                if i == 0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                    axesToPlot.spines['right'].set_position(('axes', 0.9 + 0.1 * i))

                # Plotting
                figure.suptitle('Vibrations', fontsize=13)
                p, = axesToPlot.plot(t, vibrations, 'C{}'.format(i),
                                     label='{} {} [{}]'.format(nameToPlot, numberFile, units))
                lines.append(p)

                # Changing color properties of the plot
                axesToPlot.yaxis.label.set_color(p.get_color())
                tkw = dict(size=4, width=1.5)
                axesToPlot.tick_params(axis='y', colors=p.get_color(), **tkw)

                axesToPlot.set_xlabel('Time [s]')
                axesToPlot.set_ylabel('Vibration of {}'.format(nameToPlot))

            # If user wants to export data...
            if self.savePlot:
                title = 'Vibration signal - Time [s]'
                axesToPlot.set_title(title)
                axesToPlot.legend()
                titleSave = 'Vibration_{}'.format(sensorName)

                # Exporting graph...
                path = '{}{}{}.jpg'.format(self.pathSavePlot,os.path.sep, titleSave)
                logger.info('Saving JPG of vibration. Title is {}.jpg'.format(titleSave))
                figure.savefig(path)

                # Exporting CSV...
                # Taking into account if there are ranges of time
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append([timeSplitted[x][0], timeSplitted[x][-1]])

                if not np.isnan(np.sum(t)):
                    timeToCSV = ['Time']
                    vibrationSignal = ['Vibration']
                    timeToCSV.extend(t)
                    vibrationSignal.extend(vibrations)
                    rows = zip(timeToCSV, vibrationSignal)
                else:
                    rawTime = self.testFlight.sensor.get(fileName)[sensorName].timeInitial
                    timeToCSV = ['Time']
                    timeToCSV.extend(rawTime)
                    vibrationSignal = ['Vibration']
                    vibrationSignal.extend(vibrations)
                    vibrationSignalRange = ['Vibration with ranges']
                    vibrations = vibrations.astype(object)
                    vibrations[np.where(np.isnan(t))] = ''
                    vibrationSignalRange.extend(vibrations)
                    rows = zip(timeToCSV, vibrationSignal, vibrationSignalRange)

                path = '{}\{}.csv'.format(self.pathSavePlot, titleSave)
                logger.info('Saving CSV of vibration. Title is {}.csv'.format(titleSave))

                with open(path, 'w', newline='') as csvFile:
                    csvFile.write('################################################\n')
                    csvFile.write('# File: {}\n'.format(fileName))
                    csvFile.write('# Sensor: {}\n'.format(sensorName))
                    try:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(self.dictReference[sensorName]))
                    except:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(np.nan))
                    try:
                        csvFile.write('# Offset applied with TXT: {}\n'.format(self.dictReferenceTXT[sensorName]))
                    except:
                        csvFile.write('# Offset: {}\n'.format(np.nan))
                    csvFile.write('# Step: {}\n'.format(step))
                    csvFile.write('# Overlap: {}\n'.format(overlap))
                    for m in range(len(rangesToCSV)):
                        csvFile.write(
                            '# Range {} [s]: [{:.2f}-{:.2f}]\n'.format(m, rangesToCSV[m][0], rangesToCSV[m][1]))
                    timeFlight = self.testFlight.nameFiles[fileName].time_year
                    timeFlight1 = timeFlight[~np.isnan(timeFlight)][0]
                    timeFlight2 = timeFlight[~np.isnan(timeFlight)][-1]
                    csvFile.write('# Time of Flight: {}-{} [s]\n'.format(timeFlight1, timeFlight2))
                    csvFile.write('################################################\n')
                    writer = csv.writer(csvFile, delimiter=',')
                    for row in rows:
                        writer.writerow(row)
                logger.info('****************************************')
            else:
                pass

        if not self.savePlot:
            if numberOfSensors >= 1:
                title = 'Vibration signal - Time [s]'
                axesToPlot.set_title(title)
                axesToPlot.legend(lines, [l.get_label() for l in lines])
            self.MplWidget.removePlot()
            self.MplWidget.addPlot(figure)
        else:
            pass


    def plotAllSignalsMainWindow(self):
        '''
        Plotting ALL SIGNALS in main window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Showing groupSelectionPlotAll QTableWidget -> Ranges of plotAllSignalsMain
        self.groupSelectionPlotAll.setHidden(False)
        self.filterDisplacementFrame.setHidden(True)

        # checkPlots is a dictionary which pick the values of the ranges user want to plot
        checkPlots = {}
        for i in range(self.selectionPlotAllSignals.rowCount()):
            rowName = 'Range' + str(i)
            checkComplete = int(self.selectionPlotAllSignals.item(i, 0).text())
            checkSteady = int(self.selectionPlotAllSignals.item(i, 1).text())
            checkVibrations = int(self.selectionPlotAllSignals.item(i, 2).text())
            checkPlots[rowName] = [checkComplete, checkSteady, checkVibrations]

        # Counting number of sensors
        numberOfSensors = len(self.paramSel.selectedItems())

        # This kind of plot only allows 1 plot at the samen time
        if numberOfSensors == 1:
            # Reading characteristics of every sensor
            index = self.paramSel.selectedIndexes()[0]
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            numberFile = self.paramSel.item(index.row(), 1).text()
            units = self.paramSel.item(index.row(), 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Saving time, complete data, vibrations, steady, step and overlap
            step = float(self.stepMovingAvarage.toPlainText())
            overlap = float(self.overlapMovingAvarge.toPlainText())
            t = copy.deepcopy(self.testFlight.sensor[fileName][sensorName].time)
            y = copy.deepcopy(self.testFlight.sensor[fileName][sensorName].data)
            vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)
            steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

            # The time is going to be splitted in the ranges the user has definned
            timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]

            # Loop through all ranges of the time. It is going to be checked if the user wants to plot it. If not, nothing is
            # going to be plotted. It has been specially done for Main Landig Gear Door analysis, so if steady or vibrations
            # has been marked as 0, vibrations will be set as 0 and steady signal will be equal as complete data, so that
            # the equation complete = vibration + steady always is correct (condition of stress Airbus)

            # Checking if it is going to be plotted or not
            i = 0
            for timeRange in timeSplitted:
                rangeName = 'Range' + str(i)
                indexRange = []
                for timeValue in timeRange:
                    indexRange.append(np.where(t == timeValue)[0][0])

                if checkPlots[rangeName][1] == 0:
                    steadyData[indexRange] = y[indexRange]
                    vibrations[indexRange] = 0
                else:
                    pass

                if checkPlots[rangeName][2] == 0:
                    steadyData[indexRange] = y[indexRange]
                    vibrations[indexRange] = 0
                else:
                    pass

                if checkPlots[rangeName][0] == 0:
                    y[indexRange] = np.nan
                else:
                    pass

                i += 1

            # Checking what name is going to be used for title and legend
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Plotting

            ax1.plot(t, y, '-b', label='Complete signal')
            ax1.plot(t, steadyData, '-r', label='Steady signal')
            ax1.plot(t, vibrations, '-g', label='Vibrations')
            title = 'C+S+V of sensor {} {}'.format(nameToPlot, numberFile)
            ax1.set_xlabel('Time [s]')
            ax1.set_ylabel('{} [{}]'.format(nameToPlot, units))
            ax1.set_title(title)
            ax1.legend()

            # If user want to export data...
            if self.savePlot:
                figure.suptitle('C+S+V', fontsize=13)
                titleSave = 'C+S+V_{}'.format(sensorName)

                # Exporting graph...
                path = '{}{}{}.jpg'.format(self.pathSavePlot,os.path.sep,titleSave)
                logger.info('Saving JPG of C+S+V. Title is {}.jpg'.format(titleSave))
                figure.savefig(path)

                # Exporting CSV...
                timeRaw = self.testFlight.sensor.get(fileName)[sensorName].timeInitial
                timeToCSV = ['Time']
                timeToCSV.extend(timeRaw)
                totalSignal = ['Total Signal']
                totalSignal.extend(y)
                steadySignal = ['Steady Signal']
                steadySignal.extend(steadyData)
                vibrationSignal = ['Vibration Signal']
                vibrationSignal.extend(vibrations)

                # Taking into account if there are ranges of time
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                rangesToCSV = []
                for x in range(len(timeSplitted)):
                    rangesToCSV.append([timeSplitted[x][0], timeSplitted[x][-1]])

                rows = zip(timeToCSV, totalSignal, vibrationSignal, steadySignal)
                path = '{}\{}.csv'.format(self.pathSavePlot, titleSave)
                logger.info('Saving CSV of C+S+V. Title is {}.csv'.format(titleSave))

                with open(path, 'w', newline='') as csvFile:
                    csvFile.write('################################################\n')
                    csvFile.write('# File: {}\n'.format(fileName))
                    csvFile.write('# Sensor: {}\n'.format(sensorName))
                    try:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(self.dictReference[sensorName]))
                    except:
                        csvFile.write('# Offset applied with CDF: {}\n'.format(np.nan))
                    try:
                        csvFile.write('# Offset: {}\n'.format(self.dictReferenceTXT[sensorName]))
                    except:
                        csvFile.write('# Offset: {}\n'.format(np.nan))
                    csvFile.write('# Step: {}\n'.format(step))
                    csvFile.write('# Overlap: {}\n'.format(overlap))
                    for m in range(len(rangesToCSV)):
                        csvFile.write(
                            '# Range {} [s]: [{:.2f}-{:.2f}]\n'.format(m, rangesToCSV[m][0], rangesToCSV[m][1]))
                    timeFlight = self.testFlight.nameFiles[fileName].time_year
                    timeFlight1 = timeFlight[~np.isnan(timeFlight)][0]
                    timeFlight2 = timeFlight[~np.isnan(timeFlight)][-1]
                    csvFile.write('# Time of Flight: {}-{} [s]\n'.format(timeFlight1, timeFlight2))
                    csvFile.write('################################################\n')
                    writer = csv.writer(csvFile, delimiter=',')
                    for row in rows:
                        writer.writerow(row)
                logger.info('****************************************')
            else:
                pass

        if not self.savePlot:
            self.MplWidget.removePlot()
            self.MplWidget.addPlot(figure)
        else:
            pass

    '''
    ################################################################################################################
    ################################################################################################################

                                                    TIME WINDOW FUNCTIONS

    ################################################################################################################
    ################################################################################################################

    '''
    def timeAnalysis(self):
        '''
        Method that is applied when Time Analysis tab is applied
        '''
        # Clearing listCDFTimeAnalysis QListWidgetItem
        self.listCDFTimeAnalysis.clear()
        # Clearing contents of tableRMS QTableWidget
        self.tableRMS.clearContents()
        # Clearing contents of listSecParamTimeAnalysis QTableWidget
        self.listSecParamTimeAnalysis.clearContents()
        # Clearing contents of listParamTimeAnalysis QTableWidget
        self.listParamTimeAnalysis.clearContents()

        # Copying selected CDF files from fileSelect QListWidget of main window to listCDFTimeAnalysis QListWidget
        for fileName in self.fileSelect.selectedItems():
            self.listCDFTimeAnalysis.addItem(fileName.text())

        # Setting number of rows of listSecParamTimeAnalysis QTableWidget, counting elements of paramSel QTableWidget
        # of main window
        numberRows = self.paramSel.rowCount()
        self.listSecParamTimeAnalysis.setRowCount(numberRows)

        # Inserting all elements in listSecParamTimeAnalysis
        for row in range(numberRows):
            self.listSecParamTimeAnalysis.setItem(row, 0, PyQt5.QtWidgets.QTableWidgetItem(self.paramSel.item(row,0).text()))
            self.listSecParamTimeAnalysis.setItem(row, 1, PyQt5.QtWidgets.QTableWidgetItem(self.paramSel.item(row,1).text()))
            self.listSecParamTimeAnalysis.setItem(row, 2, PyQt5.QtWidgets.QTableWidgetItem(self.paramSel.item(row,2).text()))
            self.listSecParamTimeAnalysis.setItem(row, 3, PyQt5.QtWidgets.QTableWidgetItem(self.paramSel.item(row,3).text()))

        # Writting selected sensors of paramSel QTableWidget in listParamTimeAnalysis QTableWidget
        countSelectedItems = len(self.paramSel.selectedIndexes())
        for i in range(countSelectedItems):
            # Maximum 2 sensors in listParamTimeAnalysis QTableWidget
            if i >= 2:
                pass
            else:
                # Saving properties of all sensors selected
                index = self.paramSel.selectedIndexes()[i]
                sensorName = self.paramSel.item(index.row(), 0).text()
                fileNumber = self.paramSel.item(index.row(), 1).text()
                units = self.paramSel.item(index.row(), 2).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                fileName = self.fileSelectedDict[fileNumber]

                # Counting number of decimals for RMS and N0
                decimalsRMS = int(self.decimalsRMS.toPlainText())

                # Step and overlap are taken of main window, they will be used to calculate RMS and N0
                step = float(self.stepMovingAvarage.toPlainText())
                overlap = float(self.overlapMovingAvarge.toPlainText())

                # Inserting elements in listParamTimeAnalysis QTableWidget
                self.listParamTimeAnalysis.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName))
                self.listParamTimeAnalysis.setItem(i, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName))
                self.listParamTimeAnalysis.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(fileNumber))
                self.listParamTimeAnalysis.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(units))

                # Calculating RMS and N0
                RMS, N0 = self.test_flights_save.RMS_loads(fileName, sensorName, overlap, step)
                RMS = '{:.{decimals}f}'.format(float(RMS), decimals=decimalsRMS)
                N0 = '{:.{decimals}f}'.format(float(N0), decimals=decimalsRMS)

                # Inserting values of RMS and N0 to tableRMS QTableWidget
                self.tableRMS.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName))
                self.tableRMS.setItem(i, 1, PyQt5PyQt5.QtWidgets.QTableWidgetItem(str(RMS)))
                self.tableRMS.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(str(N0)))
                self.tableRMS.setHorizontalHeaderLabels(['Sensor', 'RMS', 'N0'])

        # Resizing all QTableWidgets
        self.listParamTimeAnalysis.resizeColumnToContents(0)
        self.listParamTimeAnalysis.resizeColumnToContents(1)
        self.listParamTimeAnalysis.resizeColumnToContents(2)
        self.listParamTimeAnalysis.resizeColumnToContents(3)
        self.listSecParamTimeAnalysis.resizeColumnToContents(0)
        self.listSecParamTimeAnalysis.resizeColumnToContents(1)
        self.listSecParamTimeAnalysis.resizeColumnToContents(2)
        self.listSecParamTimeAnalysis.resizeColumnToContents(3)

        # Plotting
        self.checkPlotTimeAnalysis()

    def printSecondItemRMS(self):
        '''
        This method has been created to act when the user click on the Second Parameter Selection (listSecParamTimeAnalysis)
        '''

        # Clearing contents of Parameters Selected (listParamTimeAnalysis)
        self.listParamTimeAnalysis.clearContents()
        # Clearing contents of tableRMS
        self.tableRMS.clearContents()

        # Taking first element of paramSel, which is the item of the first row
        index = self.paramSel.selectedIndexes()[0]
        sensorName1 = self.paramSel.item(index.row(), 0).text()
        fileNumber1 = self.paramSel.item(index.row(), 1).text()
        units1 = self.paramSel.item(index.row(), 2).text()
        fullName1 = self.paramSel.item(index.row(), 3).text()
        fileName1 = self.fileSelectedDict[fileNumber1]

        # Writing first item in Parameters Selected (listParamTimeAnalysis)
        self.listParamTimeAnalysis.setItem(0, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName1))
        self.listParamTimeAnalysis.setItem(0, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName1))
        self.listParamTimeAnalysis.setItem(0, 1, PyQt5.QtWidgets.QTableWidgetItem(fileNumber1))
        self.listParamTimeAnalysis.setItem(0, 2, PyQt5.QtWidgets.QTableWidgetItem(units1))

        # Reading number of decimals to take into account for RMS and N0
        decimalsRMS = int(self.decimalsRMS.toPlainText())
        # Reading step and overlap to calculate RMS and N0
        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Calculating RMS and N0 of the first item
        RMS1, N01 = self.testFlight.RMS_loads(fileName1, sensorName1,overlap, step)
        RMS1 = '{:.{decimals}f}'.format(float(RMS1), decimals=decimalsRMS)
        N01 = '{:.{decimals}f}'.format(float(N01), decimals=decimalsRMS)

        # Inserting calculated RMS and N0 of first item
        self.tableRMS.setItem(0, 1, PyQt5.QtWidgets.QTableWidgetItem(str(RMS1)))
        self.tableRMS.setItem(0, 2, PyQt5.QtWidgets.QTableWidgetItem(str(N01)))
        self.tableRMS.setItem(0, 0, PyQt5.QtWidgets.QTableWidgetItem(str(sensorName1)))

        if len(self.listSecParamTimeAnalysis.selectedIndexes()) > 0:
            # Selecting data of sensor that has been selected in Second Parameter Selection (listSecParamTimeAnalysis)
            index2 = self.listSecParamTimeAnalysis.selectedIndexes()[0]
            sensorName2 = self.listSecParamTimeAnalysis.item(index2.row(), 0).text()
            fileNumber2 = self.listSecParamTimeAnalysis.item(index2.row(), 1).text()
            units2 = self.listSecParamTimeAnalysis.item(index2.row(), 2).text()
            fullName2 = self.listSecParamTimeAnalysis.item(index2.row(), 3).text()
            fileName2 = self.fileSelectedDict[fileNumber2]

            # Inserting values in Parameters Selected
            self.listParamTimeAnalysis.setItem(1, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName2))
            self.listParamTimeAnalysis.setItem(1, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName2))
            self.listParamTimeAnalysis.setItem(1, 1, PyQt5.QtWidgets.QTableWidgetItem(fileNumber2))
            self.listParamTimeAnalysis.setItem(1, 2, PyQt5.QtWidgets.QTableWidgetItem(units2))

            # Calculating RMS2 and N02
            RMS2, N02 = self.testFlight.RMS_loads(fileName2, sensorName2,overlap, step)
            RMS2 = '{:.{decimals}f}'.format(float(RMS2), decimals=decimalsRMS)
            N02 = '{:.{decimals}f}'.format(float(N02), decimals=decimalsRMS)

            # Inserting elements in tableRMS
            self.tableRMS.setItem(1, 1, PyQt5.QtWidgets.QTableWidgetItem(str(RMS2)))
            self.tableRMS.setItem(1, 2, PyQt5.QtWidgets.QTableWidgetItem(str(N02)))
            self.tableRMS.setItem(1, 0, PyQt5.QtWidgets.QTableWidgetItem(str(sensorName2)))

        # Resizing Parameter Selected table (listParamTimeAnalysis)
        self.listParamTimeAnalysis.resizeColumnToContents(0)
        self.listParamTimeAnalysis.resizeColumnToContents(1)
        self.listParamTimeAnalysis.resizeColumnToContents(2)
        self.listParamTimeAnalysis.resizeColumnToContents(3)

        # Plotting
        self.checkPlotTimeAnalysis()

    def decimalsChanged(self):
        # Clearing contents of tableRMS QTableWidget
        self.tableRMS.clearContents()

        # Counting number of filled rows in Parameters Selected (listParamTimeAnalysis). To do this task,
        # both rows will have to be filled.
        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())
        decimalsRMS = int(self.decimalsRMS.toPlainText())

        for i in range(numberRowsFull):
            # Taking first element of listParamTimeAnalysis, which is the item of the first row
            sensorName = self.listParamTimeAnalysis.item(i, 0).text()
            fileNumber = self.listParamTimeAnalysis.item(i, 1).text()
            units = self.listParamTimeAnalysis.item(i, 2).text()
            fullName = self.listParamTimeAnalysis.item(i, 3).text()
            fileName = self.fileSelectedDict[fileNumber]

            # Calculating RMS and N0 of the first item
            RMS, N0 = self.testFlight.RMS_loads(fileName, sensorName, overlap, step)
            RMS = '{:.{decimals}f}'.format(float(RMS), decimals=decimalsRMS)
            N0 = '{:.{decimals}f}'.format(float(N0), decimals=decimalsRMS)

            # Inserting elements in tableRMS
            self.tableRMS.setItem(i, 1, PyQt5.QtWidgets.QTableWidgetItem(str(RMS)))
            self.tableRMS.setItem(i, 2, PyQt5.QtWidgets.QTableWidgetItem(str(N0)))
            self.tableRMS.setItem(i, 0, PyQt5.QtWidgets.QTableWidgetItem(str(sensorName)))

        self.checkPlotTimeAnalysis()

    def checkPlotTimeAnalysis(self):
        '''
        This method has been created to check what kind of plot the user wants to do, depending on what button is
        clicked in Time Analysis Tab. If Main tab selection is clicked -> the same plot of Main Tab will be plotted, else,
        convex hull or main axis will be plotted. Take into account that it will be necessary 2 sensors selected
        to do two last plots mentioned.
        '''

        if self.checkConvexHull.isChecked():
            self.plotConvexHull()
        elif self.checkMainAxis.isChecked():
            self.plotMainAxes()
        else:
            if self.checkCompleteSignalMain.isChecked():
                self.plotCompleteTimeAnalysis()
            elif self.checkSteadySignalMain.isChecked():
                self.plotSteadyTimeAnalysis()
            elif self.checkVibrationsMain.isChecked():
                self.plotVibrationsTimeAnalysis()
            elif  self.checkMovingRMS.isChecked():
                self.plotMovingRMSTimeAnalysis()
            else:
                self.plotCompleteTimeAnalysis()

    def exportConvexHull(self):
        '''
        This method export into a CSV plotted convex hull
        '''

        # Counting number of filled rows in Parameters Selected (listParamTimeAnalysis). To do this task,
        # both rows will have to be filled.

        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # If 2 rows filled in Parameters Selected (listParamTimeAnalysis):
        if numberRowsFull == 2:
            pathDirectoryConvexHull = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Save CSV with convex hull data', os.getenv('HOME'))
            if pathDirectoryConvexHull != '':
                logger.info('Exporting Convex Hull and Main axes of sensors:')
                # Saving properties first sensor
                sensorName1 = self.listParamTimeAnalysis.item(0, 0).text()
                fileNumber1 = self.listParamTimeAnalysis.item(0, 1).text()
                fileName1 = self.fileSelectedDict[fileNumber1]
                logger.info('X Axis: {}'.format(sensorName1))

                # Saving properties second sensor
                sensorName2 = self.listParamTimeAnalysis.item(1, 0).text()
                fileNumber2 = self.listParamTimeAnalysis.item(1, 1).text()
                fileName2 = self.fileSelectedDict[fileNumber2]
                logger.info('Y Axis: {}'.format(sensorName2))

                # Path where this CSV is going to be saved
                nameFile = 'ConvexHull_{}_{}'.format(sensorName1,sensorName2)
                pathToSave = '{}\{}.csv'.format(pathDirectoryConvexHull, nameFile)
                logger.info('It will be saved in directory: {}'.format(pathDirectoryConvexHull))
                logger.info('With name: {}.csv'.format(nameFile))

                # Writting CSV
                with open(pathToSave, 'w',newline='' ) as csvFile:
                    writer = csv.writer(csvFile, delimiter=',')

                    writer.writerow(['###########################'])
                    writer.writerow(['## CONVEX HULL'])
                    writer.writerow(['## First sensor [x]: {}'.format(sensorName1)])
                    writer.writerow(['## CDF name of first sensor: {}'.format(fileName1)])
                    writer.writerow(['## Second sensor [y]: {}'.format(sensorName2)])
                    writer.writerow(['## CDF name of second sensor: {}'.format(fileName2)])
                    writer.writerow(['###########################'])
                    writer.writerow([''])

                    writer.writerow(['## VERTICES'])
                    x = ['X']
                    y = ['Y']
                    for pairVert in self.hull:
                        x.append(pairVert[0])
                        y.append(pairVert[1])

                    rows = zip(x, y)
                    for row in rows:
                        writer.writerow(row)

                    writer.writerow([''])
                    writer.writerow(['## POINTS'])

                    xPoint = ['X']
                    yPoint = ['Y']
                    for pairPoints in self.points:
                        xPoint.append(pairPoints[0])
                        yPoint.append(pairPoints[1])

                    rows = zip(xPoint, yPoint)
                    for row in rows:
                        writer.writerow(row)
                logger.info('****************************************')
        else:
            logger.info('There must be 2 sensors selected in Parameters Selected table. Export of Convex Hull was'
                  'not possible.')
            logger.info('****************************************')

    def plotMovingRMSTimeAnalysis(self):
        '''
        Plotting Moving RMS in Time Analysis Window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Counting number of items in Parameters Selected (listParamTimeAnalysis), without taking into account empty rows.
        numberRowsFull = 0

        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # Loop through all items selected in listParamTimeAnalysis QTableWidget
        lines = []
        for i in range(numberRowsFull):
            # Saving name, full name, file name...
            sensorName = self.listParamTimeAnalysis.item(i, 0).text()
            fullName = self.listParamTimeAnalysis.item(i, 3).text()
            numberFile = self.listParamTimeAnalysis.item(i, 1).text()
            units = self.listParamTimeAnalysis.item(i, 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Selecting step and overlap from QPlainText
            step = float(self.stepMovingAvarage.toPlainText())
            overlap = float(self.overlapMovingAvarge.toPlainText())

            # Time of selected sensor
            t = copy.deepcopy(self.testFlight.sensor.get(fileName)[sensorName].time)
            # Calculating moving RMS
            movingRMS = self.testFlight.sensor[fileName][sensorName].movingRMS(overlap, step)

            # Checking if user want to write full name in plots
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Every sensor is plotted in different axes.
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                yLabel = 'Moving RMS'
            else:
                if i == 0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                yLabel = 'Moving RMS of {} {} - [{}]'.format(nameToPlot,numberFile, units)

            # Plotting moving RMS...
            p, = axesToPlot.plot(t, movingRMS, color='C{}'.format(i), label='{} {} [{}]'.format(nameToPlot, numberFile, units))
            lines.append(p)
            axesToPlot.set_xlabel('Time [s]')
            axesToPlot.set_ylabel(yLabel)

        title = 'Moving RMS. Step = {} [s]. Overlap = {} [%].'.format(step, overlap)
        axesToPlot.set_title(title)
        axesToPlot.legend(lines, [l.get_label() for l in lines])
        figure.suptitle('Moving RMS', fontsize=13)
        self.MplWidgetTime.removePlot()
        self.MplWidgetTime.addPlot(figure)


    def plotSteadyTimeAnalysis(self):
        '''
            Plotting Steady Signal in Time Analysis Window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Counting number of items in Parameters Selected (listParamTimeAnalysis), without taking into account empty rows.
        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # Loop through all sensors...
        lines = []
        for i in range(numberRowsFull):
            # Reading characteristics of every sensor
            sensorName = self.listParamTimeAnalysis.item(i, 0).text()
            fullName = self.listParamTimeAnalysis.item(i, 3).text()
            numberFile = self.listParamTimeAnalysis.item(i, 1).text()
            units = self.listParamTimeAnalysis.item(i, 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Saving time, step, overlap and steady signal
            t = self.testFlight.sensor.get(fileName)[sensorName].time
            step = float(self.stepMovingAvarage.toPlainText())
            overlap = float(self.overlapMovingAvarge.toPlainText())
            steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

            # Checking names that are going to be used in title, legend...
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Taking into account what axes is going to be used and the position of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                yLabel = 'Steady Signal'
            else:
                if i == 0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                yLabel = 'Steady signal of {} {} - [{}]'.format(nameToPlot, numberFile, units)

            # Plotting
            p, = axesToPlot.plot(t, steadyData, color='C{}'.format(i), label='{} {} [{}]'.format(nameToPlot, numberFile, units))
            lines.append(p)
            axesToPlot.set_xlabel('Time [s]')
            axesToPlot.set_ylabel(yLabel)

        title = 'Steady signal - Time [s]. Step = {}s. Overlap = {}%'.format(step, overlap)
        axesToPlot.set_title(title)
        figure.suptitle('Steady signal', fontsize=13)
        axesToPlot.legend(lines, [l.get_label() for l in lines])
        self.MplWidgetTime.removePlot()
        self.MplWidgetTime.addPlot(figure)


    def plotVibrationsTimeAnalysis(self):
        '''
            Plotting Vibration in Time Analysis Window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Counting number of items in Parameters Selected (listParamTimeAnalysis), without taking into account empty rows.
        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # Loop through all sensors...
        lines = []
        for i in range(numberRowsFull):
            # Reading characteristics of every sensor
            sensorName = self.listParamTimeAnalysis.item(i, 0).text()
            fullName = self.listParamTimeAnalysis.item(i, 3).text()
            numberFile = self.listParamTimeAnalysis.item(i, 1).text()
            units = self.listParamTimeAnalysis.item(i, 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Saving time, step, overlap and vibrations
            step = float(self.stepMovingAvarage.toPlainText())
            overlap = float(self.overlapMovingAvarge.toPlainText())
            t = self.testFlight.sensor.get(fileName)[sensorName].time
            vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)

            # Checking what names are going to be used in the title and the legend
            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Checking what axes are going to be used and the place of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                yLabel = 'Vibration'
            else:
                if i == 0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                yLabel = 'Vibration of {} {} - [{}]'.format(nameToPlot, numberFile, units)

            # Plotting
            p, = axesToPlot.plot(t, vibrations, 'C{}'.format(i), label='{} {} [{}]'.format(nameToPlot, numberFile, units))
            lines.append(p)

            axesToPlot.set_xlabel('Time [s]')
            axesToPlot.set_ylabel(yLabel)

        title = 'Vibration signal - Time [s]'
        axesToPlot.set_title(title)
        axesToPlot.legend(lines, [l.get_label() for l in lines])
        figure.suptitle('Vibrations', fontsize=13)
        self.MplWidgetTime.removePlot()
        self.MplWidgetTime.addPlot(figure)

    def plotCompleteTimeAnalysis(self):
        '''
            Plotting Complete Signal in Time Analysis Window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)


        # Counting number of items in Parameters Selected (listParamTimeAnalysis), without taking into account empty rows.
        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # Loop through all sensors...
        lines = []
        for i in range(numberRowsFull):
            # Reading characteristics of every sensor
            sensorName = self.listParamTimeAnalysis.item(i, 0).text()
            fullName = self.listParamTimeAnalysis.item(i, 3).text()
            numberFile = self.listParamTimeAnalysis.item(i, 1).text()
            units = self.listParamTimeAnalysis.item(i, 2).text()
            fileName = self.fileSelectedDict[numberFile]

            # Saving time, data, step, overlap and steadyData
            t = self.testFlight.sensor.get(fileName)[sensorName].time
            y = self.testFlight.sensor.get(fileName)[sensorName].data
            step = float(self.stepMovingAvarage.toPlainText())
            overlap = float(self.overlapMovingAvarge.toPlainText())
            # Calculating steady data
            steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName
            else:
                if fullName == '':
                    nameToPlot = sensorName
                else:
                    nameToPlot = fullName

            # Selecting axes to plot, colors of every sensor and the place of the legend
            if self.checkAxesYesMain.isChecked():
                axesToPlot = ax1
                yLabel = 'Complete signal'
            else:
                if i == 0:
                    axesToPlot = ax1
                else:
                    ax2 = ax1.twinx()
                    axesToPlot = ax2
                yLabel = 'Complete signal of {} {} - [{}]'.format(nameToPlot, numberFile, units)
            # Checking what name is going to be used in the title and the legend

            p1, = axesToPlot.plot(t, y, color='C{}'.format(i*2), label='{} {} [{}]'.format(nameToPlot, numberFile, units))
            p2, = axesToPlot.plot(t, steadyData, color='C{}'.format(i*2+1), label='{} {} [{}]'.format(nameToPlot, numberFile, units))
            lines.append(p1)
            lines.append(p2)

            axesToPlot.set_xlabel('Time [s]')
            axesToPlot.set_ylabel(yLabel)

        if numberRowsFull >=1:
            title = 'Complete signal - Time [s]'
            axesToPlot.set_title(title)
            axesToPlot.legend(lines, [l.get_label() for l in lines])
            figure.suptitle('Complete signal', fontsize=13)
        self.MplWidgetTime.removePlot()
        self.MplWidgetTime.addPlot(figure)


    def plotMainAxes(self):
        '''
            Plotting Main Axes in Time Analysis Window
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)
        ax2 = ax1.twinx()

        # Counting number of filled rows in Parameters Selected (listParamTimeAnalysis). To do this task,
        # both rows will have to be filled.
        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # If 2 rows filled in Parameters Selected (listParamTimeAnalysis):
        if numberRowsFull == 2:
            # Saving properties first sensor
            sensorName1 = self.listParamTimeAnalysis.item(0, 0).text()
            fullName1 = self.listParamTimeAnalysis.item(0, 3).text()
            numberFile1 = self.listParamTimeAnalysis.item(0, 1).text()
            units1 = self.listParamTimeAnalysis.item(0, 2).text()
            fileName1 = self.fileSelectedDict[numberFile1]

            # Saving properties second sensor
            sensorName2 = self.listParamTimeAnalysis.item(1, 0).text()
            fullName2 = self.listParamTimeAnalysis.item(1, 3).text()
            numberFile2 = self.listParamTimeAnalysis.item(1, 1).text()
            units2 = self.listParamTimeAnalysis.item(1, 2).text()
            fileName2 = self.fileSelectedDict[numberFile2]

            # Calculating convex hull
            hull, points, major_axis_length,minor_axis_length,small_lonwise,big_lonwise,small_latwise,big_latwise = \
                self.testFlight.convex_hull(fileName1, sensorName1,fileName2,sensorName2)
            self.points = points

            # Plotting all points
            ax1.scatter(points[:, 0], points[:, 1], s=5)

            # Plotting vertices
            for simplex in hull.simplices:
                ax1.plot(points[simplex, 0], points[simplex, 1], 'forestgreen')

            self.hull = []
            for i in hull.vertices:
                self.hull.append([self.points[i,0],self.points[i,1]])


            # Calculating main axis of convex hull

            xSave = []
            ySave = []
            pca = PCA(n_components=2)
            pca.fit(points)
            arrowprops = dict(arrowstyle='->', linewidth=2, shrinkA=0, shrinkB=0)
            for length, vector in zip(pca.explained_variance_, pca.components_):
                v = vector * 3 * np.sqrt(length)
                xSave.append(pca.mean_[0])
                ySave.append(pca.mean_[1])
                xSave.append((pca.mean_ + v)[0])
                ySave.append((pca.mean_ + v)[1])
                ax1.annotate('', pca.mean_ + v, pca.mean_, arrowprops=arrowprops)

            centerEllipse = [xSave[0],ySave[0]]
            axis1 = [xSave[1],ySave[1]]
            axis2 =[xSave[3],ySave[3]]
            axis1Module = np.sqrt((centerEllipse[0]-xSave[1])**2+(centerEllipse[1]-ySave[1])**2)
            axis2Module = np.sqrt((centerEllipse[0]-xSave[3])**2+(centerEllipse[1]-ySave[3])**2)

            if axis1Module >= axis2Module:
                semiMajorAxis = axis1
                semiMinorAxis = axis2
                semiMajorAxisModule = axis1Module
                semiMinorAxisModule = axis2Module
            else:
                semiMajorAxis = axis2
                semiMinorAxis = axis1
                semiMajorAxisModule = axis2Module
                semiMinorAxisModule = axis1Module

            angleEllipseRad = np.math.acos((semiMajorAxis[0]-centerEllipse[0])/semiMajorAxisModule)
            angleEllipseG = angleEllipseRad * 180 / np.math.pi
            if (semiMajorAxis[1]-centerEllipse[1])<0:
                angleEllipseG = 360 - angleEllipseG


            semiX = np.amax(np.absolute((np.absolute(points[:,0])- np.absolute(centerEllipse[0]))))
            semiY = np.amax(np.absolute(np.absolute(points[:,1]) - np.absolute(centerEllipse[1])))
            if np.absolute(axis1[0]-centerEllipse[0])> np.absolute(axis2[0]-centerEllipse[0]):
                MainAxisX = np.absolute(axis1[0]-centerEllipse[0])
            else:
                MainAxisX = np.absolute(axis2[0]-centerEllipse[0])

            if np.absolute(axis1[1]-centerEllipse[1])> np.absolute(axis2[1]-centerEllipse[1]):
                MainAxisY = np.absolute(axis1[1]-centerEllipse[1])
            else:
                MainAxisY = np.absolute(axis2[1]-centerEllipse[1])

            minX = min((centerEllipse[0]- semiX), min(points[:,0]), centerEllipse[0]-MainAxisX)
            maxX = max((centerEllipse[0] + semiX), max(points[:,0]),centerEllipse[0]+MainAxisX)
            minY = min((centerEllipse[1] - semiY), min(points[:,1]),centerEllipse[1]-MainAxisY)
            maxY = max((centerEllipse[1] + semiY),max(points[:,1]),centerEllipse[1]+MainAxisY)

            if semiY/centerEllipse[1]<0.05:
                minY = minY - 0.2*semiY
                maxY = maxY + 0.2*semiY
            else:
                minY = minY - 0.02 * np.absolute(minY)
                maxY = maxY + 0.02 * np.absolute(maxY)

            if semiX/centerEllipse[0]<0.01:
                minX = minX - 0.01 * semiX
                maxX = maxX + 0.01* semiX
            else:
                minX = minX - 0.01 * np.absolute(minX)
                maxX = maxX + 0.01 * np.absolute(maxX)

            ellipse = Ellipse(centerEllipse,2*semiMajorAxisModule,2*semiMinorAxisModule,angleEllipseG, edgecolor = 'k', fill = False,lw = 3)

            # Plotting elipse created with main axes
            ax1.add_artist(ellipse)

            # Checking what name is going to be plotted in title and axes
            if self.checkKeyAxisName.isChecked():
                nameToPlot1 = sensorName1
                nameToPlot2 = sensorName2
            else:
                if fullName1 == '':
                    nameToPlot1 = sensorName1
                else:
                    nameToPlot1 = fullName1

                if fullName2 == '':
                    nameToPlot2 = sensorName2
                else:
                    nameToPlot2 = fullName2

            xlabel = ('{} - [{}]').format(nameToPlot1,units1)
            ylabel =('{} - [{}]').format(nameToPlot2,units2)
            title = ('Main axes between ({}) and ({})').format(nameToPlot1,nameToPlot2)

            # Legend and properties
            legend = 'Semi Major Axis = {} \n Semi Minor Axis = {}'.format('{0:.3f}'.format(semiMajorAxisModule), '{0:.3f}'.format(semiMinorAxisModule))
            ax2.text(0.95, 0.01,legend,verticalalignment='bottom',horizontalalignment='right',transform=ax2.transAxes,
                                        color='k', fontsize=11)
            ax1.set_title(title)
            ax1.set_xlabel(xlabel)
            ax1.set_ylabel(ylabel)

            ax1.set_xlim([minX,maxX])
            ax1.set_ylim([minY, maxY])

            self.MplWidgetTime.removePlot()
            self.MplWidgetTime.addPlot(figure)
        else:
            pass


    def plotRMS1(self):
        '''
            Plotting RMS of first sensor
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Saving properties of first sensor
        sensorName = self.listParamTimeAnalysis.item(0, 0).text()
        fileNumber = self.listParamTimeAnalysis.item(0, 1).text()
        units = self.listParamTimeAnalysis.item(0, 2).text()
        fullName = self.listParamTimeAnalysis.item(0, 3).text()
        fileName = self.fileSelectedDict[fileNumber]

        # Saving time, step, overlap and vibrations
        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Calculating time, data and creating a var with RMS value
        t = self.testFlight.sensor.get(fileName)[sensorName].time
        vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)
        y2 =np.ones(t.shape[0])*float(self.tableRMS.item(0,1).text())

        # Checking what name is going to be used in the title and the legend
        if self.checkKeyAxisName.isChecked():
            nameToPlot = sensorName
        else:
            if fullName == '':
                nameToPlot = sensorName
            else:
                nameToPlot = fullName

        # Plotting
        line1 = ax1.plot(t, vibrations, '-b', label= nameToPlot)
        line2 = ax1.plot(t, y2, '-r',label= 'RMS')
        title = 'Vibration of {} [{}] and RMS value - Time [s]'.format(nameToPlot,units)
        ax1.set_title(title)
        ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('{} [{}]'.format(nameToPlot, units))
        # Plotting legend
        lns = line1 + line2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc=0)
        self.MplWidgetTime.removePlot()
        self.MplWidgetTime.addPlot(figure)

    def plotRMS2(self):
        '''
            Plotting RMS of first sensor
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        sensorName = self.listParamTimeAnalysis.item(1, 0).text()
        fileNumber = self.listParamTimeAnalysis.item(1, 1).text()
        units = self.listParamTimeAnalysis.item(1, 2).text()
        fullName = self.listParamTimeAnalysis.item(1, 3).text()
        fileName = self.fileSelectedDict[fileNumber]

        # Saving time, step, overlap and vibrations
        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        # Calculating time, data and creating a var with RMS value
        t = self.testFlight.sensor.get(fileName)[sensorName].time
        vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)
        y2 = np.ones(t.shape[0]) * float(self.tableRMS.item(1, 1).text())

        # Checking what name is going to be used in the title and the legend
        if self.checkKeyAxisName.isChecked():
            nameToPlot = sensorName
        else:
            if fullName == '':
                nameToPlot = sensorName
            else:
                nameToPlot = fullName

        # Plotting
        line1 = ax1.plot(t, vibrations, '-b', label=nameToPlot)
        line2 = ax1.plot(t, y2, '-r', label='RMS')
        title = 'Vibration of {} [{}] and RMS value - Time [s]'.format(nameToPlot,units)
        ax1.set_title(title)
        ax1.set_xlabel('Time [s]')
        ax1.set_ylabel('{} [{}]'.format(nameToPlot, units))
        # Plotting legend
        lns = line1 + line2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, loc=0)

        self.MplWidgetTime.removePlot()
        self.MplWidgetTime.addPlot(figure)

    def plotConvexHull(self):
        '''
            Plotting RMS of first sensor
        '''

        figure = Figure(constrained_layout=True)
        ax1 = figure.add_subplot(111)

        # Counting number of filled rows in Parameters Selected (listParamTimeAnalysis). To do this task,
        # both rows will have to be filled.
        numberRowsFull = 0
        for i in range(self.listParamTimeAnalysis.rowCount()):
            if self.listParamTimeAnalysis.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # If 2 rows filled in Parameters Selected (listParamTimeAnalysis):
        if numberRowsFull == 2:

            # Saving properties first sensor
            sensorName1 = self.listParamTimeAnalysis.item(0, 0).text()
            fullName1 = self.listParamTimeAnalysis.item(0, 3).text()
            numberFile1 = self.listParamTimeAnalysis.item(0, 1).text()
            units1 = self.listParamTimeAnalysis.item(0, 2).text()
            fileName1 = self.fileSelectedDict[numberFile1]

            # Saving properties second sensor
            sensorName2 = self.listParamTimeAnalysis.item(1, 0).text()
            fullName2 = self.listParamTimeAnalysis.item(1, 3).text()
            numberFile2 = self.listParamTimeAnalysis.item(1, 1).text()
            units2 = self.listParamTimeAnalysis.item(1, 2).text()
            fileName2 = self.fileSelectedDict[numberFile2]

            # Calculating convex hull
            hull, points, major_axis_length,minor_axis_length,small_lonwise,big_lonwise,small_latwise,big_latwise = \
                self.testFlight.convex_hull(fileName1, sensorName1,fileName2,sensorName2)
            self.points = points

            # Plotting points
            ax1.scatter(points[:,0],points[:,1], s=5)

            # Plotting vertices
            for simplex in hull.simplices:
                ax1.plot(points[simplex, 0], points[simplex, 1], 'forestgreen')

            self.hull = []
            for i in hull.vertices:
                self.hull.append([self.points[i,0],self.points[i,1]])

            # Calculating biggest and smallest distances between vertives
            if euclidean(big_latwise, small_latwise)>= euclidean(big_lonwise, small_lonwise):
                x2 = np.array((small_lonwise[0],big_lonwise[0]))
                y2 = np.array((small_lonwise[1],big_lonwise[1]))
                x1 = np.array((small_latwise[0],big_latwise[0]))
                y1 = np.array((small_latwise[1], big_latwise[1]))
            else:
                x1 = np.array((small_lonwise[0],big_lonwise[0]))
                y1 = np.array((small_lonwise[1],big_lonwise[1]))
                x2 = np.array((small_latwise[0],big_latwise[0]))
                y2 = np.array((small_latwise[1], big_latwise[1]))

            # Plotting lines
            line1 = ax1.plot(x1,y1,'-k', label = 'Biggest diff vert = {}'.format("{0:.2f}".format(major_axis_length)), zorder = 8)
            line2 = ax1.plot(x2,y2, '-r',label = 'Shortest diff vert = {}'.format("{0:.2f}".format(minor_axis_length)),zorder = 9)

            # Calculating x and y axes limits
            minX = min(points[:, 0]) - np.absolute(0.01 * min(points[:, 0]))
            maxX = max(points[:, 0]) + np.absolute(0.01 * max(points[:, 0]))
            minY = min(points[:, 1]) - np.absolute(0.01 * min(points[:, 1]))
            maxY = max(points[:, 1]) + np.absolute(0.01 * max(points[:, 1]))

            # Plotting legend
            lns = line1 + line2
            labs = [l.get_label() for l in lns]
            ax1.legend(lns, labs, loc=0)

            if self.checkKeyAxisName.isChecked():
                nameToPlot1 = sensorName1
                nameToPlot2 = sensorName2
            else:
                if fullName1 == '':
                    nameToPlot1 = sensorName1
                else:
                    nameToPlot1 = fullName1

                if fullName2 == '':
                    nameToPlot2 = sensorName2
                else:
                    nameToPlot2 = fullName2

            xlabel = ('{} - [{}]').format(nameToPlot1,units1)
            ylabel =('{} - [{}]').format(nameToPlot2,units2)
            title = ('Convex Hull between ({}) and ({})').format(nameToPlot1,nameToPlot2)

            ax1.set_title(title)
            ax1.set_xlabel(xlabel)
            ax1.set_ylabel(ylabel)

            ax1.set_xlim([minX,maxX])
            ax1.set_ylim([minY, maxY])

            self.MplWidgetTime.removePlot()
            self.MplWidgetTime.addPlot(figure)
        else:
            pass

    '''
    ################################################################################################################
    ################################################################################################################

                                                    FREQUENCY WINDOW FUNCTIONS

    ################################################################################################################
    ################################################################################################################

    '''
    def freqAnalysis(self):
        '''
        Method that will fill all the tab Freq Analysis when it is clicked.
        '''
        # Clearing CDF file selected (listCDFFreq)

        self.listCDFFreq.clear()

        # Copying all selected files of Main Window to CDF file selected (listCDFFreq)
        for fileName in self.fileSelect.selectedItems():
            self.listCDFFreq.addItem(fileName.text())

        # Clearing contents Parameters Selected (paramListFreq)
        self.paramListFreq.clearContents()

        # Deleting contents of Second Parameter Selection (secondParamListFreq)
        self.secondParamListFreq.clearContents()

        # Setting number of rows in Second Parameter Selection (secondParamListFreq) of Freq Analysis Tab
        numberTotalRows = self.paramSel.rowCount()
        self.secondParamListFreq.setRowCount(numberTotalRows)

        self.boxAxisSpec.clear()
        self.boxAxisSpec.addItem('Time')

        # Inserting all sensors of selected files to Second Parameter Selection (secondParamListFreq)
        for row in range(numberTotalRows):
            key = self.paramSel.item(row, 0).text()
            ref = self.paramSel.item(row, 1).text()
            units = self.paramSel.item(row, 2).text()
            fullName = self.paramSel.item(row, 3).text()

            if key != 'GMT':
                self.boxAxisSpec.addItem(key)
            else:
                pass

            # Inserting all elements
            self.secondParamListFreq.setItem(row, 0, PyQt5.QtWidgets.QTableWidgetItem(key))
            self.secondParamListFreq.setItem(row, 1, PyQt5.QtWidgets.QTableWidgetItem(ref))
            self.secondParamListFreq.setItem(row, 2, PyQt5.QtWidgets.QTableWidgetItem(units))
            self.secondParamListFreq.setItem(row, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName))
            # Resizing columns
            self.secondParamListFreq.resizeColumnToContents(0)
            self.secondParamListFreq.resizeColumnToContents(1)
            self.secondParamListFreq.resizeColumnToContents(2)
            self.secondParamListFreq.resizeColumnToContents(3)

        # Inserting selected items in Main Window to Parameters Selected (paramListFreq)
        for row in range(len(self.paramSel.selectedItems())):
            index = self.paramSel.selectedIndexes()[row]
            fileNumber = self.paramSel.item(index.row(),1).text()
            sensorName = self.paramSel.item(index.row(), 0).text()
            fullName = self.paramSel.item(index.row(), 3).text()
            units = self.paramSel.item(index.row(), 2).text()
            self.paramListFreq.setItem(row, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName))
            self.paramListFreq.setItem(row, 1, PyQt5.QtWidgets.QTableWidgetItem(fileNumber))
            self.paramListFreq.setItem(row, 2, PyQt5.QtWidgets.QTableWidgetItem(units))
            self.paramListFreq.setItem(row, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName))

        # Resizing columns
        self.paramListFreq.resizeColumnToContents(0)
        self.paramListFreq.resizeColumnToContents(1)
        self.paramListFreq.resizeColumnToContents(2)
        self.paramListFreq.resizeColumnToContents(3)

        # Plotting PSD
        self.plotPSD()

    def exportPSD(self):
        '''
        Method that export data of PSD in format CSV.
        '''

        # Counting number of filled rows in Parameters Selected (paramListFreq).
        numberRowsFull = 0
        for i in range(self.paramListFreq.rowCount()):
            if self.paramListFreq.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        stepWindow = int(self.windowSample.toPlainText())
        overlapWindow = int(self.overlapSample.toPlainText())
        if self.boxDetrend.currentText() == 'Yes':
            detrendBool = True
        else:
            detrendBool = False
        windowType = self.boxWindowFun.currentText().lower()
        order = self.orderFFT.toPlainText()
        highPassFreq = self.highFreqFFT.toPlainText()
        lowPassFreq = self.lowFreqFFT.toPlainText()

        # Saving directory path
        pathDirectoryPSD = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Save CSV with PSD data', os.getenv('HOME'))
        if pathDirectoryPSD != '':
            # Loop through all sensors (it is going to be created one CSV for each sensor)
            logger.info('Exporting PSD...')
            for row in range(numberRowsFull):
                # Saving attributes of sensor
                sensorName = self.paramListFreq.item(row, 0).text()
                fileNumber = self.paramListFreq.item(row, 1).text()
                fileName = self.fileSelectedDict[fileNumber]
                nameFile = 'PSD_{}.csv'.format(sensorName)
                logger.info('Sensor {} of file {}.'.format(sensorName, fileName))

                # Saving time and splitting it. It could be splitted in ranges.
                t = self.testFlight.sensor[fileName].get(sensorName).time
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                freqSplitted, PSDSplitted = self.testFlight.sensor[fileName].get(sensorName).PSD(stepWin = stepWindow,
                                                                                               overlapWin = overlapWindow,
                                                                                               win = windowType,
                                                                                               detrendBool = detrendBool,
                                                                                               order = order,
                                                                                               highPassFreq=highPassFreq,
                                                                                               lowPassFreq=lowPassFreq)

                # Path of the CSV
                pathToSavePSD = '{}\{}'.format(pathDirectoryPSD, nameFile)
                logger.info('CSV saved in directory {}'.format(pathDirectoryPSD))
                logger.info('With name {}'.format(nameFile))

                # Writting CSV
                with open(pathToSavePSD, 'w',newline='' ) as csvFile:
                    writer = csv.writer(csvFile, delimiter=',')
                    writer.writerow(['#########################'])
                    writer.writerow(['## PSD'])
                    writer.writerow(['## Sensor: {}'.format(sensorName)])
                    writer.writerow(['## File: {}'.format(fileName)])
                    for i in range(len(timeSplitted)):
                        writer.writerow(['## Range {}: {:.2f}-{:.2f} [s]'.format(i+1, timeSplitted[i][0],timeSplitted[i][-1])])
                    writer.writerow(['#########################'])
                    writer.writerow([''])

                    listToZip = []
                    for i in range(len(PSDSplitted)):
                        frequency = ['Frequency']
                        data = ['Range {}'.format(i+1)]
                        frequency.extend(freqSplitted[i])
                        data.extend(PSDSplitted[i])
                        listToZip.append(frequency)
                        listToZip.append(data)

                    rows = zip(*listToZip)
                    for row in rows:
                        writer.writerow(row)
            logger.info('****************************************')

    def exportFFT(self):
        '''
        Method that exports FFT plot to CSV
        '''

        if self.boxDetrend.currentText() == 'Yes':
            detrendBool = True
        else:
            detrendBool = False
        windowType = self.boxWindowFun.currentText().lower()
        highPassFreq = self.highFreqFFT.toPlainText()
        lowPassFreq = self.lowFreqFFT.toPlainText()
        order = self.orderFFT.toPlainText()

        # Counting number of filled rows in Parameters Selected (paramListFreq).
        numberRowsFull = 0
        for i in range(self.paramListFreq.rowCount()):
            if self.paramListFreq.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        # Path of the directory in which is going to be saved the CSV
        pathDirectoryFFT = PyQt5.QtWidgets.QFileDialog.getExistingDirectory(self, 'Save CSV with FFT data', os.getenv('HOME'))
        if pathDirectoryFFT != '':
            logger.info('Exporting FFT...')
            # Loop through all rows in Parameters Selected
            for row in range(numberRowsFull):
                sensorName = self.paramListFreq.item(row, 0).text()
                fileNumber = self.paramListFreq.item(row, 1).text()
                fileName = self.fileSelectedDict[fileNumber]
                nameFile = 'FFT_{}.csv'.format(sensorName)
                pathToSave = '{}\{}'.format(pathDirectoryFFT, nameFile)

                logger.info('Sensor {} of file {}'.format(sensorName, fileName))
                logger.info('CSV saved in directory {}'.format(pathDirectoryFFT))
                logger.info('With name {}'.format(nameFile))
                t = self.testFlight.sensor[fileName].get(sensorName).time
                originalData = self.testFlight.sensor[fileName].get(sensorName).data
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                originalDataSplitted = [originalData[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                freqSplitted, dataSplitted = self.testFlight.sensor[fileName].get(sensorName).tofreq(win= windowType,
                                                                                                   detrendBool = detrendBool,
                                                                                                   highPassFreq= highPassFreq,
                                                                                                   lowPassFreq=lowPassFreq,
                                                                                                   order=order)

                # Loop through all ranges
                listToZip = []
                for i in range(len(freqSplitted)):

                    timeRange = ['Time']
                    time = timeSplitted[i]
                    timeRange.extend(time)
                    listToZip.append(timeRange)

                    dataRange = ['Original data']
                    data = originalDataSplitted[i]
                    dataRange.extend(data)
                    listToZip.append(dataRange)

                    freq = freqSplitted[i]
                    data = dataSplitted[i]

                    # First Plot
                    firstPlotFreq = ['Frequency']
                    firstPlotData = ['Data']
                    freq = freq[0: int(freq.shape[0] / 2) - 1]
                    data = data[0:int(data.shape[0] / 2) - 1]
                    firstPlotFreq.extend(freq)
                    listToZip.append(firstPlotFreq)
                    firstPlotData.extend(data)
                    listToZip.append(firstPlotData)

                    # Second Plot
                    secondPlotData = ['Phase of data [Deg]']
                    phaseArray = np.angle(data)
                    phaseArray = phaseArray * 180 / np.pi
                    phaseArray = np.unwrap(phaseArray)
                    secondPlotData.extend(phaseArray)
                    listToZip.append(secondPlotData)

                    # Third Plot
                    thirdPlotData = ['Real part of data']
                    dataReal = data.real
                    thirdPlotData.extend(dataReal)
                    listToZip.append(thirdPlotData)

                    # Fourth Plot
                    fourthPlotData = ['Imaginary part of data']
                    dataImag = data.imag
                    fourthPlotData.extend(dataImag)
                    listToZip.append(dataImag)

                    # Fifth Plot
                    fifthPlotData = ['Amplitude of data']
                    dataAmplit = abs(data)
                    fifthPlotData.extend(dataAmplit)
                    listToZip.append(fifthPlotData)

                rows = zip_longest(*listToZip)

                with open(pathToSave, 'w', newline='') as csvFile:
                    writer = csv.writer(csvFile, delimiter=',')
                    writer.writerow(['#########################'])
                    writer.writerow(['## FFT'])
                    writer.writerow(['## Sensor: {}'.format(sensorName)])
                    writer.writerow(['## File: {}'.format(fileName)])
                    for i in range(len(timeSplitted)):
                        writer.writerow(['## Range {}: {:.2f}-{:.2f} [s]'.format(i+1, timeSplitted[i][0],timeSplitted[i][-1])])
                    writer.writerow(['#########################'])
                    writer.writerow([''])

                    rangeRowList = []
                    for i in range(len(timeSplitted)):
                        rangeRowList.append('Range {}'.format(i))
                        for i in range(7):
                            rangeRowList.append('')

                    writer.writerow(rangeRowList)

                    for row in rows:
                        writer.writerow(row)

    def clearAllFreq(self):
        '''
        Method that clear previous plots in Freq Analysis Tab and return original tab
        '''
        logger.info('Resetting Freq Analaysis tab')
        self.MplWidgetFreq.removePlot()
        self.freqAnalysis()
        self.windowSample.setPlainText('1024')
        self.overlapSample.setPlainText('100')
        self.lowFreqFFT.setPlainText('High pass')
        self.highFreqFFT.setPlainText('Low pass')
        self.orderFFT.setPlainText('n')
        logger.info('****************************************')

    def plotSpectrogramFreqWindow(self):
        # Plot the spectrogram
        figure = Figure()

        stepWindow = int(self.windowSample.toPlainText())
        overlapWindow = int(self.overlapSample.toPlainText())
        if self.boxDetrend.currentText() == 'Yes':
            detrendBool = True
        else:
            detrendBool = False
        windowType = self.boxWindowFun.currentText().lower()
        order = self.orderFFT.toPlainText()
        highPassFreq = self.highFreqFFT.toPlainText()
        lowPassFreq = self.lowFreqFFT.toPlainText()
        xAxisSensor = self.boxAxisSpec.currentText()


        # If user has selected sensor 1 to be plotted
        if self.FFT1.isChecked():
            # Saving attrinutesw of sensor
            sensorName1 = self.paramListFreq.item(0, 0).text()
            numberFile1 = self.paramListFreq.item(0, 1).text()
            units1 = self.paramListFreq.item(0, 2).text()
            fileName1 = self.fileSelectedDict[numberFile1]
            fullName1 = self.paramListFreq.item(0, 3).text()

        # If user has selected sensor 2 to be plotted
        else:
            # Saving attributes of sensor
            sensorName1 = self.paramListFreq.item(1, 0).text()
            numberFile1 = self.paramListFreq.item(1, 1).text()
            units1 = self.paramListFreq.item(1, 2).text()
            fileName1 = self.fileSelectedDict[numberFile1]
            fullName1 = self.paramListFreq.item(1, 3).text()

        figure.suptitle('Spectogram - PSD', fontsize=13)

        logger.info('Plotting spectogram with the following properties:')
        # Saving time and data
        data = self.testFlight.sensor[fileName1].get(sensorName1).data
        time = self.testFlight.sensor[fileName1].get(sensorName1).time
        if xAxisSensor == 'Time':
            logger.info('- x axis is: Time')
            sampleRate = self.testFlight.sensor[fileName1][sensorName1].sampleRate
        else:
            dataXAxis = self.testFlight.sensor[fileName1][xAxisSensor].data
            if np.all(np.diff(dataXAxis) > 0):
                sampleRate = 1./dataXAxis[1]-dataXAxis[0]
                logger.info('- x axis is {}'.format(xAxisSensor))
            else:
                sampleRate = self.testFlight.sensor[fileName1][sensorName1].sampleRate
                logger.info('- Sensor {} is not an increasing monotone array. Time will be used instead.'.format(xAxisSensor))


        if windowType == 'none':
            windowType = 'hanning'
            logger.info('- Window is imperative. Hanning window will be used.')
        else:
            logger.info('- Window funtion applied: {}'.format(windowType))
        logger.info('- Step size of data: {} hz'.format(sampleRate))
        logger.info('- Number of step elements: {}'.format(stepWindow))
        logger.info('- Number of overlap elements: {}'.format(overlapWindow))
        if detrendBool:
            detrendType = 'mean'
            logger.info('- Detrend applied')
        else:
            detrendType = 'none'
            logger.info('Detrend not applied')
        logger.info('- Mode: PSD')
        logger.info('- Scale: dB')

        highPassBool = False
        lowPassBool = False
        if order == 'n':
            logger.info('- No high pass filter applied')
            logger.info('- No low pass filter applied')
        else:
            order = int(order)
            if highPassFreq == 'High pass' or highPassFreq == '':
                logger.info('- No high pass filter applied')
            else:
                logger.info('- High pass filter applied. Cut of: {} hz'.format(highPassFreq))
                highPassFreq = float(highPassFreq)
                highPassBool = True
            if lowPassFreq == 'Low pass' or lowPassFreq == '':
                logger.info('- No low pass filter applied')
            else:
                logger.info('- Low pass filter applied. Cut of: {} hz'.format(lowPassFreq))
                lowPassFreq = float(lowPassFreq)
                lowPassBool = True

        freqSplitted, PSDSplitted = self.testFlight.sensor[fileName1].get(sensorName1).PSD(stepWin = stepWindow,
                                                                                           overlapWin = overlapWindow,
                                                                                           win=windowType,
                                                                                           detrendBool =detrendBool,
                                                                                           order = order,
                                                                                           highPassFreq=highPassFreq,
                                                                                           lowPassFreq=lowPassFreq)

        # Calculating all ranges of time and data
        timeSplitted = [time[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(time))]
        dataSplitted = [data[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(time))]

        # Checking what range is going to be plotted. Depending on the range one color is selected
        if self.range1FFT.isChecked():
            rangeIndex = 0
            colorPlot = '#1f77b4'
        elif self.range2FFT.isChecked():
            rangeIndex = 1
            colorPlot = '#ff7f0e'
        elif self.range3FFT.isChecked():
            rangeIndex = 2
            colorPlot = '#2ca02c'
        elif self.range4FFT.isChecked():
            rangeIndex = 3
            colorPlot = '#d62728'
        elif self.range5FFT.isChecked():
            rangeIndex = 4
            colorPlot = '#9467bd'
        elif self.range6FFT.isChecked():
            rangeIndex = 5
            colorPlot = '#8c564b'

        # Calculating all data of the range that is going to be plotted
        dataOfRange = dataSplitted[rangeIndex]

        if highPassBool:
            # The frequency is normalized (Nyquist)
            w = highPassFreq / (sampleRate / 2)
            b, a = signal.butter(N=order, Wn=w, btype='highpass')
            dataOfRange = signal.filtfilt(b, a, dataOfRange)

        if lowPassBool:
            # The frequency is normalized (Nyquist)
            w = lowPassFreq / (sampleRate / 2)
            b, a = signal.butter(N=order, Wn=w, btype='lowpass')
            dataOfRange = signal.filtfilt(b, a, dataOfRange)

        # Checking what name is going to be used for title and legend
        if self.checkKeyAxisName.isChecked():
            nameToPlot = sensorName1
        else:
            if fullName1 == '':
                nameToPlot = sensorName1
            else:
                nameToPlot = fullName1

        grid1 = figure.add_gridspec(ncols=2, nrows=1, width_ratios=[3, 1], wspace=0, bottom = 0.35)
        grid2 = figure.add_gridspec(ncols=1, nrows=1, top = 0.26)


        ax1 = figure.add_subplot(grid1[0, 0])
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Spectogram of {}'.format(nameToPlot))

        ax2 = figure.add_subplot(grid1[0, 1], sharey=ax1, label = 'Range {}'.format(rangeIndex))
        ax2.set_xticklabels([])
        ax2.xaxis.tick_top()
        ax2.spines['left'].set_visible(False)
        ax2.set_title('PSD')

        ax3 = figure.add_subplot(grid2[0, 0])
        ax3.set_xlabel('Time')
        ax3.set_ylabel(nameToPlot)
        ax3.set_title('Complete signal')


        ax1.specgram(dataOfRange, Fs = sampleRate, NFFT = stepWindow, detrend=detrendType,
                     mode='psd', noverlap=overlapWindow, scale = 'dB')

        ax2.plot(PSDSplitted[rangeIndex],freqSplitted[rangeIndex], color=colorPlot)
        for index in range(len(timeSplitted)):
            ax3.plot(timeSplitted[index], dataSplitted[index], label='Range {}'.format(index))

        self.MplWidgetFreq.removePlot()
        self.MplWidgetFreq.addPlot(figure)

    def plotFFT(self):
        '''
        Plotting FFT
        '''

        figure = Figure()
        figure.set_tight_layout({'rect': [0, 0, 1, 0.95]})

        if self.boxDetrend.currentText() == 'Yes':
            detrendBool = True
        else:
            detrendBool = False
        windowType = self.boxWindowFun.currentText().lower()
        highPassFreq = self.highFreqFFT.toPlainText()
        lowPassFreq = self.lowFreqFFT.toPlainText()
        order = self.orderFFT.toPlainText()

        # If user has selected sensor 1 to be plotted
        if self.FFT1.isChecked():
            # Saving attrinutesw of sensor
            sensorName1 = self.paramListFreq.item(0,0).text()
            numberFile1 = self.paramListFreq.item(0,1).text()
            units1 = self.paramListFreq.item(0,2).text()
            fileName1 = self.fileSelectedDict[numberFile1]
            fullName1 = self.paramListFreq.item(0,3).text()

        # If user has selected sensor 2 to be plotted
        else:
            # Saving attributes of sensor
            sensorName1 = self.paramListFreq.item(1, 0).text()
            numberFile1 = self.paramListFreq.item(1, 1).text()
            units1 = self.paramListFreq.item(1, 2).text()
            fileName1 = self.fileSelectedDict[numberFile1]
            fullName1 = self.paramListFreq.item(1, 3).text()

        figure.suptitle('FFT', fontsize=13)

        # Saving time and data
        data = self.testFlight.sensor[fileName1].get(sensorName1).data
        time = self.testFlight.sensor[fileName1].get(sensorName1).time

        # Calculating all ranges of time and data
        timeSplitted = [time[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(time))]
        dataSplitted = [data[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(time))]

        # Calculating all ranges of freq and data freq
        freqSplitted, dataFreqSplitted = self.testFlight.sensor[fileName1].get(sensorName1).tofreq(win= windowType,
                                                                                                   detrendBool = detrendBool,
                                                                                                   highPassFreq= highPassFreq,
                                                                                                   lowPassFreq=lowPassFreq,
                                                                                                   order=order)

        # Checking what range is going to be plotted. Depending on the range one color is selected
        if self.range1FFT.isChecked():
            rangeIndex = 0
            colorPlot = '#1f77b4'
        elif self.range2FFT.isChecked():
            rangeIndex = 1
            colorPlot = '#ff7f0e'
        elif self.range3FFT.isChecked():
            rangeIndex = 2
            colorPlot = '#2ca02c'
        elif self.range4FFT.isChecked():
            rangeIndex = 3
            colorPlot = '#d62728'
        elif self.range5FFT.isChecked():
            rangeIndex = 4
            colorPlot = '#9467bd'
        elif self.range6FFT.isChecked():
            rangeIndex = 5
            colorPlot = '#8c564b'

        # Calculating all data of the range that is going to be plotted
        data = dataSplitted[rangeIndex]
        time = timeSplitted[rangeIndex]
        freq = freqSplitted[rangeIndex]
        dataFreq = dataFreqSplitted[rangeIndex]

        # Checking what name is going to be used for title and legend
        if self.checkKeyAxisName.isChecked():
            nameToPlot = sensorName1
        else:
            if fullName1 == '':
                nameToPlot = sensorName1
            else:
                nameToPlot = fullName1


        '''
        ###################################
                    FIRST PLOT
        ###################################
        '''
        ax1 = figure.add_subplot(321)

        # Plotting complete signal with different colors for every range
        for i in range(len(timeSplitted)):
            ax1.plot(timeSplitted[i], dataSplitted[i], label = 'Range'+str(i+1))

        ax1.legend()
        ax1.set_xlim(left=0, right=timeSplitted[-1][-1])
        title = '{} {} - [{}] - Time [s]'.format(nameToPlot,numberFile1, units1)
        xlabel = 'Time [ s ]'
        ylabel = '{} [{}]'.format(nameToPlot, units1)

        ax1.set_title(title)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)

        '''
        ###################################
                    SECOND PLOT
        ###################################
        '''
        # Plotting phase of the sesnor
        freq = freq[0: int(freq.shape[0]/2)-1]
        dataFreq = dataFreq[0:int(dataFreq.shape[0]/2)-1]
        phaseArray = np.angle(dataFreq)
        phaseArray = phaseArray*180/np.pi
        phaseArray = np.unwrap(phaseArray)

        ax2 = figure.add_subplot(322)
        ax2.plot(freq, phaseArray, color = colorPlot)
        ax2.set_ylim(top=phaseArray.max() * 1.1)

        title = 'Phase of sensor: {}'.format(nameToPlot)
        xlabel = 'Frequency [ Hz ]'
        ylabel = 'Phase [Deg]'

        ax2.set_title(title)
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)

        '''
                    THIRD PLOT
        '''
        # Plotting real part
        ax3 = figure.add_subplot(323)
        ax3.plot(freq,dataFreq.real, color = colorPlot)
        ax3.set_ylim(top=dataFreq.real.max() * 1.1)

        title = 'Real part of sensor: {} {}'.format(nameToPlot, numberFile1)
        xlabel = 'Frequency [ Hz ]'
        ylabel = 'Real Part'

        ax3.set_title(title)
        ax3.set_xlabel(xlabel)
        ax3.set_ylabel(ylabel)
        ax3.ticklabel_format(axis='y', style='sci',scilimits=(-2,3))

        '''
                    FOURTH PLOT
        '''
        # Plotting imaginary part
        ax4 = figure.add_subplot(324)

        ax4.plot(freq, dataFreq.imag, color = colorPlot)
        ax4.set_ylim(top=dataFreq.imag.max() * 1.1)

        title = 'Imaginary part of sensor: {} {}'.format(nameToPlot, numberFile1)
        xlabel = 'Frequency [ Hz ]'
        ylabel = 'Imaginary Part'

        ax4.set_title(title)
        ax4.set_xlabel(xlabel)
        ax4.set_ylabel(ylabel)
        ax4.ticklabel_format(axis='y', style='sci',scilimits=(-2,3))

        '''
                    FIFTH PLOT
        '''
        # Plotting amplitude
        ax5 = figure.add_subplot(325)

        amplitude = abs(dataFreq)
        ax5.plot(freq, amplitude, color = colorPlot)
        ax5.set_ylim(top=dataFreq.imag.max() * 1.1)

        title = 'Amplitude of sensor: {} {}'.format(nameToPlot, numberFile1)
        xlabel = 'Frequency [ Hz ]'
        ylabel = 'Amplitude'

        ax5.set_title(title)
        ax5.set_xlabel(xlabel)
        ax5.set_ylabel(ylabel)
        ax5.ticklabel_format(axis='y', style='sci',scilimits=(-2,3))

        self.MplWidgetFreq.removePlot()
        self.MplWidgetFreq.addPlot(figure)


    def plotPSD(self):
        '''
        Plotting PSD
        '''
        figure = Figure()
        figure.set_tight_layout({'rect': [0,0,1,0.95], 'pad':0.5, 'w_pad':0.5, 'h_pad':0.5})

        # Counting number of filled rows in Parameters Selected (paramListFreq)
        numberRowsFull = 0
        for i in range(self.paramListFreq.rowCount()):
            if self.paramListFreq.item(i, 0) is not None:
                numberRowsFull += 1
            else:
                pass

        step = float(self.stepMovingAvarage.toPlainText())
        overlap = float(self.overlapMovingAvarge.toPlainText())

        stepWindow = int(self.windowSample.toPlainText())
        overlapWindow = int(self.overlapSample.toPlainText())
        if self.boxDetrend.currentText() == 'Yes':
            detrendBool = True
        else:
            detrendBool = False
        windowType = self.boxWindowFun.currentText().lower()
        order = self.orderFFT.toPlainText()
        highPassFreq = self.highFreqFFT.toPlainText()
        lowPassFreq = self.lowFreqFFT.toPlainText()

        for i in range(numberRowsFull):

            sensorName1 = self.paramListFreq.item(i, 0).text()
            numberFile1 = self.paramListFreq.item(i, 1).text()
            fullName1 = self.paramListFreq.item(i, 3).text()
            fileName1 = self.fileSelectedDict[numberFile1]

            t = copy.deepcopy(self.testFlight.sensor.get(fileName1)[sensorName1].time)
            timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]

            movingRMS = self.testFlight.sensor[fileName1][sensorName1].movingRMS(overlap, step)
            movingRMSSplitted = [movingRMS[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]



            freqSplitted ,PSDSplitted = self.testFlight.sensor[fileName1].get(sensorName1).PSD(stepWin = stepWindow,
                                                                                               overlapWin = overlapWindow,
                                                                                               win = windowType,
                                                                                               detrendBool = detrendBool,
                                                                                               order = order,
                                                                                               highPassFreq=highPassFreq,
                                                                                               lowPassFreq=lowPassFreq)

            if self.checkKeyAxisName.isChecked():
                nameToPlot = sensorName1
            else:
                if fullName1 == '':
                    nameToPlot = sensorName1
                else:
                    nameToPlot = fullName1

            columns = numberRowsFull
            rows = len(timeSplitted)+1
            if i == 0:
                grid = figure.add_gridspec(rows, columns)
            ax1 = figure.add_subplot(grid[0,i])

            for index in range(len(timeSplitted)):
                ax1.plot(timeSplitted[index], movingRMSSplitted[index], color = 'C{}'.format(index), label='Moving RMS')

            title = '{} {}. Step = {}. Overlap = {}.'.format(nameToPlot,numberFile1, step, overlap)
            ylabel = 'Moving RMS'
            xlabel = 'Time [s]'
            ax1.set_title(title)
            ax1.set_xlabel(xlabel)
            ax1.set_ylabel(ylabel)
            ax1.ticklabel_format(axis='y', style='sci', scilimits=(-2, 3))

            for index in range(len(timeSplitted)):
                freq = freqSplitted[index]
                PSD = PSDSplitted[index]
                ax = figure.add_subplot(grid[index+1,i])
                ax.plot(freq, PSD,color= 'C{}'.format(index),label='Range {}'.format(index+1))
                title = 'PSD of sensor: {} {}'.format(nameToPlot, numberFile1)
                xlabel = 'Frequency [ Hz ]'
                ylabel = '{}'.format(nameToPlot)
                ax.set_title(title)
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)
                ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 3))
                ax.legend()

        if numberRowsFull != 0:
            figure.suptitle('Moving RMS and PSD', fontsize=13)
            self.MplWidgetFreq.removePlot()
            self.MplWidgetFreq.addPlot(figure)

    def printSecondItemFreq(self):
        '''
        Method that acts when user click in a row of Second Parameter Selection
        '''
        self.paramListFreq.clearContents()

        # Saving attributes of sensor selected in Parameters Selection in Main Window
        index1 = self.paramSel.selectedIndexes()[0].row()
        sensorName1 = self.paramSel.item(index1,0).text()
        fullName1 = self.paramSel.item(index1,3).text()
        numberFile1 = self.paramSel.item(index1,1).text()
        units1 = self.paramSel.item(index1, 2).text()

        # Writting sensor in Parameters Selection (paramListFreq)
        self.paramListFreq.setItem(0, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName1))
        self.paramListFreq.setItem(0, 1, PyQt5.QtWidgets.QTableWidgetItem(numberFile1))
        self.paramListFreq.setItem(0, 2, PyQt5.QtWidgets.QTableWidgetItem(units1))
        self.paramListFreq.setItem(0, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName1))

        # If one sensor is selected in Second Parameter Selection (secondParamListFreq)
        if len(self.secondParamListFreq.selectedIndexes()) > 0:
            index2 = self.secondParamListFreq.selectedIndexes()[0].row()
            sensorName2 = self.secondParamListFreq.item(index2,0).text()
            fullName2 = self.secondParamListFreq.item(index2, 3).text()
            numberFile2 = self.secondParamListFreq.item(index2, 1).text()
            units2 = self.secondParamListFreq.item(index2, 2).text()


            self.paramListFreq.setItem(1, 0, PyQt5.QtWidgets.QTableWidgetItem(sensorName2))
            self.paramListFreq.setItem(1, 1, PyQt5.QtWidgets.QTableWidgetItem(numberFile2))
            self.paramListFreq.setItem(1, 2, PyQt5.QtWidgets.QTableWidgetItem(units2))
            self.paramListFreq.setItem(1, 3, PyQt5.QtWidgets.QTableWidgetItem(fullName2))

        # Resizing columns
        self.paramListFreq.resizeColumnToContents(0)
        self.paramListFreq.resizeColumnToContents(1)
        self.paramListFreq.resizeColumnToContents(2)
        self.paramListFreq.resizeColumnToContents(3)

        self.plotPSD()
    '''
        
    ################################################################################################################
    ################################################################################################################

                                            MULTI PLOT FUNCTIONS

    ################################################################################################################
    ################################################################################################################
    '''

    def multiPlot(self):
        '''
        This method acts when Multiple Plots Tab is clicked by the user. Its main function is to have the possibilityy of
        plotting up to 9 sensors in different plots, so the user could see difference between them
        '''
        figure = Figure(constrained_layout=True)

        numberOfSensors = len(self.paramSel.selectedIndexes())
        if numberOfSensors == 1:
            grid = figure.add_gridspec(1, 1)
        elif numberOfSensors == 2:
            grid = figure.add_gridspec(1, 2)
        elif (numberOfSensors == 3) or (numberOfSensors == 4):
            grid = figure.add_gridspec(2, 2)
        elif (numberOfSensors == 5) or (numberOfSensors == 6):
            grid = figure.add_gridspec(2, 3)
        elif (numberOfSensors == 7) or (numberOfSensors == 8) or (numberOfSensors == 9):
            grid = figure.add_gridspec(3, 3)
        else:
            pass

        # If complete signal is checked...
        if self.checkCompleteSignalMulti.isChecked():
            # Changing super title
            figure.suptitle('Complete signal', fontsize = 15)

            # Loop through all elements:
            i = 0
            for index in self.paramSel.selectedIndexes():

                if i == 0:
                    row = 0
                    column = 0
                elif i == 1:
                    row = 0
                    column = 1
                elif i == 2:
                    row = 1
                    column = 0
                elif i == 3:
                    row = 1
                    column = 1
                elif i == 4:
                    row = 0
                    column = 2
                elif i == 5:
                    row = 1
                    column = 2
                elif i == 6:
                    row = 2
                    column = 0
                elif i == 7:
                    row = 2
                    column = 1
                elif i == 8:
                    row = 2
                    column = 2
                else:
                    pass

                # Attributes of the sensor
                sensorName = self.paramSel.item(index.row(), 0).text()
                numberFile = self.paramSel.item(index.row(), 1).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                units = self.paramSel.item(index.row(), 2).text()
                fileName = self.fileSelectedDict[numberFile]

                # Checking what name is going to be used in the title and the legend
                if self.checkKeyAxisName.isChecked():
                    nameToPlot = sensorName
                else:
                    if fullName == '':
                        nameToPlot = sensorName
                    else:
                        nameToPlot = fullName


                # Saving data and time
                data = self.testFlight.sensor[fileName].get(sensorName).data
                time = self.testFlight.sensor[fileName].get(sensorName).time

                title = '{} {} - [{}] - Time [s]'.format(nameToPlot, numberFile, units)
                xlabel = 'Time [ s ]'
                ylabel = '{} {} [{}]'.format(nameToPlot, numberFile, units)

                ax = figure.add_subplot(grid[row, column])
                ax.plot(time, data, '-b')
                ax.set_title(title, color='brown')
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)

                if i == 0:
                    yMin = ax.get_ylim()[0]
                    yMax = ax.get_ylim()[1]
                    xMin = ax.get_xlim()[0]
                    xMax = ax.get_xlim()[1]
                else:
                    if ax.get_ylim()[0] < yMin:
                        yMin = ax.get_ylim()[0]
                    if ax.get_ylim()[1] > yMax:
                        yMax = ax.get_ylim()[1]
                    if ax.get_xlim()[0] < xMin:
                        xMin = ax.get_xlim()[0]
                    if ax.get_xlim()[1] > xMax:
                        xMax = ax.get_xlim()[1]

                i+=1

        # If steady signal is checked
        if self.checkSteadySignalMulti.isChecked():
            # Changing super title
            figure.suptitle('Steady signal', fontsize=15)
            # Loop through all sensors
            x = 0
            for index in self.paramSel.selectedIndexes():

                if x == 0:
                    row = 0
                    column = 0
                elif x == 1:
                    row = 0
                    column = 1
                elif x == 2:
                    row = 1
                    column = 0
                elif x == 3:
                    row = 1
                    column = 1
                elif x == 4:
                    row = 0
                    column = 2
                elif x == 5:
                    row = 1
                    column = 2
                elif x == 6:
                    row = 2
                    column = 0
                elif x == 7:
                    row = 2
                    column = 1
                elif x == 8:
                    row = 2
                    column = 2
                else:
                    pass

                # Saving attributes of the sensor
                sensorName = self.paramSel.item(index.row(), 0).text()
                numberFile = self.paramSel.item(index.row(), 1).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                units = self.paramSel.item(index.row(), 2).text()
                fileName = self.fileSelectedDict[numberFile]

                # Checking what name is going to be used in the title and the legend
                if self.checkKeyAxisName.isChecked():
                    nameToPlot = sensorName
                else:
                    if fullName == '':
                        nameToPlot = sensorName
                    else:
                        nameToPlot = fullName

                t = self.testFlight.sensor.get(fileName)[sensorName].time
                step = float(self.stepMovingAvarage.toPlainText())
                overlap = float(self.overlapMovingAvarge.toPlainText())
                steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

                title = '{} {} - [{}]. Step={}s. Overlap={}%'.format(nameToPlot,numberFile, units, step, overlap)
                xlabel = 'Time [ s ]'
                ylabel = '{} {} [{}]'.format(nameToPlot, numberFile, units)

                ax = figure.add_subplot(grid[row, column])
                ax.plot(t, steadyData, '-b')
                ax.set_title(title, color = 'brown')
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)

                if x == 0:
                    yMin = ax.get_ylim()[0]
                    yMax = ax.get_ylim()[1]
                    xMin = ax.get_xlim()[0]
                    xMax = ax.get_xlim()[1]
                else:
                    if ax.get_ylim()[0] < yMin:
                        yMin = ax.get_ylim()[0]
                    if ax.get_ylim()[1] > yMax:
                        yMax = ax.get_ylim()[1]
                    if ax.get_xlim()[0] < xMin:
                        xMin = ax.get_xlim()[0]
                    if ax.get_xlim()[1] > xMax:
                        xMax = ax.get_xlim()[1]

                x += 1

        # If vibration signal is checked...
        if self.checkVibrationsSignalMulti.isChecked():
            figure.suptitle('Vibrations', fontsize=15)
            m = 0
            # Loop through all sensors...
            for index in self.paramSel.selectedIndexes():

                if m == 0:
                    row = 0
                    column = 0
                elif m == 1:
                    row = 0
                    column = 1
                elif m == 2:
                    row = 1
                    column = 0
                elif m == 3:
                    row = 1
                    column = 1
                elif m == 4:
                    row = 0
                    column = 2
                elif m == 5:
                    row = 1
                    column = 2
                elif m == 6:
                    row = 2
                    column = 0
                elif m == 7:
                    row = 2
                    column = 1
                elif m == 8:
                    row = 2
                    column = 2
                else:
                    pass

                # Getting attributes of sensor
                sensorName = self.paramSel.item(index.row(), 0).text()
                numberFile = self.paramSel.item(index.row(), 1).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                units = self.paramSel.item(index.row(), 2).text()
                fileName = self.fileSelectedDict[numberFile]

                # Checking what name is going to be used in the title and the legend
                if self.checkKeyAxisName.isChecked():
                    nameToPlot = sensorName
                else:
                    if fullName == '':
                        nameToPlot = sensorName
                    else:
                        nameToPlot = fullName

                # Calculating vibrations
                step = float(self.stepMovingAvarage.toPlainText())
                overlap = float(self.overlapMovingAvarge.toPlainText())
                t = self.testFlight.sensor.get(fileName)[sensorName].time
                vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)

                # Plotting...
                title = '{} {} - [{}]. Step={}s. Overlap={}%.'.format(nameToPlot,numberFile, units, step, overlap)
                xlabel = 'Time [ s ]'
                ylabel = '{} {} [{}]'.format(nameToPlot, numberFile, units)

                ax = figure.add_subplot(grid[row, column])
                ax.plot(t, vibrations, '-b')
                ax.set_title(title, color = 'brown')
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)

                if m == 0:
                    yMin = ax.get_ylim()[0]
                    yMax = ax.get_ylim()[1]
                    xMin = ax.get_xlim()[0]
                    xMax = ax.get_xlim()[1]
                else:
                    if ax.get_ylim()[0] < yMin:
                        yMin = ax.get_ylim()[0]
                    if ax.get_ylim()[1] > yMax:
                        yMax = ax.get_ylim()[1]
                    if ax.get_xlim()[0] < xMin:
                        xMin = ax.get_xlim()[0]
                    if ax.get_xlim()[1] > xMax:
                        xMax = ax.get_xlim()[1]

                m += 1

        # If plot all signals is checked...
        if self.checkAllSignalsMulti.isChecked():
            figure.suptitle('Complete+Steady+Vibration', fontsize=15)
            l = 0
            # Loop through all sensors
            for index in self.paramSel.selectedIndexes():

                if l == 0:
                    row = 0
                    column = 0
                elif l == 1:
                    row = 0
                    column = 1
                elif l == 2:
                    row = 1
                    column = 0
                elif l == 3:
                    row = 1
                    column = 1
                elif l == 4:
                    row = 0
                    column = 2
                elif l == 5:
                    row = 1
                    column = 2
                elif l == 6:
                    row = 2
                    column = 0
                elif l == 7:
                    row = 2
                    column = 1
                elif l == 8:
                    row = 2
                    column = 2
                else:
                    pass

                # Getting attributes of sensor
                sensorName = self.paramSel.item(index.row(), 0).text()
                numberFile = self.paramSel.item(index.row(), 1).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                units = self.paramSel.item(index.row(), 2).text()
                fileName = self.fileSelectedDict[numberFile]

                # Checking what name is going to be used for the title and the legend
                if self.checkKeyAxisName.isChecked():
                    nameToPlot = sensorName
                else:
                    if fullName == '':
                        nameToPlot = sensorName
                    else:
                        nameToPlot = fullName

                # Creating a dictionary that will be used to know what ranges are going to be plotted, reading them
                # from selectionPlotAllSignals.
                checkPlots = {}
                for i in range(self.selectionPlotAllSignals.rowCount()):
                    rowName = 'Range' + str(i)
                    checkComplete = int(self.selectionPlotAllSignals.item(i, 0).text())
                    checkSteady = int(self.selectionPlotAllSignals.item(i, 1).text())
                    checkVibrations = int(self.selectionPlotAllSignals.item(i, 2).text())
                    checkPlots[rowName] = [checkComplete, checkSteady, checkVibrations]

                # Calculating all the data that is going to be plotted
                step = float(self.stepMovingAvarage.toPlainText())
                overlap = float(self.overlapMovingAvarge.toPlainText())

                t = self.testFlight.sensor.get(fileName)[sensorName].time
                y = self.testFlight.sensor.get(fileName)[sensorName].data
                vibrations = self.testFlight.sensor[fileName][sensorName].detrend(overlap, step)
                steadyData = self.testFlight.sensor[fileName][sensorName].moving_average(overlap, step)

                # Splitting time in ranges (depending on if the user has cutted data)
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]

                # Loop through all ranges. The data is going to be changed, as well as it was done in the method
                # plotAllSignalsMain()
                i = 0
                for timeRange in timeSplitted:
                    rangeName = 'Range' + str(i)
                    indexRange = []
                    for timeValue in timeRange:
                        indexRange.append(np.where(t == timeValue)[0][0])

                    if checkPlots[rangeName][1] == 0:
                        steadyData[indexRange] = y[indexRange]
                        vibrations[indexRange] = 0
                    else:
                        pass

                    if checkPlots[rangeName][2] == 0:
                        steadyData[indexRange] = y[indexRange]
                        vibrations[indexRange] = 0
                    else:
                        pass

                    if checkPlots[rangeName][0] == 0:
                        y[indexRange] = np.nan
                    else:
                        pass

                    i += 1

                # Plotting...
                title = '{} {} - [{}] - Time [s]'.format(nameToPlot, numberFile, units)
                xlabel = 'Time [ s ]'
                ylabel = '{} {} [{}]'.format(nameToPlot, numberFile, units)

                ax = figure.add_subplot(grid[row, column])
                ax.plot(t, y, '-b', label = 'Complete')
                ax.plot(t, steadyData,'-r', label = 'Seady')
                ax.plot(t, vibrations,'-g', label = 'Vibration')
                ax.set_title(title, color = 'brown')
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)

                if l == 0:
                    yMin = ax.get_ylim()[0]
                    yMax = ax.get_ylim()[1]
                    xMin = ax.get_xlim()[0]
                    xMax = ax.get_xlim()[1]
                else:
                    if ax.get_ylim()[0] < yMin:
                        yMin = ax.get_ylim()[0]
                    if ax.get_ylim()[1] > yMax:
                        yMax = ax.get_ylim()[1]
                    if ax.get_xlim()[0] < xMin:
                        xMin = ax.get_xlim()[0]
                    if ax.get_xlim()[1] > xMax:
                        xMax = ax.get_xlim()[1]

                l += 1

        # If plot PSD is checked...
        if self.checkPSDMulti.isChecked():
            figure.suptitle('PSD', fontsize=15)

            stepWindow = int(self.windowSample.toPlainText())
            overlapWindow = int(self.overlapSample.toPlainText())
            if self.boxDetrend.currentText() == 'Yes':
                detrendBool = True
            else:
                detrendBool = False
            windowType = self.boxWindowFun.currentText().lower()
            order = self.orderFFT.toPlainText()
            highPassFreq = self.highFreqFFT.toPlainText()
            lowPassFreq = self.lowFreqFFT.toPlainText()

            n = 0
            # Loop through all sensors...
            for index in self.paramSel.selectedIndexes():

                if n == 0:
                    row = 0
                    column = 0
                elif n == 1:
                    row = 0
                    column = 1
                elif n == 2:
                    row = 1
                    column = 0
                elif n == 3:
                    row = 1
                    column = 1
                elif n == 4:
                    row = 0
                    column = 2
                elif n == 5:
                    row = 1
                    column = 2
                elif n == 6:
                    row = 2
                    column = 0
                elif n == 7:
                    row = 2
                    column = 1
                elif n == 8:
                    row = 2
                    column = 2
                else:
                    pass

                # Getting attributes of the sensor
                sensorName = self.paramSel.item(index.row(), 0).text()
                numberFile = self.paramSel.item(index.row(), 1).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                units = self.paramSel.item(index.row(), 2).text()
                fileName = self.fileSelectedDict[numberFile]

                # Checking what name is going to be used for the title and the legend
                if self.checkKeyAxisName.isChecked():
                    nameToPlot = sensorName
                else:
                    if fullName == '':
                        nameToPlot = sensorName
                    else:
                        nameToPlot = fullName

                # Calculating data
                t = copy.deepcopy(self.testFlight.sensor.get(fileName)[sensorName].time)
                timeSplitted = [t[s] for s in np.ma.clump_unmasked(np.ma.masked_invalid(t))]
                freqSplitted, PSDSplitted = self.testFlight.sensor[fileName].get(sensorName).PSD(stepWin = stepWindow,
                                                                                               overlapWin = overlapWindow,
                                                                                               win = windowType,
                                                                                               detrendBool = detrendBool,
                                                                                               order = order,
                                                                                               highPassFreq=highPassFreq,
                                                                                               lowPassFreq=lowPassFreq)

                title = '{} {} - [{}] - Time [s]'.format(nameToPlot, numberFile, units)
                xlabel = 'Time [ s ]'
                ylabel = '{}'.format(nameToPlot)

                # Only is possible to plot PSD without ranges of time
                if len(timeSplitted) == 1:
                    freq = freqSplitted[0]
                    PSD = PSDSplitted[0]

                    ax = figure.add_subplot(grid[row, column])
                    ax.plot(freq, PSD)
                    ax.set_xlim(left=0, right=freq[-1])
                    ax.set_title(title, color = 'brown')
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)
                    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 3))

                else:
                    logger.info('PSD in Multiple Plot Tab can only be plotted without ranges of time')
                    break

                if n == 0:
                    yMin = ax.get_ylim()[0]
                    yMax = ax.get_ylim()[1]
                    xMin = ax.get_xlim()[0]
                    xMax = ax.get_xlim()[1]
                else:
                    if ax.get_ylim()[0] < yMin:
                        yMin = ax.get_ylim()[0]
                    if ax.get_ylim()[1] > yMax:
                        yMax = ax.get_ylim()[1]
                    if ax.get_xlim()[0] < xMin:
                        xMin = ax.get_xlim()[0]
                    if ax.get_xlim()[1] > xMax:
                        xMax = ax.get_xlim()[1]

                n += 1

        # If plot displacements is checked...
        if self.checkDisplacementsMulti.isChecked():
            figure.suptitle('Displacements', fontsize=15)

            lowFreqDisp = float(self.lowFreqDisp.toPlainText())
            highFreqDisp = float(self.highFreqDisp.toPlainText())
            windowFun = self.boxWindowFunDisp.currentText().lower()

            x = 0
            # Loop through all sensors...
            for index in self.paramSel.selectedIndexes():

                if x == 0:
                    row = 0
                    column = 0
                elif x == 1:
                    row = 0
                    column = 1
                elif x == 2:
                    row = 1
                    column = 0
                elif x == 3:
                    row = 1
                    column = 1
                elif x == 4:
                    row = 0
                    column = 2
                elif x == 5:
                    row = 1
                    column = 2
                elif x == 6:
                    row = 2
                    column = 0
                elif x == 7:
                    row = 2
                    column = 1
                elif x == 8:
                    row = 2
                    column = 2
                else:
                    pass

                # Getting attributes of the sensor
                sensorName = self.paramSel.item(index.row(), 0).text()
                numberFile = self.paramSel.item(index.row(), 1).text()
                fullName = self.paramSel.item(index.row(), 3).text()
                units = self.paramSel.item(index.row(), 2).text()
                fileName = self.fileSelectedDict[numberFile]

                # Checking what name is going to be used for the title and the legend
                if self.checkKeyAxisName.isChecked():
                    nameToPlot = sensorName
                else:
                    if fullName == '':
                        nameToPlot = sensorName
                    else:
                        nameToPlot = fullName

                # Plotting
                title = '{} {} - [{}] - Time [s]'.format(nameToPlot, numberFile, units)
                xlabel = 'Time [ s ]'
                ylabel = 'Displacements [mm]'

                t = self.testFlight.sensor.get(fileName)[sensorName].time
                displacements = self.testFlight.sensor[fileName][sensorName].displacements(lowFreqDisp,highFreqDisp,
                                                                                           win=windowFun)

                ax = figure.add_subplot(grid[row, column])
                ax.plot(t, displacements, '-b')
                ax.set_title(title, color = 'brown')
                ax.set_xlabel(xlabel)
                ax.set_ylabel(ylabel)

                if x == 0:
                    yMin = ax.get_ylim()[0]
                    yMax = ax.get_ylim()[1]
                    xMin = ax.get_xlim()[0]
                    xMax = ax.get_xlim()[1]
                else:
                    if ax.get_ylim()[0] < yMin:
                        yMin = ax.get_ylim()[0]
                    if ax.get_ylim()[1] > yMax:
                        yMax = ax.get_ylim()[1]
                    if ax.get_xlim()[0] < xMin:
                        xMin = ax.get_xlim()[0]
                    if ax.get_xlim()[1] > xMax:
                        xMax = ax.get_xlim()[1]
                x += 1
            else:
                pass

        # Changing axis limits if user has checked it
        if self.checkSameAxesTrue.isChecked():
            logger.info('Changing limits of Multiple Plots tab...')
            for ax in figure.axes:
                ax.set_ylim(yMin, yMax)
                ax.set_xlim(xMin, xMax)

        self.MplWidgetMultiPlot.removePlot()
        if self.checkFollowModeYesMulti.isChecked():
            self.MplWidgetMultiPlot.addDynamicPlot(figure)
        else:
            self.MplWidgetMultiPlot.addPlot(figure)

if __name__ == "__main__":
    print('PYFAT.log is going to be saved in:')
    print(os.getcwd())

    nameLog = '{}\{}'.format(os.getcwd(), 'PYFAT.log')

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fileHandler = logging.FileHandler(nameLog, mode='w')
    fileHandler.setLevel(logging.INFO)
    # create console handler with a higher log level
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fileHandler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)

    dirname = os.path.dirname(PyQt5.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

    sys._excepthook = sys.excepthook
    def exception_hook(exctype, value, traceback):
        print(exctype, value, traceback)
        sys._excepthook(exctype, value, traceback)
    sys.excepthook = exception_hook

    app = PyQt5.QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.show()
    sys.exit(app.exec_())