from pyqtgraph import AxisItem, DateAxisItem
from datetime import timedelta

import pyqtgraph as pg

from pyqtgraph import AxisItem
from datetime import datetime, timedelta

class MillisecondAxisItem(AxisItem):
    def tickStrings(self, values, scale, spacing):
        ms_values = [value / 1000 for value in values]
        return [datetime.utcfromtimestamp(value).strftime("%H:%M:%S.%f")[:-3] for value in ms_values]


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

        self.dateTimeAxis = MillisecondAxisItem(orientation='bottom')  # Use custom MillisecondAxisItem
        self.plotItem.setAxisItems({'bottom': self.dateTimeAxis})


    def plot(self, x, y, name='', time_window=None, *args, **kwargs):
        if x.dtype == 'datetime64[ns]':

            x = x.astype('int64') // 10 ** 6  # Convert to milliseconds

        if name in self.series_curves:
            self.series_curves[name].setData(x, y)
            if time_window is not None:
                self.plotItem.setXRange(x[-1] - time_window, x[-1])
            elif time_window is None:
                self.plotItem.enableAutoRange(axis='x')
        else:
            curve = self.plotItem.plot(x, y, *args, **kwargs)
            self.series_curves[name] = curve
            self.legend.addItem(curve, name)

