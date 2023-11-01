from PySide6.QtCore import QObject, Signal, Slot
from collections import namedtuple
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import datetime
from utils import transform_polar_timestamp_to_unix_timestamp
class Model(QObject):

    ibi_dataframe_update = Signal(object)
    hr_dataframe_update = Signal(object)
    hrv_metrics_dataframe_update = Signal(object)
    ecg_dataframe_update = Signal(object)
    acc_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()
        self.ibi_dataframe = pd.DataFrame()
        self.hr_dataframe = pd.DataFrame()
        self.hrv_dataframe = pd.DataFrame()
        self.ecg_dataframe = pd.DataFrame()
        self.acc_dataframe = pd.DataFrame()

    @Slot(dict)
    def update_ibi_dataframe(self, value):
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'ibi': [value['ibi']]}, index=[timestamp])
        self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row])
        self.ibi_dataframe.index = pd.DatetimeIndex(self.ibi_dataframe.index)
        self.ibi_dataframe_update.emit(self.ibi_dataframe)
        # self.calculate_hrv_metrics()

    @Slot(dict)
    def update_hr_dataframe(self, value):

        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'hr': [value['hr']]}, index=[timestamp])
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row])
        self.hr_dataframe.index = pd.DatetimeIndex(self.hr_dataframe.index)
        self.hr_dataframe_update.emit(self.hr_dataframe)

    @Slot(dict)
    def _update_ecg_dataframe(self, value):
        # sensor timestamp is in nanoseconds from polar epoch
        timestamp_ns = value['timestamp']

        # Offset between Unix epoch and Polar epoch in nanoseconds
        nanosecond_offset = 946684800000000000 # aka 2000-01-01 00:00:00 UTC

        # Convert to unix timestamp in milliseconds
        timestamp_ms = (timestamp_ns + nanosecond_offset) / 1000000
        # Convert to datetime
        timestamp_datetime = pd.to_datetime(timestamp_ms, unit='ms')

        print(timestamp_datetime)
        new_row = pd.DataFrame({'ecg': [value['ecg']]}, index=[timestamp_datetime])
        self.ecg_dataframe = pd.concat([self.ecg_dataframe, new_row])
        self.ecg_dataframe.index = pd.DatetimeIndex(self.ecg_dataframe.index)
        self.ecg_dataframe_update.emit(self.ecg_dataframe)
        # print(self.ecg_dataframe)

    @Slot(dict)
    def _update_ecg_dataframe(self, value):
        # Sensor timestamp is in nanoseconds since epoch 2000-01-01T00:00:00Z
        timestamp_ns = value['timestamp']
        nanosecond_offset = 946684800000000000 # aka 2000-01-01 00:00:00 UTC
        # Convert to datetime using the correct epoch
        timestamp_datetime = timestamp_ns + nanosecond_offset

        # calculate offset beetween timestamp and current time
        current_time = int(datetime.datetime.now().timestamp() * 1000000000)

        offset = current_time - timestamp_ns

        print(f'offset: {offset}')

        new_row = pd.DataFrame({'ecg': [value['ecg']]}, index=[timestamp_datetime])
        self.ecg_dataframe = pd.concat([self.ecg_dataframe, new_row])
        self.ecg_dataframe.index = pd.DatetimeIndex(self.ecg_dataframe.index)
        self.ecg_dataframe_update.emit(self.ecg_dataframe)

    @Slot(dict)
    def update_ecg_dataframe(self, value):
        # Sensor timestamp is in nanoseconds since epoch 2000-01-01T00:00:00Z
        timestamp_ns = value['timestamp']
        # calculate offset beetween timestamp and current time
        current_time = int(datetime.datetime.now().timestamp() * 1000000000)
        # print(datetime.datetime.now().timestamp())
        offset = current_time - timestamp_ns
        new_row = pd.DataFrame({'offset': [offset]}, index=[timestamp_ns])
        self.ecg_dataframe = pd.concat([self.ecg_dataframe, new_row])
        self.ecg_dataframe.index = pd.DatetimeIndex(self.ecg_dataframe.index)
        self.ecg_dataframe_update.emit(self.ecg_dataframe)
        # print(self.ecg_dataframe)

        if len(self.ecg_dataframe) == 1000:
            # self.ecg_dataframe['offset'].plot.kde()
            # self.ecg_dataframe['offset'].plot.hist()
            # print statistical data
            print(f'mean: {self.ecg_dataframe["offset"].mean()}')
            print(f'median: {self.ecg_dataframe["offset"].median()}')
            print(f'std: {self.ecg_dataframe["offset"].std()}')
            print(f'min: {self.ecg_dataframe["offset"].min()}')
            print(f'max: {self.ecg_dataframe["offset"].max()}')

            # more analysis
            print(f'kurtosis: {self.ecg_dataframe["offset"].kurtosis()}')
            print(f'skewness: {self.ecg_dataframe["offset"].skew()}')
            print(f'variance: {self.ecg_dataframe["offset"].var()}')

            # plot offset over steps
            self.ecg_dataframe['offset'].plot()
            # print(f'covariance: {self.ecg_dataframe["offset"].cov()}')
            # print(f'quantile: {self.ecg_dataframe["offset"].quantile()}')

            plt.show()

    @Slot(dict)
    def update_acc_dataframe(self, value):
        # fix timestamp stuff
        timestamp = pd.to_datetime(value['timestamp'], unit='ns')
        new_row = pd.DataFrame({'x': [value['x']], 'y': [value['y']], 'z': [value['z']], 'mag': [value['mag']]},
                               index=[timestamp])
        self.acc_dataframe = pd.concat([self.acc_dataframe, new_row])
        self.acc_dataframe.index = pd.DatetimeIndex(self.acc_dataframe.index)
        self.acc_dataframe_update.emit(self.acc_dataframe)

    def calculate_hrv_metrics(self, time_metrics_window=10):
        df = self.ibi_dataframe

        time_metrics_window = time_metrics_window // 1000
        interval = f'{time_metrics_window}s'

        start_time = df.index.min().floor(interval)

        # Initialize variables to track the current interval
        current_interval_start = start_time
        current_interval_end = current_interval_start + pd.Timedelta(seconds=time_metrics_window)

        # Create an empty list to store the calculated HRV metrics
        hrv_metrics_list = []

        # Group by custom time periods and calculate HRV metrics for each group
        for timestamp, ibi_value in df['ibi'].items():
            if timestamp >= current_interval_end:
                # Calculate HRV metrics for the completed interval
                group_df = df.loc[current_interval_start:current_interval_end]

                if len(group_df) > 1:
                    sdnn = np.std(group_df['ibi'].values)
                    rmssd = np.sqrt(np.mean(np.square(np.diff(group_df['ibi'].values))))
                    pnn50 = float(np.sum(np.abs(np.diff(group_df['ibi'].values)) > 50) / len(group_df['ibi'].values) * 100)
                    pnn20 = float(np.sum(np.abs(np.diff(group_df['ibi'].values)) > 20) / len(group_df['ibi'].values) * 100)
                else:
                    sdnn = np.nan
                    rmssd = np.nan
                    pnn50 = np.nan
                    pnn20 = np.nan

                hrv_metrics = {'SDNN': sdnn, 'RMSSD': rmssd, 'pNN50': pnn50, 'pNN20': pnn20,
                               'timestamp': current_interval_end}
                hrv_metrics_list.append(hrv_metrics)

                # Update the current interval
                current_interval_start = current_interval_end
                current_interval_end = current_interval_start + pd.Timedelta(seconds=time_metrics_window)

        # Create a DataFrame from the list of HRV metrics
        hrv_dataframe = pd.DataFrame(hrv_metrics_list)
        try:
            hrv_dataframe.set_index('timestamp', inplace=True)
        except KeyError:
            pass

        return hrv_dataframe




