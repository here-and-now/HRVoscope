from datetime import datetime
import numpy as np
import pandas as pd
from scipy import signal

from scipy.interpolate import interp1d

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
    QStylePainter
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QMargins, QSize, QDateTime
from PySide6.QtGui import QIcon, QLinearGradient, QBrush, QGradient, QColor
from PySide6.QtCharts import QChartView, QChart, QSplineSeries, QValueAxis, QAreaSeries, QLineSeries, QScatterSeries, QDateTimeAxis

from utils import BLUE, WHITE, GREEN, YELLOW, RED
from pacer import Pacer
from sensor import SensorClient
# from sensor_mock import SensorClient

class View(QMainWindow):
    def __init__(self, model):
        super().__init__()

        self.setWindowTitle("HRVoscope")

        self.model = model

        self.sensor = SensorClient()
        self.sensor.connect_client(self.sensor)

        # IBI
        self.ibi_widget = XYSeriesWidget()
        self.model.ibi_dataframe_update.connect(self.plot_ibi)
        self.sensor.ibi_update.connect(self.model.update_ibi_dataframe)

        # HR
        self.hr_widget = XYSeriesWidget()
        self.model.hr_dataframe_update.connect(self.plot_hr)
        # self.model.hr_dataframe_update.connect(self.printmock)
        self.sensor.hr_update.connect(self.model.update_hr_dataframe)


        # Layout stuff
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.ibi_widget)
        self.layout.addWidget(self.hr_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)

        self.setCentralWidget(central_widget)

    def printmock(self,df):
        print(df.index[-1])

    def plot_ibi(self, df):
        # self.ibi_widget.update_series(df['timestamp'], df['ibi'])
        df = self.downsample_dataframe(df, 100)
        index = [i for i in range(df.index.shape[0])]
        self.ibi_widget.update_series(index, df['ibi'])
    def plot_hr(self, df):
        # self.hr_widget.update_series(df['timestamp'], df['hr'])
        df = self.downsample_dataframe(df, 100)
        index = [i for i in range(df.index.shape[0])]
        self.hr_widget.update_series(index, df['hr'])

    def _downsample_dataframe(self, df, target_points):
        # looks good, but currently not resampling the datetimeindex
        if len(df) <= target_points:
            return df

        df_downsampled = pd.DataFrame()

        for column in df.columns:
            downsampled_column = signal.resample(df[column].values, target_points)
            df_downsampled[column] = downsampled_column

        resampled_index = signal.resample(df.index, target_points)
        df_downsampled.index = pd.to_datetime(resampled_index)

        return df_downsampled

    def downsample_dataframe(self, df, target_points):
        if len(df) <= target_points:
            return df

        df_downsampled = pd.DataFrame()

        for column in df.columns:
            x = df.index.values.astype(np.float64)
            f = interp1d(x, df[column], kind='cubic')
            target_index = pd.date_range(start=df.index[0], end=df.index[-1], periods=target_points)
            target_x = target_index.values.astype(np.float64)
            interpolated_values = f(target_x)
            df_downsampled[column] = interpolated_values

        df_downsampled.index = target_index

        return df_downsampled

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
        # self.time_series = QScatterSeries()
        self.plot.addSeries(self.time_series)
        pen = self.time_series.pen()
        pen.setWidth(1)
        pen.setColor(line_color)
        self.time_series.setPen(pen)

        self.x_axis = QValueAxis()
        # self.x_axis = QDateTimeAxis()
        self.x_axis.setLabelFormat("%i")
        self.x_axis.setRange(0, 100)
        self.plot.addAxis(self.x_axis, Qt.AlignBottom)
        self.time_series.attachAxis(self.x_axis)

        self.y_axis = QValueAxis()
        self.y_axis.setLabelFormat("%i")
        self.y_axis.setRange(0, 2000)
        self.plot.addAxis(self.y_axis, Qt.AlignLeft)
        self.time_series.attachAxis(self.y_axis)

        self.setChart(self.plot)


    def update_series(self, x_values, y_values):
        self.time_series.clear()
        for x, y in zip(x_values, y_values):
            # x_timestamp = x.to_pydatetime()
            # x_qdatetime = QDateTime(x_timestamp.date(), x_timestamp.time(), Qt.UTC)
            # self.time_series.append(x_qdatetime.toMSecsSinceEpoch(), y)
            self.time_series.append(x,y)
        # self.set_dynamic_range(x_values, y_values)

    def set_dynamic_range(self, x_values, y_values):
        if len(x_values) > 0:
            x_min = min(x_values)#to_pydatetime()
            x_max = max(x_values)#.to_pydatetime()

            self.x_axis.setRange(x_min, x_max)
            # self.x_axis.setFormat("yyyy-MM-dd HH:mm:ss")

        if len(y_values) > 0:
            self.y_axis.setRange(min(y_values), max(y_values))


