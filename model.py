from PySide6.QtCore import QObject, Signal, Slot
from collections import namedtuple
import numpy as np

NamedSignal = namedtuple("NamedSignal", "name value")
class Model(QObject):
    ecg_buffer_update = Signal(NamedSignal)
    ibi_buffer_update = Signal(NamedSignal)
    def __init__(self):
        super().__init__()

        self.ecg_buffer = np.full(1000, 1000, dtype=int)

        self.ibi_buffer = np.full(1000, 1000, dtype=int)

        # self._x_values = None
        # self._y_values = None


    @Slot(object)
    def update_ibi_buffer(self, value):
        self.ibi_buffer = np.roll(self.ibi_buffer, -1)
        self.ibi_buffer[-1] = value
        # print('Ibi buffer', self.ibi_buffer)
        array = np.linspace(0, len(self.ibi_buffer) - 1, len(self.ibi_buffer))
        self.ibi_buffer_update.emit(NamedSignal('InterBeatInterval', (array,self.ibi_buffer)))



