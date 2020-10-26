import logging
from PyQt5 import QtWidgets
# Importing Search Window - User Interface (created with QtDesigner)
from searchCDFWindow import Ui_Dialog as dialogSearchWind
import os

class searchCDFWindow(QtWidgets.QDialog,dialogSearchWind):
    '''
    This class creates a specific window to look for CDFs and save their paths.
    '''
    def __init__(self, parent = None):


        super(searchCDFWindow,self).__init__(parent)
        self.setupUi(self)

        '''
        Signals of the window
        '''
        self.buttonOneCDF.clicked.connect(self.findOneCDF)
        self.buttonMultipleCDF.clicked.connect(self.findMultipleCDF)
        self.buttonDeletePath.clicked.connect(self.deleteRow)
        self.buttonAccept.clicked.connect(self.returnValue)
        if self.checkSameSampleYes.isChecked():
            self.boolSameSampleRate = True
        else:
            self.boolSameSampleRate = False
        if self.checkReadUnitsYes.isChecked():
            self.boolReadUnits = True
        else:
            self.boolReadUnits = False

        self.checkSameSampleYes.clicked.connect(self.checkRadioButtons)
        self.checkSameSampleNo.clicked.connect(self.checkRadioButtons)
        self.checkReadUnitsYes.clicked.connect(self.checkRadioButtons)
        self.checkReadUnitsNo.clicked.connect(self.checkRadioButtons)
        '''
        Atributes of this class.
        '''
        # List used to return all paths of the CDFs that the user has looked for
        self.listPathCDF = []

    def checkRadioButtons(self):
        if self.checkSameSampleYes.isChecked():
            self.boolSameSampleRate = True
        else:
            self.boolSameSampleRate = False
        if self.checkReadUnitsYes.isChecked():
            self.boolReadUnits = True
        else:
            self.boolReadUnits = False

    def findOneCDF(self):
        '''
        When user does not use any input TXT to look for the CDF. He looks in the specific folder where are located.
        '''
        listPath = QtWidgets.QFileDialog.getOpenFileNames(self, 'Search CDFs', os.getenv('HOME'),
                                           filter='Text files (*.cdf)')[0]

        # Inserting the paths in QListWidget
        for path in listPath:
            if path != '':
                self.listPathCDFWidget.insertItem(0, QtWidgets.QListWidgetItem(path))

    def findMultipleCDF(self):
        '''
        When user looks all CDFs using a specific input TXT
        '''
        logger = logging.getLogger('__main__')
        pathTXT = QtWidgets.QFileDialog.getOpenFileName(self, 'Search TXT with CDF information', os.getenv('HOME'),
                                           filter='Text files (*.txt)')[0]

        if pathTXT != '':
            fileTXT = open(pathTXT, 'r')

            # Reading input TXT
            listNameCDF = []
            listPathCDF = []
            for fileLine in fileTXT.readlines():
                fileLine = fileLine.strip()
                if fileLine == 'CDF_FILES':
                    pass
                elif fileLine == '[end]':
                    break
                else:
                    if fileLine[-3:] == 'cdf':
                        listNameCDF.append(fileLine)
                    else:
                        listPathCDF.append(fileLine)

            if len(listNameCDF) == len(listPathCDF):
                # Inserting the paths in QListWidget
                for index in range(len(listNameCDF)):
                    path = '{}{}{}'.format(listPathCDF[index],os.path.sep, listNameCDF[index])
                    self.listPathCDFWidget.insertItem(0, QtWidgets.QListWidgetItem(path))

            else:
                logger.info('User forgot to write one or more directories of some CDFs in the input...')
                logger.info('Please, check it')
                logger.info('****************************************')

    def deleteRow(self):
        '''
        Delete selected items of QListWidget.
        '''
        listSelectedItems = self.listPathCDFWidget.selectedItems()
        if not listSelectedItems:
            pass
        else:
            for selectedItem in self.listPathCDFWidget.selectedItems():
                self.listPathCDFWidget.takeItem(self.listPathCDFWidget.row(selectedItem))

    def returnValue(self):
        '''
        Return all the paths that are written in the QListWidget
        '''
        for row in range(self.listPathCDFWidget.count()):
            self.listPathCDF.append(self.listPathCDFWidget.item(row).text())
        # Closing the window
        self.close()