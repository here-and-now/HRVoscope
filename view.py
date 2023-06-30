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
        self.HRV_SDNN_RANGE = [0, 200]
        self.HRV_pNN20_RANGE = [0, 100]
        self.HRV_pNN50_RANGE = [0, 100]

        self.HRV_METRICS_X_RANGE = [0, 200]

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

        # ECG
        self.ecg_widget = XYSeriesWidget()
        self.model.ecg_dataframe_update.connect(self.plot_ecg)
        self.sensor.ecg_update.connect(self.model.update_ecg_dataframe)
        # ACC
        self.acc_widget = XYSeriesWidget()
        self.model.acc_dataframe_update.connect(self.plot_acc)
        self.sensor.acc_update.connect(self.model.update_acc_dataframe)


        # Layout stuff
        self.layout = QHBoxLayout()
        # self.layout.addWidget(self.ibi_widget)
        # self.layout.addWidget(self.hr_widget)
        # self.layout.addWidget(self.hrv_widget)
        self.layout.addWidget(self.ecg_widget)
        self.layout.addWidget(self.acc_widget)

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
        df = self.downsample_dataframe(df, 200)
        index = [i for i in range(df.index.shape[0])]
        self.hr_widget.update_series(index, df['hr'])

    def plot_hrv(self, df):
        if not bool(self.hrv_widget.series_dict):
            self.hrv_widget.add_series("SDNN", x_range=self.HRV_METRICS_X_RANGE, y_range=self.HRV_SDNN_RANGE, line_color=RED, pen_width=2)
            self.hrv_widget.add_series("RMSSD", x_range=self.HRV_METRICS_X_RANGE, y_range=self.HRV_RMSSD_RANGE, line_color=BLUE, pen_width=2)
        else:
            index = [i for i in range(df.index.shape[0])]

            df = df.dropna()
            df = self.downsample_dataframe(df, self.HRV_METRICS_X_RANGE[1])
            self.hrv_widget.update_series('SDNN', index, df['SDNN'].values)
            self.hrv_widget.update_series('RMSSD', index, df['RMSSD'].values)

    def plot_ecg(self, df):
        if not bool(self.ecg_widget.series_dict):
            self.ecg_widget.add_series("ECG", x_range=[0, 1000], y_range=[-1500, 1500], line_color=BLUE, pen_width=2)
        else:
            # reduce to last 1000 points
            df = df.iloc[-1000:]
            index = [i for i in range(df.index.shape[0])]
            # df = self.downsample_dataframe(df, 1000)
            self.ecg_widget.update_series('ECG', index, df['ecg'].values)
    def plot_acc(self, df):
        if not bool(self.acc_widget.series_dict):
            self.acc_widget.add_series("ACC", x_range=[0, 1000], y_range=[-1500, 1500], line_color=BLUE, pen_width=2)
        else:
            # reduce to last 1000 points
            df = df.iloc[-1000:]
            index = [i for i in range(df.index.shape[0])]
            # df = self.downsample_dataframe(df, 1000)
            self.acc_widget.update_series('ACC', index, df['mag'].values)
    def downsample_dataframe(self, df, target_points):
        if len(df) <= target_points:
            return df

        df_downsampled = pd.DataFrame()

        for column in df.columns:
            x = df.index.values.astype(np.float64)
            f = interp1d(x, df[column], kind='linear')
            target_index = pd.date_range(start=df.index[0], end=df.index[-1], periods=target_points)
            target_x = target_index.values.astype(np.float64)
            interpolated_values = f(target_x)
            df_downsampled[column] = interpolated_values

        df_downsampled.index = target_index

        return df_downsampled

class XYSeriesWidget(QChartView):
    def __init__(self):
        super().__init__()

        self.plot = QChart()
        self.plot.legend().setVisible(True)
        self.plot.setBackgroundRoundness(0)
        self.plot.setMargins(QMargins(0, 0, 0, 0))

        self.series_dict = {}
        self.axes = []
        self.main_axis = None

        self.setChart(self.plot)

    def add_series(self, series_name, x_values=None, y_values=None, x_range=[0, 200], y_range=[0, 200], line_color=BLUE,
                   pen_width=1):
        series = QSplineSeries()
        pen = series.pen()
        pen.setWidth(pen_width)
        pen.setColor(line_color)
        series.setPen(pen)

        if self.main_axis is None:
            axis_x = QValueAxis()
            axis_x.setLabelFormat("%i")
            axis_x.setRange(x_range[0], x_range[1])
            self.main_axis = axis_x
        else:
            axis_x = self.main_axis

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


