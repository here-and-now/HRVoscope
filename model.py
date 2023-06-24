from PySide6.QtCore import QObject, Signal, Slot

class Model(QObject):

    def __init__(self):
        super().__init__()
        self._x_values = None
        self._y_values = None
