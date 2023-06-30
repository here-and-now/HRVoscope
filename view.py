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
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QMargins, QSize, QDateTime, QPointF
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

        self.HRV_RMSSD_RANGE = [0, 200]
        self.HRV_SDNN_RANGE = [0, 2000]
        self.HRV_pNN20_RANGE = [0, 100]
        self.HRV_pNN50_RANGE = [0, 100]

        # # IBI
        # self.ibi_widget = XYSeriesWidget()
        # self.model.ibi_dataframe_update.connect(self.plot_ibi)
        self.sensor.ibi_update.connect(self.model.update_ibi_dataframe)
        #
        # # HR
        # self.hr_widget = XYSeriesWidget()
        # self.model.hr_dataframe_update.connect(self.plot_hr)
        # # self.model.hr_dataframe_update.connect(self.printmock)
        self.sensor.hr_update.connect(self.model.update_hr_dataframe)


        # HRV

        self.hrv_widget = XYSeriesWidget()
        self.model.hrv_metrics_dataframe_update.connect(self.plot_hrv)



        # Layout stuff
        self.layout = QHBoxLayout()
        # self.layout.addWidget(self.ibi_widget)
        # self.layout.addWidget(self.hr_widget)
        self.layout.addWidget(self.hrv_widget)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)

        self.setCentralWidget(central_widget)

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

    def plot_hrv(self, df):
        if not bool(self.hrv_widget.series_dict):
            # x_values = []
            # y_values = []
            self.hrv_widget.add_series("SDNN", x_range=[0, 100], y_range=self.HRV_SDNN_RANGE, line_color=RED, pen_width=2)
        else:
            index = [i for i in range(df.index.shape[0])]
            self.hrv_widget.update_series('SDNN', index, df['SDNN'].values )

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
    def __init__(self):
        super().__init__()

        self.plot = QChart()
        self.plot.legend().setVisible(True)
        self.plot.setBackgroundRoundness(0)
        self.plot.setMargins(QMargins(0, 0, 0, 0))

        self.series_dict = {}
        self.axes = []

        self.setChart(self.plot)

    def add_series(self, series_name, x_values=None, y_values=None, x_range=[0, 200], y_range=[0, 200], line_color=BLUE,
                   pen_width=1):
        series = QSplineSeries()
        pen = series.pen()
        pen.setWidth(pen_width)
        pen.setColor(line_color)
        series.setPen(pen)

        axis_x = QValueAxis()
        axis_x.setLabelFormat("%i")
        axis_x.setRange(x_range[0], x_range[1])

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%i")
        axis_y.setRange(y_range[0], y_range[1])

        self.plot.addSeries(series)
        self.plot.addAxis(axis_x, Qt.AlignBottom)
        self.plot.addAxis(axis_y, Qt.AlignLeft)

        series.attachAxis(axis_x)
        series.attachAxis(axis_y)

        self.series_dict[series_name] = series
        self.axes.append((axis_x, axis_y))

    def update_series(self, series_name, x_values, y_values):
        series = self.series_dict.get(series_name)
        if series is not None:
            data = [QPointF(x, y) for x, y in zip(x_values, y_values)]
            series.replace(data)
    def set_dynamic_range(self, series_name, x_values, y_values):
        axis_x, axis_y = self._get_axes_by_name(series_name)
        if axis_x and axis_y:
            if len(x_values) > 0:
                x_min = min(x_values)
                x_max = max(x_values)
                axis_x.setRange(x_min, x_max)

            if len(y_values) > 0:
                y_min = min(y_values)
                y_max = max(y_values)
                axis_y.setRange(y_min, y_max)

    def _get_axes_by_name(self, series_name):
        series_index = self._get_series_index_by_name(series_name)
        if series_index is not None and series_index < len(self.axes):
            return self.axes[series_index]
        return None, None

    def _get_series_index_by_name(self, series_name):
        series = self.series_dict.get(series_name)
        if series is not None:
            return list(self.series_dict.values()).index(series)
        return None


