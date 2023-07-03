from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


class XYSeriesWidget(pg.GraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.plotItem = pg.PlotItem()
        self.setCentralItem(self.plotItem)
        self.plotItem.showGrid(x=True, y=True)

        self.setBackground('w')  # Set background color to white

        self.series_curves = {}  # Dictionary to store plotted curves for each series
        self.legend = pg.LegendItem()  # Create legend
        self.legend.setParentItem(self.plotItem.graphicsItem())
        self.legend.anchor((1, 1), (1, 1))  # Align to the top-right corner of the plot

        self.dateTimeAxis = pg.DateAxisItem(orientation='bottom')  # Create DateAxisItem
        self.plotItem.setAxisItems({'bottom': self.dateTimeAxis})

    def plot(self, x, y, name='', time_window=None, *args, **kwargs):
        # check if x = datetime64[ns] and convert to unix timestamp
        if x.dtype == 'datetime64[ns]':
            x = x.astype('int64') // 10 ** 9
        if name in self.series_curves:
            self.series_curves[name].setData(x, y)
            print(x[-1])
            if time_window is not None:
                self.plotItem.setXRange(x[-1] - time_window, x[-1])
        else:
            curve = self.plotItem.plot(x, y, *args, **kwargs)
            self.series_curves[name] = curve
            self.legend.addItem(curve, name)



