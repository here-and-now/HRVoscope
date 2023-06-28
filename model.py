from PySide6.QtCore import QObject, Signal, Slot
from collections import namedtuple
import numpy as np
import pandas as pd

class Model(QObject):

    ibi_dataframe_update = Signal(object)
    hr_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()
        self.ibi_dataframe = pd.DataFrame()
        self.hr_dataframe = pd.DataFrame()

    @Slot(object)
    def update_ibi_dataframe(self, value):
        new_row = pd.DataFrame({'ibi': [value]})
        self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row], ignore_index=True)
        self.ibi_dataframe_update.emit(self.ibi_dataframe)

    @Slot(object)
    def update_hr_dataframe(self, value):
        new_row = pd.DataFrame({'hr': [value]})
        self.hr_dataframe = pd.concat([self.hr_dataframe, new_row], ignore_index=True)
        self.hr_dataframe_update.emit(self.hr_dataframe)
