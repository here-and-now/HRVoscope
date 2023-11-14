# ~/gits/HRVoscope/model.py
from PySide6.QtCore import QObject, Signal, Slot
import pandas as pd
import numpy as np
import datetime
from utils import transform_polar_timestamp_to_unix_timestamp

class Model(QObject):
    # Signal declarations
    ibi_dataframe_update = Signal(object)
    hr_dataframe_update = Signal(object)
    hrv_metrics_dataframe_update = Signal(object)
    ecg_dataframe_update = Signal(object)
    acc_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()
        # Initialize dataframes
        self.initialize_dataframes()

    def initialize_dataframes(self):
        """
        Initialize all the pandas dataframes required for storing sensor data.
        """
        self.ibi_dataframe = pd.DataFrame()
        self.hr_dataframe = pd.DataFrame()
        self.hrv_dataframe = pd.DataFrame()
        self.ecg_dataframe = pd.DataFrame()
        self.acc_dataframe = pd.DataFrame()

    @Slot(dict)
    def update_ibi_dataframe(self, value):
        """
        Update the Inter-Beat Interval (IBI) dataframe with new data.
        Discard values that are outside a plausible range for IBI.
        """
        ibi_cutoff_low = 200  # Lower limit for IBI in milliseconds
        ibi_cutoff_high = 2000  # Upper limit for IBI in milliseconds

        ibi_value = value['ibi']
        if ibi_cutoff_low <= ibi_value <= ibi_cutoff_high:
            timestamp = pd.to_datetime(value['timestamp'], unit='ms')
            new_row = pd.DataFrame({'ibi': [ibi_value]}, index=[timestamp])
            self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row])
            self.ibi_dataframe.index = pd.DatetimeIndex(self.ibi_dataframe.index)
            self.ibi_dataframe_update.emit(self.ibi_dataframe)
        else:
            print(f"Discarded improbable IBI value: {ibi_value} ms")

        # every 100 ibi values print statistics
        if len(self.ibi_dataframe) % 5 == 0:
            print(f"IBI statistics: {self.ibi_dataframe.describe()}")
            print(f"IBI dataframe length: {len(self.ibi_dataframe)}")



    @Slot(dict)
    def update_hr_dataframe(self, value):
        """
        Update the Heart Rate (HR) dataframe with new data.
        """
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'hr': [value['hr']]}, index=[timestamp])
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row])
        self.hr_dataframe.index = pd.DatetimeIndex(self.hr_dataframe.index)
        self.hr_dataframe_update.emit(self.hr_dataframe)

    def calculate_hrv_metrics(self, time_metrics_window=10):
        """
        Calculate HRV (Heart Rate Variability) metrics for the stored IBI (Inter-Beat Interval) data.
        The metrics are calculated for rolling windows of the specified duration.

        :param time_metrics_window: Duration of the rolling window in seconds
        :return: DataFrame containing calculated HRV metrics for each window
        """
        df = self.ibi_dataframe
        time_metrics_window = time_metrics_window // 1000
        interval = f'{time_metrics_window}s'

        start_time = df.index.min().floor(interval)
        current_interval_end = start_time + pd.Timedelta(seconds=time_metrics_window)

        hrv_metrics_list = []

        for timestamp, row in df.iterrows():
            while timestamp >= current_interval_end:
                group_df = df.loc[current_interval_end - pd.Timedelta(seconds=time_metrics_window):current_interval_end]
                ibi_values = group_df['ibi'].values
                hrv_metrics = self.calculate_hrv_metrics_for_interval(ibi_values)
                hrv_metrics['timestamp'] = current_interval_end
                hrv_metrics_list.append(hrv_metrics)
                current_interval_end += pd.Timedelta(seconds=time_metrics_window)

        hrv_dataframe = pd.DataFrame(hrv_metrics_list)
        hrv_dataframe.set_index('timestamp', inplace=True, drop=True)
        return hrv_dataframe

    @staticmethod
    def calculate_hrv_metrics_for_interval(ibi_values):
        """
        Calculate various HRV (Heart Rate Variability) metrics for a given interval of IBI (Inter-Beat Interval) data.

        :param ibi_values: List or array of IBI values for the interval
        :return: Dictionary containing calculated HRV metrics
        """
        if len(ibi_values) > 1:
            sdnn = np.std(ibi_values)
            rmssd = np.sqrt(np.mean(np.square(np.diff(ibi_values))))
            pnn50 = float(np.sum(np.abs(np.diff(ibi_values)) > 50) / len(ibi_values) * 100)
            pnn20 = float(np.sum(np.abs(np.diff(ibi_values)) > 20) / len(ibi_values) * 100)
        else:
            sdnn, rmssd, pnn50, pnn20 = np.nan, np.nan, np.nan, np.nan

        return {'SDNN': sdnn, 'RMSSD': rmssd, 'pNN50': pnn50, 'pNN20': pnn20}
