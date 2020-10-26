from matplotlib.figure import Figure
import numpy as np
import logging
from PyQt5 import QtWidgets
'''
The pyplot module defines wrapper functions that are meant to automate the creation of the interactive plotting window,
and they will most likely cause problems for any custom GUI object. TheFigure class imported above is a very generic
plotting container for all aspects of our plot. Instances of this object have the same methods as the figure objects
created using pyplot.figure
'''

from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
'''
These are both custom Qt widgets. A canvas contains and displays a Figure instance, and a navigation toolbar is the 
widget containing the buttons for interacting with the plot.
'''
from PyQt5.QtWidgets import *

# This class has been created to allow 'Follow Mode' in the plots
class SnaptoCursor(object):
    def __init__(self, fig, listPYFAT = None):

        self.listWidget = listPYFAT
        self.countClicks = 0
        self.fig = fig
        self.clickedPoints = []
        self.dataDict = {}
        for index in range(len(self.fig.axes)):
            ax = self.fig.axes[index]
            self.dataDict[index] = {}
            xData = ax.lines[0].get_xdata()
            yData = ax.lines[0].get_ydata()
            self.dataDict[index]['x'] = xData[~np.isnan(xData)]
            self.dataDict[index]['y'] = yData[~np.isnan(xData)]
            self.dataDict[index]['totalLines'] = len(ax.lines)

    def mouse_move(self, event):
        if event.inaxes:
            for index in range(len(self.fig.axes)):
                ax = self.fig.axes[index]
                # If there are more lines than the original plot, it means that a xvline is in the plot. It has
                # to be removed before plotting the newer one.
                while len(ax.lines) > self.dataDict[index]['totalLines']:
                    ax.lines.pop(-1)

                for text in ax.texts:
                    text.set_visible(False)

                ly = ax.axvline(color='k', alpha=0.2)
                text = ax.text(0, 0, '', fontsize=10, color="b",zorder=19, verticalalignment = 'bottom',
                               horizontalalignment = 'left', transform = ax.transAxes)

                indx = np.searchsorted(self.dataDict[index]['x'], [event.xdata])[0]
                try:
                    x = self.dataDict[index]['x'][indx]
                    y = self.dataDict[index]['y'][indx]
                    marker = ax.plot([x], [y], marker="o", color='r',zorder=18)
                    ly.set_xdata(x)
                    text.set_text('x={:.3f}\ny={:.3e}'.format(x, y))
                    ax.figure.canvas.draw()
                except:
                    pass
        else:
            pass

    def onclick(self,event):
        logger = logging.getLogger('__main__')
        ax = self.fig.axes[0]
        if event.inaxes:
            x = event.xdata
            y = event.ydata
            ax.figure.canvas.draw()
            logger.info('User has clicked coordinates: x = {:.3f}'.format(x))
            self.clickedPoints.append(event.xdata)
            self.countClicks += 1
            if self.countClicks%2 == 0:
                rangeNumber = int(self.countClicks/2)
                time1 = self.clickedPoints[self.countClicks-2]
                time2 = self.clickedPoints[self.countClicks-1]
                listItem = QtWidgets.QListWidgetItem('Range {}: {:.2f}-{:.2f} [s]'.format(rangeNumber, time1, time2))
                self.listWidget.insertItem(0, listItem)
            return event.xdata, event.ydata

    def resetCounClicks(self):
        self.countClicks = 0
        self.clickedPoints = []


class MplWidget(QWidget):
    '''
    This class creates figures in the UI
    '''
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.canvas = FigureCanvas(Figure())
        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.vertical_layout.addWidget(self.toolbar)
        self.setLayout(self.vertical_layout)
        self.canvas.draw()

    def removePlot(self, ):
        self.vertical_layout.removeWidget(self.canvas)
        self.canvas.close()
        self.vertical_layout.removeWidget(self.toolbar)
        self.toolbar.close()
        self.setLayout(self.vertical_layout)

    def addPlot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.vertical_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.vertical_layout.addWidget(self.toolbar)
        self.canvas.draw()
        self.setLayout(self.vertical_layout)


    def addDynamicPlot(self, fig):
        self.canvas = FigureCanvas(fig)
        self.vertical_layout.addWidget(self.canvas)
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.vertical_layout.addWidget(self.toolbar)
        self.setLayout(self.vertical_layout)
        self.cursor = SnaptoCursor(fig)
        self.cid = self.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)

    def selectPointPlot(self, fig, QListWidget):
        self.cursor = SnaptoCursor(fig, QListWidget)
        self.canvas.mpl_connect('button_press_event', self.cursor.onclick)
        self.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
