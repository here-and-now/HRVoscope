from PySide6.QtCore import QObject, Signal, Slot
from collections import namedtuple
import numpy as np
import pandas as pd
from datetime import datetime
class Model(QObject):

    ibi_dataframe_update = Signal(object)
    hr_dataframe_update = Signal(object)
    hrv_metrics_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()
        self.ibi_dataframe = pd.DataFrame()
        self.hr_dataframe = pd.DataFrame()
        self.hrv_dataframe = pd.DataFrame()


    @Slot(dict)
    def update_ibi_dataframe(self, value):
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'ibi': [value['ibi']]}, index=[timestamp])
        self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row])
        self.ibi_dataframe.index = pd.DatetimeIndex(self.ibi_dataframe.index)
        self.ibi_dataframe_update.emit(self.ibi_dataframe)
        print('Calc HRVoscope')
        self.calculate_hrv_metrics()

    @Slot(dict)
    def update_hr_dataframe(self, value):
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'hr': [value['hr']]}, index=[timestamp])
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row])
        self.hr_dataframe.index = pd.DatetimeIndex(self.hr_dataframe.index)
        self.hr_dataframe_update.emit(self.hr_dataframe)

    def calculate_hrv_metrics(self):
        ibi_values = self.ibi_dataframe['ibi'].values
        ibi_timestamps = self.ibi_dataframe.index

        sdnn = np.std(ibi_values)
        rmssd = np.sqrt(np.mean(np.square(np.diff(ibi_values))))
        pnn50 = float(np.sum(np.abs(np.diff(ibi_values)) > 50) / len(ibi_values) * 100)
        pnn20 = float(np.sum(np.abs(np.diff(ibi_values)) > 20) / len(ibi_values) * 100)

        hrv_metrics = pd.DataFrame(
            {'SDNN': [sdnn], 'RMSSD': [rmssd], 'pNN50': [pnn50], 'pNN20': [pnn20], 'IBI': [ibi_values[-1]]},
            index=[ibi_timestamps[-1]]  # Set the index as the timestamp from the latest IBI value
        )

        self.hrv_dataframe = pd.concat([self.hrv_dataframe, hrv_metrics])  # Concatenate with the existing HRV dataframe

        print(self.hrv_dataframe)

        self.hrv_metrics_dataframe_update.emit(self.hrv_dataframe)
