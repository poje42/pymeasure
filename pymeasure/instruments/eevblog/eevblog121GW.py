#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
import simplepyble
import time

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    truncated_range, truncated_discrete_set,
    strict_discrete_set
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def connect(address):
    # Get the first adapter available
    adapters = simplepyble.Adapter.get_adapters()
    if not adapters:
        print("No BLE adapters found.")
        return None

    adapter = adapters[0]
    # Start scanning for devices
    adapter.scan_for(5000)  # Scan for 5 seconds

    # Find the device by name
    devices = adapter.scan_get_results()
    device = None
    for dev in devices:
        # if self.MULTIMETER_ADDRESS in dev.address():
        if address or address == '':
            if EEVBlog121GW.DEVICE_NAME in dev.identifier():
                device = dev
                break
        else:
            if address in dev.address():
                device = dev
                break

    if not device:
        print(f"Device '{EEVBlog121GW.MULTIMETER_ADDRESS}' not found.")
        return None

    print(f"Connecting to {device.identifier()}...")
    try:
        device.connect()
    except Exception as e:
        print(f"Failed to connect to device: {e}")
        return None          

    if not device.is_connected():
        print(f"Failed to connect to {device.identifier()}.")
        return None

    print("Connected!")
    return device




class EEVBlog121GW(Instrument):
    """ Represents the EEVBlog 121GW Multimeter and provides a high-level
    interface for interacting with the instrument.

    .. code-block:: python

        meter = Keithley2000("GPIB::1")
        meter.measure_voltage()
        print(meter.voltage)

    """
    # Constants for the EEVBlog121GW
    DEVICE_NAME = "121GW"  # Replace with your device name
    CHARACTERISTIC_UUID = "e7add780-b042-4876-aae1-112855353cc1"
    SERVICE_UUID = "0bd51666-e7cb-469b-8e4d-2742f1ba77cc"
    MULTIMETER_ADDRESS = "88:6b:0f:8f:82:34"  # Replace with your 121GW multimeter's BLE address

    MODES = {
        'current': 'CURR:DC', 'current ac': 'CURR:AC',
        'voltage': 'VOLT:DC', 'voltage ac': 'VOLT:AC',
        'resistance': 'RES', 'resistance 4W': 'FRES',
        'period': 'PER', 'frequency': 'FREQ',
        'temperature': 'TEMP', 'diode': 'DIOD',
        'continuity': 'CONT'
    }

    MODE_RANGE_LIST = [
               ["V",   "Voltage Low Z (V)", [-1]                   ], #  0
               ["V",   "Voltage DC (V)",    [-4,-3,-2,-1]          ], #  1
               ["V",   "Voltage AC (V)",    [-4,-3,-2,-1]          ], #  2
               ["mV",  "Voltage DC (mV)",   [-6, -5]               ], #  3
               ["mV",  "Voltage AC (mV)",   [-6, -5]               ], #  4
               ["°C",  "Temp (°C)",         [-1]                   ], #  5
               ["Hz",  "Frequency (Hz)",    [-3,-2,-1,0,1]         ], #  6
               ["s",   "Period (s)",        [-4,-3,-2]             ], #  7
               ["%",   "Duty (%)",          [-1]                   ], #  8
               ["Ω",   "Resistance (Ω)",    [-3,-2,-1,0,1,2,3]     ], #  9
               ["Ω",   "Continuity (Ω)",    [-2]                   ], # 10
               ["V",   "Diode (V)",         [-4,-3]                ], # 11
               ["F",   "Capacitance (F)",   [-12,-11,-10,-9,-8,-6] ], # 12
               ["uVA", "Power AC (uVA)",    [-8,-7,-7,-6]          ], # 13
               ["mVA", "Power AC (mVA)",    [-6,-5,-5,-4]          ], # 14
               ["VA",  "Power AC (VA)",     [-4,-3,-3,-2]          ], # 15
               ["uA",  "Current AC (uA)",   [-9,-8]                ], # 16
               ["uA",  "Current DC (uA)",   [-9,-8]                ], # 17
               ["mA",  "Current AC (mA)",   [-7,-6]                ], # 18
               ["mA",  "Current DC (mA)",   [-7,-6]                ], # 19
               ["A",   "Current AC (A)",    [-5,-4,-3]             ], # 20
               ["A",   "Current DC (A)",    [-5,-4,-3]             ], # 21
               ["uVA", "Power DC (uVA)",    [-8,-7,-7,-6]          ], # 22
               ["mVA", "Power DC (mVA)",    [-6,-5,-5,-4]          ], # 23
               ["VA",  "Power DC (VA)",     [-4,-3,-3,-2]          ]  # 24 
              ]    


    # mode = Instrument.control(
    #     ":CONF?", ":CONF:%s",
    #     """ A string property that controls the configuration mode for measurements,
    #     which can take the values: ``current`` (DC), ``current ac``,
    #     ``voltage`` (DC),  ``voltage ac``, ``resistance`` (2-wire),
    #     ``resistance 4W`` (4-wire), ``period``,
    #     ``temperature``, ``diode``, and ``frequency``.""",
    #     validator=strict_discrete_set,
    #     values=MODES,
    #     map_values=True,
    #     get_process=lambda v: v.replace('"', '')
    # )

    @property
    def reading(self):
        self.is_new_value = False
        # print('Start wait')
        end = time.time() + 2
        while True:
            if self.is_new_value:
                break
            if (time.time() > end):
                print("121GW Time out")
                return 0.0
        # print('Get new value')
        return self.main_value_float

    def __new__(self, adapter, **kwargs):
        device = connect(adapter)
        if not device:
            print('Class fails')
            return None
        # If successful, create the instance
        instance = super().__new__(self)
        instance.device = device  # Store the connected device
        return instance

    def __init__(self, adapter, name="EEVBlog 121GW Multimeter", **kwargs):
        super().__init__(
            None, name, **kwargs
        )
        self.buffer = bytearray()  # Buffer to collect incoming data
        self.is_waiting_for_start = True  # Flag to look for start command (0xF2)
        self.is_new_value = False
        self.main_mode_short = ''
        self.main_mode_long = ''
        self.main_range = 0

        self.device.indicate(self.SERVICE_UUID, self.CHARACTERISTIC_UUID, self.notification_handler)

        # self.connect(adapter)

    def __del__(self):
        """Close connection upon garbage collection of the device."""
        self.close()

    def close(self):
        """Close the connection."""
        # Disconnect from the device
        if self.device and self.device.is_connected():
            self.device.unsubscribe(self.SERVICE_UUID, self.CHARACTERISTIC_UUID)
            self.device.disconnect()
            print("Disconnected.")

    def parse_121GW_data(self, data):
        # print(f"Parse data: {data.hex()}")
        # Validate checksum (XOR of bytes 0-17 should equal checksum byte)
        calculated_checksum = 0
        for i in range(18):  # XOR bytes 0-17
            calculated_checksum ^= data[i]
        
        # print(f"Calculated checksum: {calculated_checksum}")
        if calculated_checksum != data[18]:
            # print("Checksum is invalid.")
            return

        # Serial Number (Bytes 1-4)
        # serial_number = ''.join([str(data[i]) for i in range(1, 5)])
        
        # Main Mode and Range (Byte 5)
        main_mode_idx = data[5] & 0x1F  # Extract the mode (bits 4-0)
        main_range_idx = data[6] & 0x0F  # Extract the range (bits 3-0)

        self.main_mode_short = self.MODE_RANGE_LIST[main_mode_idx][0]
        self.main_mode_long = self.MODE_RANGE_LIST[main_mode_idx][1]
        self.main_range = self.MODE_RANGE_LIST[main_mode_idx][2][main_range_idx]
        
        # Main Value (Bytes 7-8) -- Main value is spread across multiple bytes
        # According to your description:
        # - Bits 17 and 16 are in byte 5 (bits 7 and 6)
        # - Main Value itself is in bytes 7-8 (big-endian 16-bit value)
        main_sign = -1 if (data[6] >> 6) & 0x01 else 1
        if (data[6] >> 7) & 0x01:  # OFL
            self.main_value_float = 9.9E37 * main_sign
        else:
            main_value = ((data[5] << 10) & 0x030000) | (data[7] << 8) | data[8]
            self.main_value_float = main_value * main_sign * 10 ** self.main_range

        # print(f'Main value {self.main_value_float}')
        # Sub Mode and Range (Byte 9 and 10)
        sub_mode = data[9]
        sub_range = data[10] & 0x07  # Extract the range (bits 2-0)
            
        # Sub Value (Bytes 11-12) - Big-endian 16-bit value
        sub_value = (data[11] << 8) | data[12]  # Big-endian: bytes 11 and 12 form the sub value
        
        # Bar Status (Byte 13)
        bar_status = data[13]
        # Bar Status (Byte 14)
        bar_value = data[14] & 0x1F

        # Icon Status (Bytes 15-17)
        icon_status_1 = data[15]
        icon_status_2 = data[16]
        icon_status_3 = data[17]

        self.is_new_value = True
        # print('New value True')    

    def notification_handler(self, data):
        """Handle notifications received from the device."""

        # print(f"Notification: {data}")
        # Add your parsing logic here
        for byte in data:
            # Check for the start command 0xF2
            if self.is_waiting_for_start:
                if byte == 0xF2:
                    # print("Start command (0xF2) detected. Beginning data collection.")
                    self.is_waiting_for_start = False  # Start buffering data after start command
                    self.buffer.append(byte)  # Add the start byte to the buffer
                continue  # Skip collecting data until we find the start command
            
            # Collect data after detecting the start command
            self.buffer.append(byte)
            
            # Once we have a full packet (19 bytes), process it
            if len(self.buffer) > 18:
                if len(self.buffer) == 19:
                    # print("\nProcessing a complete packet:")
                    self.parse_121GW_data(self.buffer)  # Parse the full 19-byte packet
                self.buffer.clear()  # Reset the buffer for the next packet
                self.is_waiting_for_start = True  # Start buffering data after start command

