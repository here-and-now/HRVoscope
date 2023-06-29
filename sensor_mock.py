import random
import time

from PySide6.QtBluetooth import (
    QBluetoothDeviceDiscoveryAgent,
    QLowEnergyController,
    QLowEnergyService,
    QBluetoothUuid,
    QBluetoothDeviceInfo,
    QBluetoothAddress
)
from PySide6.QtCore import QObject, Signal, QByteArray, Qt, QCoreApplication

import math
import sys
import threading

from utils import convert_array_to_signed_int, convert_to_unsigned_long
import numpy as np
import pandas as pd
class SensorClient(QObject):
    """
    Connect to a Polar sensor that acts as a Bluetooth server / peripheral.
    On Windows, the sensor must already be paired with the machine running
    OpenHRV. Pairing isn't implemented in Qt6.

    In Qt terminology client=central, server=peripheral.
    """

    ibi_update = Signal(object)
    hr_update = Signal(object)
    ecg_update = Signal(object)
    acc_update = Signal(object)
    status_update = Signal(str)


    def __init__(self):
        super().__init__()

        self.client = None
        self.sensor = None


    def connect_client(self, sensor):
        thread = threading.Thread(target=self.mock)
        thread.start()

    def mock(self):
        while True:
            hr = random.uniform(0,100)
            ibi = random.uniform(0,100)

            timestamp = time.time_ns()/1.0e9

            self.ibi_update.emit({'timestamp': timestamp, 'ibi': ibi})
            self.hr_update.emit({'timestamp': timestamp, 'hr': hr})

            time.sleep(0.1)

