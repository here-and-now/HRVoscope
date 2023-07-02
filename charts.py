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

    def plot(self, x, y, name='', *args, **kwargs):
        if name in self.series_curves:
            self.series_curves[name].setData(x, y)
        else:
            curve = self.plotItem.plot(x, y, *args, **kwargs)
            self.series_curves[name] = curve
            self.legend.addItem(curve, name)
