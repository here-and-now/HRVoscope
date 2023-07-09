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

    def _ecg_data_handler(self, _, data):
        # [00 EA 1C AC CC 99 43 52 08 00 68 00 00 58 00 00 46 00 00 3D 00 00 32 00 00 26 00 00 16 00 00 04 00 00 ...]
        # 00 = ECG; EA 1C AC CC 99 43 52 08 = last sample timestamp in nanoseconds; 00 = ECG frameType, sample0 = [68 00 00] microVolts(104) , sample1, sample2, ....

        if data[0] == b'\x00':
            timestamp = convert_to_unsigned_long(data, 1, 8)
            step = 3
            time_step = int(1.0 / self.ECG_SAMPLING_FREQ * 1e9)
            samples = data[10:]
            n_samples = math.floor(len(samples) / step)
            offset = 0
            sample_timestamp = timestamp - (n_samples - 1) * time_step
            while offset < len(samples):
                # print(f"ECG timestamp: {timestamp}"
                #       f"ECG time step: {time_step}"
                #       f"ECG sample timestamp: {sample_timestamp}"
                #       f"ECG sample: {samples[offset:offset + step]}"
                #       f"ECG sample value: {convert_array_to_signed_int(samples, offset, step)}")
                ecg = convert_array_to_signed_int(samples, offset, step)
                offset += step
                self.ecg_update.emit({'timestamp': sample_timestamp, 'ecg': ecg})
                sample_timestamp += time_step
    def _connect_acc_service(self):
        acc_service = [s for s in self.client.services() if s == self.PMD_SERVICE]
        if not acc_service:
            print(f"Couldn't find ACC service on {self.mac_address}.")
            return
        self.acc_service = self.client.createServiceObject(*acc_service)
        if not self.acc_service:
            print(
                f"Couldn't establish connection to ACC service on {self.mac_address}."
            )
            return
        self.acc_service.stateChanged.connect(self._start_acc_notification)
        self.acc_service.characteristicChanged.connect(self._acc_data_handler)
        self.acc_service.discoverDetails()

    def _start_acc_notification(self, state):
        if state != QLowEnergyService.ServiceDiscovered:
            return
        acc_char_control = self.acc_service.characteristic(self.PMD_CONTROL)
        acc_char_data = self.acc_service.characteristic(self.PMD_DATA)
        if not acc_char_control.isValid():
            print(f"Couldn't find ACC control characteristic on {self.mac_address}.")
            return
        if not acc_char_data.isValid():
            print(f"Couldn't find ACC data characteristic on {self.mac_address}.")
            return
        self.acc_control_notification = acc_char_control.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        self.acc_data_notification = acc_char_data.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        if not self.acc_control_notification.isValid():
            print("ACC control characteristic is invalid.")
            return
        self.acc_service.writeCharacteristic(acc_char_control, self.ACC_WRITE, QLowEnergyService.WriteWithResponse)
        self.acc_service.writeDescriptor(self.acc_data_notification, self.ENABLE_NOTIFICATION)

    def _connect_acc_service(self):
        acc_service = [s for s in self.client.services() if s == self.PMD_SERVICE]
        if not acc_service:
            print(f"Couldn't find ACC service on {self.mac_address}.")
            return
        self.acc_service = self.client.createServiceObject(*acc_service)
        if not self.acc_service:
            print(
                f"Couldn't establish connection to ACC service on {self.mac_address}."
            )
            return
        self.acc_service.stateChanged.connect(self._start_acc_notification)
        self.acc_service.characteristicChanged.connect(self._acc_data_handler)
        self.acc_service.discoverDetails()

    def _start_acc_notification(self, state):
        if state != QLowEnergyService.ServiceDiscovered:
            return
        acc_char_control = self.acc_service.characteristic(self.PMD_CONTROL)
        acc_char_data = self.acc_service.characteristic(self.PMD_DATA)
        if not acc_char_control.isValid():
            print(f"Couldn't find ACC control characteristic on {self.mac_address}.")
            return
        if not acc_char_data.isValid():
            print(f"Couldn't find ACC data characteristic on {self.mac_address}.")
            return
        self.acc_control_notification = acc_char_control.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        self.acc_data_notification = acc_char_data.descriptor(
            QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration
        )
        if not self.acc_control_notification.isValid():
            print("ACC control characteristic is invalid.")
            return
        self.acc_service.writeCharacteristic(acc_char_control, self.ACC_WRITE, QLowEnergyService.WriteWithResponse)
        self.acc_service.writeDescriptor(self.acc_data_notification, self.ENABLE_NOTIFICATION)

    def _acc_data_handler(self, sender, data):
        # [02 EA 54 A2 42 8B 45 52 08 01 45 FF E4 FF B5 03 45 FF E4 FF B8 03 ...]
        # 02=ACC,
        # EA 54 A2 42 8B 45 52 08 = last sample timestamp in nanoseconds,
        # 01 = ACC frameType,
        # sample0 = [45 FF E4 FF B5 03] x-axis(45 FF=-184 millig) y-axis(E4 FF=-28 millig) z-axis(B5 03=949 millig) ,
        # sample1, sample2,
        if data[0] == b'\x02':
            timestamp = convert_to_unsigned_long(data, 1, 8) / 1.0e9  # timestamp of the last sample
            frame_type = int.from_bytes(data[9], byteorder='big')
            resolution = (frame_type + 1) * 8  # 16 bit
            time_step = 0.005  # 200 Hz sample rate
            step = math.ceil(resolution / 8.0)
            samples = data[10:]
            n_samples = math.floor(len(samples) / (step * 3))
            sample_timestamp = timestamp - (n_samples - 1) * time_step
            offset = 0
            while offset < len(samples):
                x = convert_array_to_signed_int(samples, offset, step)
                offset += step
                y = convert_array_to_signed_int(samples, offset, step)
                offset += step
                z = convert_array_to_signed_int(samples, offset, step)
                offset += step
                mag = np.linalg.norm([x, y, z])

                self.acc_update.emit({'timestamp': sample_timestamp, 'x': x, 'y': y, 'z': z, 'mag': mag})
                sample_timestamp += time_step

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
        self.client.discoveryFinished.connect(self._connect_acc_service)

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

