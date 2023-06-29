from PySide6.QtCore import QObject, Signal, Slot
from collections import namedtuple
import numpy as np
import pandas as pd
from datetime import datetime
class Model(QObject):

    ibi_dataframe_update = Signal(object)
    hr_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()
        self.ibi_dataframe = pd.DataFrame()
        self.hr_dataframe = pd.DataFrame()



    @Slot(dict)
    def update_ibi_dataframe(self, value):
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'ibi': [value['ibi']]}, index=[timestamp])
        self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row])
        self.ibi_dataframe.index = pd.DatetimeIndex(self.ibi_dataframe.index)
        self.ibi_dataframe_update.emit(self.ibi_dataframe)

        self.calculate_hrv_metrics()

    @Slot(dict)
    def update_hr_dataframe(self, value):
        timestamp = pd.to_datetime(value['timestamp'], unit='ms')
        new_row = pd.DataFrame({'hr': [value['hr']]}, index=[timestamp])
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row])
        self.hr_dataframe.index = pd.DatetimeIndex(self.hr_dataframe.index)
        self.hr_dataframe_update.emit(self.hr_dataframe)


    def calculate_hrv_metrics(self):
        # Perform HRV calculations on the IBI DataFrame
        # Calculate metrics such as SDNN, RMSSD, etc.
        # Example code:
        hrv_metrics = {}
        ibi_values = self.ibi_dataframe['ibi'].values
        # Perform your HRV calculations here using ibi_values
        sdnn = np.std(ibi_values)
        rmssd = np.sqrt(np.mean(np.square(np.diff(ibi_values))))
        # Add more HRV metrics calculations as needed

        # Update the hrv_metrics dictionary
        hrv_metrics['SDNN'] = sdnn
        hrv_metrics['RMSSD'] = rmssd
        # Add more HRV metrics to the hrv_metrics dictionary



        self.hrv_metrics_update.emit(hrv_metrics)