import numpy as np
import PySide6.QtWidgets as QtWidgets
import numpy as np
import pandas as pd
import pyqtgraph as pg
from scipy.interpolate import interp1d

from sensor import SensorClient
# from sensor_mock import SensorClient
from ui import Ui_MainWindow
from utils import BLUE, RED, get_ms_from_button_text


class View(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("HRVoscope")

        self.model = model
        self.sensor = SensorClient()
        self.sensor.connect_client(self.sensor)

        # Manage and connect dataframe updates
        self.sensor.hr_update.connect(self.model.update_hr_dataframe)
        self.sensor.ibi_update.connect(self.model.update_ibi_dataframe)
        self.sensor.ecg_update.connect(self.model.update_ecg_dataframe)
        # self.sensor.acc_update.connect(self.model.update_acc_dataframe)

        # HR
        self.model.hr_dataframe_update.connect(self.plot_hr)
        # IBI
        self.model.ibi_dataframe_update.connect(self.plot_ibi)
        # HRV
        self.model.ibi_dataframe_update.connect(self.plot_hrv_metrics)
        # ECG
        self.model.ecg_dataframe_update.connect(self.plot_ecg)
        # # ACC
        # self.model.acc_dataframe_update.connect(self.plot_acc)

        self.actionReset_data.triggered.connect(self.reset_data)
        self.actionPause_plot.triggered.connect(self.pause_plotting)
        self.actionResume_plot.triggered.connect(self.resume_plotting)

        self.plot_paused = False

    def plot_ibi(self, df):
        if self.plot_paused:
            return

        # df = self.downsample_dataframe(df, 100)
        tw = self.time_window_for_plot()
        x = df.index.values
        y = df['ibi'].values
        self.hrv_ibi_chart.plot(x, y, name='IBI', time_window=tw, pen=pg.mkPen(color=BLUE, width=2))

    def plot_hr(self, df):
        if self.plot_paused:
            return

        # df = self.downsample_dataframe(df, 200)
        tw = self.time_window_for_plot()
        x = df.index.values
        y = df['hr'].values
        self.hr_chart.plot(x, y, name='HR', time_window=tw, pen=pg.mkPen(color=BLUE, width=2))

    def plot_hrv_metrics(self, df):
        if self.plot_paused:
            return

        time_metrics_window = get_ms_from_button_text(self.hrv_metrics_time_button_group.checkedButton())
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
        return get_ms_from_button_text(self.plot_time_window_button_group.checkedButton())

    def plot_ecg(self, df):
        if self.plot_paused:
            return

        x = df.index.values
        y = df['ecg'].values
        self.ecg_chart.plot(x, y, pen=pg.mkPen(color=BLUE, width=2))

    def plot_acc(self, df):
        if self.plot_paused:
            return

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

    def reset_data(self):
        self.model.hr_dataframe = pd.DataFrame()
        self.model.ibi_dataframe = pd.DataFrame()
        self.model.hrv_dataframe = pd.DataFrame()
        self.model.ecg_dataframe = pd.DataFrame()
        self.model.acc_dataframe = pd.DataFrame()

        self.hr_chart.clear()
        self.hrv_ibi_chart.clear()
        self.ecg_chart.clear()
        self.acc_chart.clear()
        self.hrv_metrics_by_time_chart.clear()

    def pause_plotting(self):
        self.plot_paused = True

    def resume_plotting(self):
        self.plot_paused = False
