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
        # Define a sensible cutoff value for IBI
        # IBI values are usually in the range of 600 to 1000 ms for adults at rest.
        # However, it can vary widely based on activities and health conditions.
        # You may adjust this based on your specific needs and domain knowledge.
        ibi_cutoff_low = 300  # in milliseconds
        ibi_cutoff_high = 2000  # in milliseconds

        ibi_value = value['ibi']

        if ibi_cutoff_low <= ibi_value <= ibi_cutoff_high:
            timestamp = pd.to_datetime(value['timestamp'], unit='ms')
            new_row = pd.DataFrame({'ibi': [ibi_value]}, index=[timestamp])
            self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row])
            self.ibi_dataframe.index = pd.DatetimeIndex(self.ibi_dataframe.index)
            self.ibi_dataframe_update.emit(self.ibi_dataframe)
        else:
            print(f"Discarded improbable IBI value: {ibi_value} ms")

    @Slot(dict)
    def update_hr_dataframe(self, value):

        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'hr': [value['hr']]}, index=[timestamp])
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row])
        self.hr_dataframe.index = pd.DatetimeIndex(self.hr_dataframe.index)
        self.hr_dataframe_update.emit(self.hr_dataframe)


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




