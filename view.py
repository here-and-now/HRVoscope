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
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter

from utils import BLUE, WHITE, GREEN, YELLOW, RED
from pacer import Pacer
from sensor import SensorClient
# from sensor_mock import SensorClient
from ui import Ui_MainWindow

class View(QMainWindow, Ui_MainWindow):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("HRVoscope")

        self.model = model

        self.sensor = SensorClient()
        self.sensor.connect_client(self.sensor)

        self.HRV_RMSSD_RANGE = [0, 200]
        self.HRV_SDNN_RANGE = [0, 200]
        self.HRV_pNN20_RANGE = [0, 100]
        self.HRV_pNN50_RANGE = [0, 100]

        self.HRV_METRICS_X_RANGE = [0, 200]


        # Connect Model Signals to Widget Slots
        self.model.ibi_dataframe_update.connect(self.plot_ibi)
        self.model.hr_dataframe_update.connect(self.plot_hr)
        self.model.hrv_metrics_dataframe_update.connect(self.plot_hrv)
        # self.model.ecg_dataframe_update.connect(self.plot_ecg)
        # self.model.acc_dataframe_update.connect(self.plot_acc)

        # Connect Sensor Signals to Model Slots
        self.sensor.ibi_update.connect(self.model.update_ibi_dataframe)
        self.sensor.hr_update.connect(self.model.update_hr_dataframe)
        self.sensor.ecg_update.connect(self.model.update_ecg_dataframe)
        self.sensor.acc_update.connect(self.model.update_acc_dataframe)


    def plot_ibi(self, df):
        if not bool(self.hrv_ibi_chart.series_dict):
            self.hrv_ibi_chart.add_series("IBI", x_range=[0, 100], y_range=[0, 2000], line_color=BLUE, pen_width=2)
        else:
            df = self.downsample_dataframe(df, 100)
            self.hrv_ibi_chart.update_series('IBI', df.index, df['ibi'])

    def plot_hr(self, df):
        if not bool(self.hr_chart.series_dict):
            self.hr_chart.add_series("HR", x_range=[0, 200], y_range=[0, 200], line_color=BLUE, pen_width=2)
        else:
            df = self.downsample_dataframe(df, 200)
            self.hr_chart.update_series('HR', df.index, df['hr'])

    def plot_hrv(self, df):
        if not bool(self.hrv_metrics_chart.series_dict):
            self.hrv_metrics_chart.add_series("SDNN", x_range=self.HRV_METRICS_X_RANGE, y_range=self.HRV_SDNN_RANGE, line_color=RED, pen_width=2)
            self.hrv_metrics_chart.add_series("RMSSD", x_range=self.HRV_METRICS_X_RANGE, y_range=self.HRV_RMSSD_RANGE, line_color=BLUE, pen_width=2)
        else:

            df = df.dropna()
            df = self.downsample_dataframe(df, self.HRV_METRICS_X_RANGE[1])
            self.hrv_metrics_chart.update_series('SDNN', df.index, df['SDNN'].values)
            self.hrv_metrics_chart.update_series('RMSSD', df.index, df['RMSSD'].values)

    def plot_ecg(self, df):
        if not bool(self.ecg_chart.series_dict):
            self.ecg_chart.add_series("ECG", x_range=[0, 1000], y_range=[-1500, 1500], line_color=BLUE, pen_width=2)
        else:
            # reduce to last 1000 points
            df = df.iloc[-1000:]
            # df = self.downsample_dataframe(df, 1000)
            self.ecg_chart.update_series('ECG', df.index, df['ecg'].values)
    def plot_acc(self, df):
        if not bool(self.acc_chart.series_dict):
            self.acc_chart.add_series("ACC", x_range=[0, 1000], y_range=[-1500, 1500], line_color=BLUE, pen_width=2)
        else:
            # reduce to last 1000 points
            df = df.iloc[-1000:]
            df = self.downsample_dataframe(df, 1000)
            self.acc_chart.update_series('ACC', df.index, df['mag'].values)

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



