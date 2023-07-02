from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


class XYSeriesWidget(pg.GraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotItem = pg.PlotItem()
        self.setCentralItem(self.plotItem)
        self.plotItem.showGrid(x=True, y=True)



        self.setBackground('w')  # Set background color to white


    def plot(self, x, y, *args, **kwargs):
        self.plotItem.plot(x, y, *args, **kwargs)
