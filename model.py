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
        timestamp = datetime.fromtimestamp(value['timestamp'])
        new_row = pd.DataFrame({'ibi': [value['ibi']], 'timestamp': [timestamp]})
        self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row], ignore_index=True)
        self.ibi_dataframe_update.emit(self.ibi_dataframe)

    @Slot(dict)
    def update_hr_dataframe(self, value):
        timestamp = datetime.fromtimestamp(value['timestamp'])
        new_row = pd.DataFrame({'hr': [value['hr']], 'timestamp': [timestamp]})
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row], ignore_index=True)
        self.hr_dataframe_update.emit(self.hr_dataframe)