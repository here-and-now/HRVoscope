from PySide6.QtCore import QObject, Signal, Slot
from collections import namedtuple
import numpy as np
import pandas as pd
NamedSignal = namedtuple("NamedSignal", "name value")

class Model(QObject):
    ecg_buffer_update = Signal(NamedSignal)
    ibi_buffer_update = Signal(NamedSignal)

    ibi_dataframe_update = Signal(object)

    def __init__(self):
        super().__init__()

        # self.ecg_buffer = np.full(1000, np.nan, dtype=int)
        # self.ibi_buffer = np.full(1000, np.nan, dtype=int)

        self.ibi_dataframe = pd.DataFrame()


    #
    # @Slot(object)
    # def update_ibi_buffer(self, value):
    #     self.ibi_buffer = np.roll(self.ibi_buffer, -1)
    #     self.ibi_buffer[-1] = value
    #     array = np.linspace(0, len(self.ibi_buffer) - 1, len(self.ibi_buffer))
    #     self.ibi_buffer_update.emit(NamedSignal('InterBeatInterval', (array, self.ibi_buffer)))


    @Slot(object)
    def update_ibi_dataframe(self, value):
        new_row = pd.DataFrame({'ibi': [value]})
        self.ibi_dataframe = pd.concat([self.ibi_dataframe, new_row], ignore_index=True)
        self.ibi_dataframe_update.emit(self.ibi_dataframe)
