from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QComboBox,
    QSlider,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QFileDialog,
    QProgressBar,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QMargins, QSize
from PySide6.QtGui import QIcon, QLinearGradient, QBrush, QGradient, QColor
from PySide6.QtCharts import QChartView, QChart, QSplineSeries, QValueAxis, QAreaSeries

from pacer import Pacer

# from sensor import SensorClient
from bluetooth_debugging.ibi_ecg_acc_test import SensorClient


BLUE = QColor(135, 206, 250)
WHITE = QColor(255, 255, 255)
GREEN = QColor(0, 255, 0)
YELLOW = QColor(255, 255, 0)
RED = QColor(255, 0, 0)


class View(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.setWindowTitle("test")
        # self.setWindowIcon(QIcon("icon.png"))

        self.model = model

        import numpy as np

        array = np.linspace(0, len(self.model.ibi_buffer) - 1, len(self.model.ibi_buffer))

        self.ibi_widget = XYSeriesWidget(array, self.model.ibi_buffer)
        # self.ibi_widget = XYSeriesWidget([0,1,3], [0,1,3])
        self.sensor = SensorClient()
        self.sensor.connect_client(self.sensor)

        self.model.ibi_buffer_update.connect(self.plot_ibi)

        self.sensor.ibi_update.connect(self.model.update_ibi_buffer)


        # Layout stuff
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.ibi_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)

        self.setCentralWidget(central_widget)

    def plot_ibi(self, ibi):
        self.ibi_widget.update_series(*ibi.value)
    def plot_ecg_buffer(self, ecg):
        self.xy.update_series(ecg)
    def plot_pacer_disk(self):
        coordinates = self.pacer.update(self.model.breathing_rate)
        self.pacer_widget.update_series(*coordinates)

class PacerWidget(QChartView):
    def __init__(self, x_values=None, y_values=None, color=BLUE):
        super().__init__()

        self.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Fixed,  # enforce self.sizeHint by fixing horizontal (width) policy
                QSizePolicy.Preferred,
            )
        )

        self.plot = QChart()
        self.plot.legend().setVisible(False)
        self.plot.setBackgroundRoundness(0)
        self.plot.setMargins(QMargins(0, 0, 0, 0))

        self.disc_circumference_coord = QSplineSeries()
        if x_values is not None and y_values is not None:
            self._instantiate_series(x_values, y_values)
        self.disk = QAreaSeries(self.disc_circumference_coord)
        self.disk.setColor(color)
        self.plot.addSeries(self.disk)

        self.x_axis = QValueAxis()
        self.x_axis.setRange(-1, 1)
        self.x_axis.setVisible(False)
        self.plot.addAxis(self.x_axis, Qt.AlignBottom)
        self.disk.attachAxis(self.x_axis)

        self.y_axis = QValueAxis()
        self.y_axis.setRange(-1, 1)
        self.y_axis.setVisible(False)
        self.plot.addAxis(self.y_axis, Qt.AlignLeft)
        self.disk.attachAxis(self.y_axis)

        self.setChart(self.plot)

    def _instantiate_series(self, x_values, y_values):
        for x, y in zip(x_values, y_values):
            self.disc_circumference_coord.append(x, y)

    def update_series(self, x_values, y_values):
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            self.disc_circumference_coord.replace(i, x, y)

    def sizeHint(self):
        height = self.size().height()
        return QSize(height, height)  # force square aspect ratio

    def resizeEvent(self, event):
        if self.size().width() != self.size().height():
            self.updateGeometry()  # adjusts geometry based on sizeHint
        return super().resizeEvent(event)

class XYSeriesWidget(QChartView):
    def __init__(self, x_values=None, y_values=None, line_color=BLUE):
        super().__init__()

        self.plot = QChart()
        self.plot.legend().setVisible(False)
        self.plot.setBackgroundRoundness(0)
        self.plot.setMargins(QMargins(0, 0, 0, 0))

        self.time_series = QSplineSeries()
        self.plot.addSeries(self.time_series)
        pen = self.time_series.pen()
        pen.setWidth(4)
        pen.setColor(line_color)
        self.time_series.setPen(pen)
        if x_values is not None and y_values is not None:
            print('not empty')
            self._instantiate_series(x_values, y_values)

        self.x_axis = QValueAxis()
        self.x_axis.setLabelFormat("%i")
        self.x_axis.setRange(0, 1000)
        self.plot.addAxis(self.x_axis, Qt.AlignBottom)
        self.time_series.attachAxis(self.x_axis)

        self.y_axis = QValueAxis()
        self.y_axis.setLabelFormat("%i")
        self.y_axis.setRange(0, 1000)
        self.plot.addAxis(self.y_axis, Qt.AlignLeft)
        self.time_series.attachAxis(self.y_axis)

        self.setChart(self.plot)

    def _instantiate_series(self, x_values, y_values):
        for x, y in zip(x_values, y_values):
            self.time_series.append(x, y)

    def update_series(self, x_values, y_values):
        print('update series')
        print(len(x_values))
        print(len(y_values))
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            self.time_series.replace(i, x, y)