from datetime import datetime
import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import interp1d
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import PySide6.QtWidgets as QtWidgets
import pyqtgraph as pg

from utils import BLUE, WHITE, GREEN, YELLOW, RED, get_seconds_from_button_text
from pacer import Pacer
from sensor import SensorClient
# from sensor_mock import SensorClient
from ui import Ui_MainWindow


class View(QtWidgets.QMainWindow, Ui_MainWindow):
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
        self.model.ibi_dataframe_update.connect(self.plot_hrv_metrics)

        self.model.hr_dataframe_update.connect(self.plot_hr)
        # self.model.hrv_metrics_dataframe_update.connect(self.plot_hrv_metrics)



        self.model.ecg_dataframe_update.connect(self.plot_ecg)
        # self.model.acc_dataframe_update.connect(self.plot_acc)

        # Connect Sensor Signals to Model Slots
        self.sensor.ibi_update.connect(self.model.update_ibi_dataframe)
        self.sensor.hr_update.connect(self.model.update_hr_dataframe)


        # self.sensor.ecg_update.connect(self.model.update_ecg_dataframe)
        # self.sensor.acc_update.connect(self.model.update_acc_dataframe)

    def plot_ibi(self, df):
        # df = self.downsample_dataframe(df, 100)
        tw = self.time_window_for_plot()
        x = df.index.values
        y = df['ibi'].values
        self.hrv_ibi_chart.plot(x, y, name='IBI', time_window=tw, pen=pg.mkPen(color=BLUE, width=2))

    def plot_hr(self, df):
        # df = self.downsample_dataframe(df, 200)
        tw = self.time_window_for_plot()
        x = df.index.values
        y = df['hr'].values
        self.hr_chart.plot(x, y, name='HR', time_window=tw, pen=pg.mkPen(color=BLUE, width=2))

    def plot_hrv(self, df):
        if 'SDNN' in df and 'RMSSD' in df:
            df = df.dropna()
            x = df.index.values
            y_sdnn = df['SDNN'].values
            y_rmssd = df['RMSSD'].values
            self.hrv_metrics_chart.plot(x, y_sdnn, name='SDNN', pen=pg.mkPen(color=RED, width=2))
            self.hrv_metrics_chart.plot(x, y_rmssd, name='RMSSD', pen=pg.mkPen(color=BLUE, width=2))

    def plot_hrv_metrics(self, df):
        time_metrics_window = get_seconds_from_button_text(self.hrv_metrics_time_button_group.checkedButton())

        df = self.model.calculate_hrv_metrics(time_metrics_window=time_metrics_window)

        tw = self.time_window_for_plot()

        if 'SDNN' in df and 'RMSSD' in df:
            df = df.dropna()
            x = df.index.values
            y_sdnn = df['SDNN'].values
            y_rmssd = df['RMSSD'].values
            self.hrv_metrics_by_time_chart.plot(x, y_sdnn, name='SDNN', time_window=tw, pen=pg.mkPen(color=RED, width=2))
            self.hrv_metrics_by_time_chart.plot(x, y_rmssd, name='RMSSD', time_window=tw, pen=pg.mkPen(color=BLUE, width=2))

    def time_window_for_plot(self):
        return get_seconds_from_button_text(self.plot_time_window_button_group.checkedButton())

    def plot_ecg(self, df):
        df = df.iloc[-1000:]
        x = df.index
        y = df['ecg'].values
        self.ecg_chart.plot(x, y, pen=pg.mkPen(color=BLUE, width=2))

    def plot_acc(self, df):
        df = df.iloc[-1000:]
        df = self.downsample_dataframe(df, 1000)
        x = df.index.values
        y = df['mag'].values
        self.acc_chart.plot(x, y, pen=pg.mkPen(color=BLUE, width=2))

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
