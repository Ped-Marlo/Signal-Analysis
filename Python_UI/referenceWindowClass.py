from PyQt5 import QtWidgets
import numpy as np
import os
# Importing Reference Window - User Interface (created with QtDesigner)
from referenceWindow import Ui_Dialog as dialogReferenceWind

class referenceWindow(QtWidgets.QDialog,dialogReferenceWind):
    '''
    This class creates a specific window to look for the reference of all the CDFs.
    '''

    def __init__(self, cdfFiles, parent = None):
        super(referenceWindow,self).__init__(parent)
        self.setupUi(self)

        '''
        Signals of the window
        '''
        self.pushButton.clicked.connect(self.changeReferenceCDF)
        self.pushButtonTXT.clicked.connect(self.changeReferenceTXT)

        '''
        Attributes of the class
        '''
        # self.dictReferenceTXT will be used if an input TXT is used as reference
        self.dictReferenceTXT = np.nan
        # self.filesReference will be used if other CDFs are used as references
        self.filesReference = np.nan


        # Writting in the QListWidget all the CDFs that have been downloaded in the Main Window
        self.fileSelect.clear()
        for fileName in cdfFiles:
            self.fileSelect.insertItem(0, QtWidgets.QListWidgetItem(str(fileName)))

    def changeReferenceCDF(self):
        '''
        Saving all selected paths of the QListWidget in the attribute self.filesReference
        '''
        self.filesReference = []
        for fileName in self.fileSelect.selectedItems():
            indexSpace = fileName.text().find(' ')
            fileName = fileName.text()[:indexSpace]
            self.filesReference.append(fileName)

        # Closing window
        self.close()

    def changeReferenceTXT(self):
        '''
        Saving all the paths of the input TXT in the attribute self.dictReferenceTXT
        '''
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Search TXT reference', os.getenv('HOME'),filter = 'Text files (*.txt)')[0]
        if path != '':

            fileTXT = open(path, 'r')
            self.dictReferenceTXT = {}
            # Reading input TXT
            readOffsets = False
            for line in fileTXT:
                if '[END]' in line:
                    readOffsets = False
                    break
                elif readOffsets:
                    line = line.strip()
                    line = line.replace(' ', '')
                    lineSplitted = line.split(':')
                    print(lineSplitted)
                    self.dictReferenceTXT[lineSplitted[0]] = lineSplitted[1]
                else:
                    if '[Parameters with offset]' in line:
                        readOffsets = True
                    else:
                        pass
            fileTXT.close()
            # Closing window
            self.close()

    def returnReferenceCDF(self):
        '''
        Returning the attribute self.filesReference
        '''
        return self.filesReference

    def returnReferenceTXT(self):
        '''
            Returning the attribute self.dictReferenceTXT
        '''
        return self.dictReferenceTXT