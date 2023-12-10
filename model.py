from PySide6.QtCore import QObject, Signal, Slot
import pandas as pd
import numpy as np
import datetime

class Model(QObject):
    # Updated Signal for combined HR and IBI DataFrame
    hr_ibi_dataframe_update = Signal(object)
    hrv_metrics_dataframe_update = Signal(object)
    ecg_dataframe_update = Signal(object)
    acc_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()
        # Combined HR and IBI DataFrame
        self.hr_ibi_dataframe = pd.DataFrame()
        self.hrv_dataframe = pd.DataFrame()
        self.ecg_dataframe = pd.DataFrame()
        self.acc_dataframe = pd.DataFrame()

    @Slot(dict)
    def update_hr_ibi_dataframe(self, value):
        # Extract HR and IBI values
        hr_value = value['hr']
        ibi_value = value['ibi']
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')

        # Create a new row and add it to the existing DataFrame
        new_row = pd.DataFrame({'hr': [hr_value], 'ibi': [ibi_value]}, index=[timestamp])

        self.hr_ibi_dataframe = pd.concat([self.hr_ibi_dataframe, new_row])
        self.hr_ibi_dataframe.index = pd.DatetimeIndex(self.hr_ibi_dataframe.index)
        # Emit the updated DataFrame
        self.hr_ibi_dataframe_update.emit(self.hr_ibi_dataframe)

    def calculate_hrv_metrics(self, time_metrics_window=10):
        df = self.hr_ibi_dataframe

        time_metrics_window = time_metrics_window // 1000
        interval = f'{time_metrics_window}s'

        start_time = df.index.min().floor(interval)

        current_interval_start = start_time
        current_interval_end = current_interval_start + pd.Timedelta(seconds=time_metrics_window)

        hrv_metrics_list = []

        for timestamp, row in df.iterrows():
            if timestamp >= current_interval_end:
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

                current_interval_start = current_interval_end
                current_interval_end = current_interval_start + pd.Timedelta(seconds=time_metrics_window)

        hrv_dataframe = pd.DataFrame(hrv_metrics_list)
        try:
            hrv_dataframe.set_index('timestamp', inplace=True)
        except KeyError:
            pass

        return hrv_dataframe
