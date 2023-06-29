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

        self.mac_address = 'D1:EC:51:A8:A2:6A'

        self.client = None
        self.sensor = None

        self.hr_service = None
        self.hr_notification = None
        self.ecg_service = None
        self.ecg_control_notification = None
        self.acc_service = None
        self.acc_notification = None

        self.ecg_stream_values = []
        self.ecg_stream_times = []


        self.ENABLE_NOTIFICATION = QByteArray.fromHex(b"0100")
        self.DISABLE_NOTIFICATION = QByteArray.fromHex(b"0000")

        self.ECG_WRITE = QByteArray(bytes(bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])))
        self.ACC_WRITE = QByteArray(
            bytes(bytearray([0x02, 0x02, 0x00, 0x01, 0xC8, 0x00, 0x01, 0x01, 0x10, 0x00, 0x02, 0x01, 0x08, 0x00])))

        self.HR_CHARACTERISTIC = QBluetoothUuid.CharacteristicType.HeartRateMeasurement
        self.HR_SERVICE = QBluetoothUuid.ServiceClassUuid.HeartRate

        self.PMD_SERVICE = QBluetoothUuid(
            "fb005c80-02e7-f387-1cad-8acd2d8df0c8")  ## UUID for connection establishment with device ##
        self.PMD_CONTROL = QBluetoothUuid("fb005c81-02e7-f387-1cad-8acd2d8df0c8")  ## UUID for Request of stream settings ##
        self.PMD_DATA = QBluetoothUuid("fb005c82-02e7-f387-1cad-8acd2d8df0c8")  ## UUID for Request of start stream ##


        self.ACC_SAMPLING_FREQ = 200
        self.ECG_SAMPLING_FREQ = 130

    def _connect_ecg_service(self):
        ecg_service = [s for s in self.client.services() if s == self.PMD_SERVICE]

        if not ecg_service:
            print(f"Couldn't find ECG service on {self.mac_address}.")
            return

        self.ecg_service = self.client.createServiceObject(*ecg_service)

        if not self.ecg_service:
            print(f"Couldn't establish connection to ECG service on {self.mac_address}.")
            return

        self.ecg_service.stateChanged.connect(self._start_ecg_notification)
        self.ecg_service.characteristicChanged.connect(self._ecg_data_handler)
        self.ecg_service.discoverDetails()

    def _start_ecg_notification(self, state):
        if state != QLowEnergyService.ServiceDiscovered:
            return
        ecg_char_control = self.ecg_service.characteristic(self.PMD_CONTROL)
        ecg_char_data = self.ecg_service.characteristic(self.PMD_DATA)

        if not ecg_char_control.isValid():
            print(f"Couldn't find ECG control characteristic on {self.mac_address}.")
            return

        if not ecg_char_data.isValid():
            print(f"Couldn't find ECG data characteristic on {self.mac_address}.")
            return

        self.ecg_control_notification = ecg_char_control.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )

        self.ecg_data_notification = ecg_char_data.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )

        if not self.ecg_control_notification.isValid():
            print("ECG characteristic is invalid.")
            return

        self.ecg_service.writeCharacteristic(ecg_char_control, self.ECG_WRITE, QLowEnergyService.WriteWithResponse)
        self.ecg_service.writeDescriptor(self.ecg_data_notification, self.ENABLE_NOTIFICATION)


    def _connect_hr_service(self):
        hr_service = [s for s in self.client.services() if s == self.HR_SERVICE]
        if not hr_service:
            print(f"Couldn't find HR service on {self.mac_address}.")
            return
        self.hr_service = self.client.createServiceObject(*hr_service)
        if not self.hr_service:
            print(
                f"Couldn't establish connection to HR service on {self.mac_address}."
            )
            return
        self.hr_service.stateChanged.connect(self._start_hr_notification)
        self.hr_service.characteristicChanged.connect(self._hr_data_handler)
        self.hr_service.discoverDetails()
    def _start_hr_notification(self, state):
        if state != QLowEnergyService.ServiceDiscovered:
            return
        hr_char = self.hr_service.characteristic(self.HR_CHARACTERISTIC)
        if not hr_char.isValid():
            print(f"Couldn't find HR characteristic on {self.mac_address}.")
            return
        self.hr_notification = hr_char.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        if not self.hr_notification.isValid():
            print("HR characteristic is invalid.")
            return
        self.hr_service.writeDescriptor(self.hr_notification, self.ENABLE_NOTIFICATION)
    def _reset_connection(self):
        print(f"Discarding sensor at {self.mac_address}")
        self._remove_service()
        self._remove_client()
    def _remove_service(self):
        try:
            self.hr_service.deleteLater()
        except Exception as e:
            print(f"Couldn't remove HR service: {e}")
        try:
            self.ecg_service.deleteLater()
        except Exception as e:
            print(f"Couldn't remove ECG service: {e}")
        try:
            self.acc_service.deleteLater()
        except Exception as e:
            print(f"Couldn't remove ACC service: {e}")
        finally:
            self.hr_service = None
            self.hr_notification = None
            self.ecg_service = None
            self.ecg_control_notification = None
            self.acc_service = None
            self.acc_notification = None
    def _remove_client(self):
        try:
            self.client.disconnected.disconnect()
            self.client.deleteLater()
        except Exception as e:
            print(f"Couldn't remove client: {e}")
        finally:
            self.client = None
    def _catch_error(self, error):
        self.status_update.emit(f"An error occurred: {error}. Disconnecting sensor.")
        print(f"An error occurred: {error}. Disconnecting sensor.")  # Print the status update message to the console
        self._reset_connection()
    def _hr_data_handler(self, _, data):  # _ is an unused but mandatory argument
        """
        `data` is formatted according to the
        "GATT Characteristic and Object Type 0x2A37 Heart Rate Measurement"
        which is one of the three characteristics included in the
        "GATT Service 0x180D Heart Rate".

        `data` can include the following bytes:
        - flags
            Always present.
            - bit 0: HR format (uint8 vs. uint16)
            - bit 1, 2: sensor contact status
            - bit 3: energy expenditure status
            - bit 4: RR interval status
        - HR
            Encoded by one or two bytes depending on flags/bit0. One byte is
            always present (uint8). Two bytes (uint16) are necessary to
            represent HR > 255.
        - energy expenditure
            Encoded by 2 bytes. Only present if flags/bit3.
        - inter-beat-intervals (IBIs)
            One IBI is encoded by 2 consecutive bytes. Up to 18 bytes depending
            on presence of uint16 HR format and energy expenditure.
        """
        data = data.data()  # convert from QByteArray to Python bytes


        byte0 = data[0]
        uint8_format = (byte0 & 1) == 0
        energy_expenditure = ((byte0 >> 3) & 1) == 1
        rr_interval = ((byte0 >> 4) & 1) == 1

        if not rr_interval:
            return

        first_rr_byte = 2
        if uint8_format:
            hr = data[1]
            pass
        else:
            hr = (data[2] << 8) | data[1]
            first_rr_byte += 1

        if energy_expenditure:
            ee = (data[first_rr_byte + 1] << 8) | data[first_rr_byte]
            first_rr_byte += 2

        for i in range(first_rr_byte, len(data), 2):
            ibi = (data[i + 1] << 8) | data[i]
            # Polar H7, H9, and H10 record IBIs in 1/1024 seconds format.
            # Convert 1/1024 sec format to milliseconds.
            # TODO: move conversion to model and only convert if sensor doesn't
            # transmit data in milliseconds.
            ibi = math.ceil(ibi / 1024 * 1000)

            timestamp = time.time_ns()/1.0e6

            self.ibi_update.emit({'timestamp': timestamp, 'ibi': ibi})
            self.hr_update.emit({'timestamp': timestamp, 'hr': hr})

            # print('HR: ', hr, 'ibi: ', ibi)

    def __ecg_data_handler(self, _, data):
        # [00 EA 1C AC CC 99 43 52 08 00 68 00 00 58 00 00 46 00 00 3D 00 00 32 00 00 26 00 00 16 00 00 04 00 00 ...]
        # 00 = ECG; EA 1C AC CC 99 43 52 08 = last sample timestamp in nanoseconds; 00 = ECG frameType, sample0 = [68 00 00] microVolts(104) , sample1, sample2, ....
        print('ECG start')
        print(data)
        if data[0] == 0x00:
            print('Its 0x00')
            timestamp = convert_to_unsigned_long(data, 1, 8) / 1.0e9
            step = 3
            time_step = 1.0 / self.ECG_SAMPLING_FREQ
            samples = data[10:]
            n_samples = math.floor(len(samples) / step)
            offset = 0
            sample_timestamp = timestamp - (n_samples - 1) * time_step
            while offset < len(samples):
                ecg = convert_array_to_signed_int(samples, offset, step)
                offset += step
                self.ecg_stream_values.extend([ecg])
                self.ecg_stream_times.extend([sample_timestamp])
                sample_timestamp += time_step

            print(self.ecg_stream_values)
    def _ecg_data_handler(self, _, data):
        """
        The ECG data handler receives ECG data from the sensor. Each data packet contains
        a sequence number and a raw ECG data frame. The frame is a 13-byte array that
        represents the ECG data of 3 ECG channels (x, y, and z) at a specific timestamp.

        The ECG data handler extracts the raw ECG data and emits it as a signal.

        Args:
            data (QByteArray): The raw ECG data packet.
        """
        sequence_number = int.from_bytes(data[:4], byteorder='little')
        raw_ecg_data = data[4:]
        ecg_values = []

        for i in range(0, len(raw_ecg_data), 2):
            ecg_value = convert_array_to_signed_int(raw_ecg_data, i, 2)
            ecg_values.append(ecg_value)

        self.ecg_update.emit(ecg_values)

    def connect_client(self, sensor):
        if self.client:
            msg = (
                f"Currently connected to sensor at {self.mac_address}."
                " Please disconnect before (re-)connecting to (another) sensor."
            )
            self.status_update.emit(msg)
            print(msg)  # Print the status update message to the console
            return
        self.status_update.emit(
            f"Connecting to sensor at {self.mac_address}."
        )
        print(f"Connecting to sensor at {self.mac_address}.")  # Print the status update message to the console

        self.sensor = QBluetoothDeviceInfo(QBluetoothAddress(self.mac_address), 'Polar H10', 0)
        self.client = QLowEnergyController.createCentral(self.sensor)
        self.client.errorOccurred.connect(self._catch_error)
        self.client.connected.connect(self._discover_services)

        self.client.discoveryFinished.connect(self._connect_hr_service)
        self.client.discoveryFinished.connect(self._connect_ecg_service)

        self.client.disconnected.connect(self._reset_connection)
        self.client.connectToDevice()

    def disconnect_client(self):
        if self.hr_notification and self.hr_service:
            if not self.hr_notification.isValid():
                return
            print("Unsubscribing from HR service.")
            self.hr_service.writeDescriptor(
                self.hr_notification, self.DISABLE_NOTIFICATION
            )
        if self.ecg_control_notification and self.ecg_service:
            if not self.ecg_control_notification.isValid():
                return
            print("Unsubscribing from ECG service.")
            self.ecg_service.writeDescriptor(
                self.ecg_control_notification, self.DISABLE_NOTIFICATION
            )
        if self.acc_notification and self.acc_service:
            if not self.acc_notification.isValid():
                return
            print("Unsubscribing from ACC service.")
            self.acc_service.writeDescriptor(
                self.acc_notification, self.DISABLE_NOTIFICATION
            )
        if self.client:
            self.status_update.emit(
                f"Disconnecting from sensor at {self.mac_address}."
            )
            print(f"Disconnecting from sensor at {self.mac_address}.")  # Print the status update message to the console
            self.client.disconnectFromDevice()

    def _discover_services(self):
        self.client.discoverServices()

