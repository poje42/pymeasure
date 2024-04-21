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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    truncated_range, truncated_discrete_set,
    strict_discrete_set
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Agilent34401A(Instrument):
    """ Represents the Agilent 34401A Multimeter and provides a high-level
    interface for interacting with the instrument.

    .. code-block:: python

        meter = Agilent34401A("GPIB::1")
        meter.measure_voltage()
        print(meter.voltage)

    """
    MODES = {
        'current': 'CURR', 'current ac': 'CURR:AC',
        'voltage': 'VOLT', 'voltage ac': 'VOLT:AC',
        'resistance': 'RES', 'resistance 4w': 'FRES',
        'period': 'PER', 'frequency': 'FREQ',
        'diode': 'DIOD', 'continuity': 'CONT',
        'voltage ratio': 'VOLT:RAT'
    }

    mode = Instrument.control(
        ":FUNC?", ':CONF:%s',
        """ A string property that controls the configuration mode for measurements,
        which can take the values: ``current`` (DC), ``current ac``,
        ``voltage`` (DC),  ``voltage ac``, ``resistance`` (2-wire),
        ``resistance 4w`` (4-wire), ``period``, ``diode``,
        ``continuity``, ``voltage ratio``, and ``frequency``.""",
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )

    reading = Instrument.measurement(
        ":READ?",
        """ Reads a measurement based on the active :attr:`~.Agilent34401A.mode`. """
    )

    beep_enabled = Instrument.control(
        ":SYST:BEEP:STAT?",
        ":SYST:BEEP:STAT %g",
        """ A string property that enables the system status beeper,
        which can take the values: True or False. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    beep_state = Instrument.control(
        ":SYST:BEEP:STAT?",
        ":SYST:BEEP:STAT %g",
        """ A string property that enables or disables the system status beeper,
        which can take the values: ``enabled`` and ``disabled``. """,
        validator=strict_discrete_set,
        values={'enabled': 1, 'disabled': 0},
        map_values=True
    )

    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC current measurement in Amps, based on the
        active :attr:`~.Agilent34401A.mode`. """
    )
    current_range = Instrument.control(
        ":SENS:CURR:DC:RANG?", ":SENS:CURR:DC:RANG:AUTO 0;:SENS:CURR:DC:RANG %g",
        """ A floating point property that controls the DC current range in
        Amps, which can take values from 0.01 to 3.0 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 3.0]
    )
    current_nplc = Instrument.control(
        ":SENS:CURR:DC:NPLC?", ":SENS:CURR:DC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1,
        10 and 100 are defined levels. """
    )
    current_resolution = Instrument.control(
        ":SENS:CURR:DC:RES?", ":SENS:CURR:DC:RES %g",
        """ A floating property that controls the resolution in Amps. """,
        validator=truncated_range,
        values=[0, 3.0]
    )
    current_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the DC current reference
        value in Amps, which can take values from -3.6 to 3.6 A. """,
        validator=truncated_range,
        values=[-3.6, 3.6]
    )
    current_ac_range = Instrument.control(
        ":SENS:CURR:AC:RANG?", ":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG %g",
        """ A floating point property that controls the AC current range in
        Amps, which can take values from 0 to 3.0 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 3.0]
    )
    current_ac_resolution = Instrument.control(
        ":SENS:CURR:AC:RES?", ":SENS:CURR:AC:RES %g",
        """ A floating property that controls the resolution in Amps. """,
        validator=truncated_range,
        values=[0, 3.0]
    )
    current_ac_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the AC current reference
        value in Amps, which can take values from -3.6A to 3.6 A. """,
        validator=truncated_range,
        values=[-3.6, 3.6]
    )
    current_ac_bandwidth = Instrument.control(
        ":SENS:DET:BAND?", ":SENS:DET:BAND %g",
        """ A floating point property that sets the AC current detector
        to the lowest frequency in Hz, which can take the values 3, 20, and 200 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 20, 200]
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC voltage measurement in Volts, based on the
        active :attr:`~.Agilent34401A.mode`. """
    )
    voltage_range = Instrument.control(
        ":SENS:VOLT:DC:RANG?", ":SENS:VOLT:DC:RANG:AUTO 0;:SENS:VOLT:DC:RANG %g",
        """ A floating point property that controls the DC voltage range in
        Volts, which can take values from 0 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1000]
    )
    voltage_nplc = Instrument.control(
        ":SENS:VOLT:DC:NPLC?", ":SENS:VOLT:DC:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1,
        10 and 100 are defined levels. """
    )
    voltage_resolution = Instrument.control(
        ":SENS:VOLT:DC:RES?", ":SENS:VOLT:DC:RES %g",
        """ A floating property that controls the resolution in Volts. """,
        validator=truncated_range,
        values=[0, 1000.0]
    )
    voltage_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the DC current reference
        value in Volts, which can take values from -1200 to 1200 V. """,
        validator=truncated_range,
        values=[-1200.0, 1200.0]
    )
    voltage_high_input_impedance = Instrument.control(
        "INP:IMP:AUTO?", "INP:IMP:AUTO %s",
        """Control if high input resistance mode is enabled.

        Only valid for dc voltage measurements.
        When disabled (default), the input resistance is fixed
        at 10 MOhms for all ranges. If enabled, the input resistance is set to
        >10 GOhms for the 100 mV, 1 V, and 10 V ranges.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )
    voltage_ac_range = Instrument.control(
        ":SENS:VOLT:AC:RANG?", ":SENS:VOLT:AC:RANG:AUTO 0;:SENS:VOLT:AC:RANG %g",
        """ A floating point property that controls the AC voltage range in
        Volts, which can take values from 0 to 750 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1000]
    )
    voltage_ac_resolution = Instrument.control(
        ":SENS:VOLT:AC:RES?", ":SENS:VOLT:AC:RES %g",
        """ A floating property that controls the resolution in Volts. """,
        validator=truncated_range,
        values=[0, 750.0]
    )
    voltage_ac_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the AC current reference
        value in Volts, which can take values from -1200 to 1200 V. """,
        validator=truncated_range,
        values=[-1200.0, 1200.0]
    )
    voltage_ac_bandwidth = Instrument.control(
        ":SENS:DET:BAND?", ":SENS:DET:BAND %g",
        """ A floating point property that sets the AC current detector
        to the lowest frequency in Hz, which can take the values 3, 20, and 200 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 20, 200]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Reads a resistance measurement in Ohms for both 2-wire and 4-wire
        configurations, based on the active :attr:`~.Agilent34401A.mode`. """
    )
    resistance_range = Instrument.control(
        ":SENS:RES:RANG?", ":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG %g",
        """ A floating point property that controls the 2-wire resistance range
        in Ohms, which can take values from 0 to 100 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_nplc = Instrument.control(
        ":SENS:RES:NPLC?", ":SENS:RES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1,
        10 and 100 are defined levels. """
    )
    resistance_resolution = Instrument.control(
        ":SENS:RES:RES?", ":SENS:RES:RES %g",
        """ A floating property that controls the resolution in Ohms. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the 2-wire resistance
        reference value in Ohms, which can take values from -120 to 120 MOhms. """,
        validator=truncated_range,
        values=[-120e6, 120e6]
    )
    resistance_4w_range = Instrument.control(
        ":SENS:FRES:RANG?", ":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG %g",
        """ A floating point property that controls the 4-wire resistance range
        in Ohms, which can take values from 0 to 100 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_4w_nplc = Instrument.control(
        ":SENS:FRES:NPLC?", ":SENS:FRES:NPLC %g",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 4-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1,
        10 and 100 are defined levels. """
    )
    resistance_4w_resolution = Instrument.control(
        ":SENS:FRES:RES?", ":SENS:FRES:RES %g",
        """ A floating property that controls the resolution in Ohms. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_4w_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the 4-wire resistance
        reference value in Ohms, which can take values from -120 to 120 MOhms. """,
        validator=truncated_range,
        values=[-120e6, 120e6]
    )

    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(
        ":READ?",
        """ Reads a frequency measurement in Hz, based on the
        active :attr:`~.Agilent34401A.mode`. """
    )
    frequency_range = Instrument.control(
        ":SENS:FREQ:VOLT:RANG?", ":SENS:FREQ:VOLT:RANG:AUTO 0;:SENS:FREQ:VOLT:RANG %g",
        """ A floating point property that controls the voltage range in
        Volts, which can take values from 0 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1000]
    )
    frequency_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the frequency reference
        value in Hz, which can take values from -1.2 to 1.2 MHz. """,
        validator=truncated_range,
        values=[-1.2e6, 1.2e6]
    )
    frequency_aperature = Instrument.control(
        ":SENS:FREQ:APER?", ":SENS:FREQ:APER %g",
        """ A floating point property that controls the frequency aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )

    ##############
    # Period (s) #
    ##############

    period = Instrument.measurement(
        ":READ?",
        """ Reads a period measurement in seconds, based on the
        active :attr:`~.Agilent34401A.mode`. """
    )
    period_range = Instrument.control(
        ":SENS:PER:VOLT:RANG?", ":SENS:PER:VOLT:RANG:AUTO 0;:SENS:PER:VOLT:RANG %g",
        """ A floating point property that controls the voltage range in
        Volts, which can take values from 0 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1000]
    )
    period_reference = Instrument.control(
        ":CALC:NULL:OFFS?", ":CALC:FUNC NULL;:CALC:STAT ON;:CALC:NULL:OFFS %g",
        """ A floating point property that controls the period reference value
        in seconds, which can take values from -1.2 to 1.2 s. """,
        validator=truncated_range,
        values=[-1.2, 1.2]
    )
    period_aperature = Instrument.control(
        ":SENS:PER:APER?", ":SENS:PER:APER %g",
        """ A floating point property that controls the period aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )

    ####################
    # Continuity (Ohm) #
    ####################

    continuity = Instrument.measurement(
        ":READ?",
        """ Reads the continuity in Ohm, based on the
        active :attr:`~.Agilent34401A.mode`. """
    )
    # continuity_threshold = Instrument.control(
    #     ":SENS:FREQ:THR:VOLT:RANG?", ":SENS:FREQ:THR:VOLT:RANG %g",
    #     """ A floating point property that controls the voltage signal threshold
    #     level in Volts for the continuity measurement, which can take values
    #     from 1 to 1000 Ohms. """,
    #     validator=truncated_range,
    #     values=[1, 1000]
    # )

    #############
    # Diode (V) #
    #############

    diode = Instrument.measurement(
        ":READ?",
        """ Reads the diode in volts, based on the
        active :attr:`~.Agilent34401A.mode`. """
    )

    ###########
    # Trigger #
    ###########

    trigger_count = Instrument.control(
        ":TRIG:COUN?", ":TRIG:COUN %d",
        """ An integer property that controls the trigger count,
        which can take values from 1 to 50,000. """,
        validator=truncated_range,
        values=[1, 50000]
    )
    trigger_delay = Instrument.control(
        ":TRIG:DEL?", ":TRIG:DEL %g",
        """ A floating point property that controls the trigger delay
        in seconds, which can take values from 0 to 3,600 s. """,
        validator=truncated_range,
        values=[0, 3600.0]
    )

    def __init__(self, adapter, name="Agilent 34401A Multimeter", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    def measure_voltage(self, max_voltage=1, ac=False):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if ac:
            self.mode = 'voltage ac'
            self.voltage_ac_range = max_voltage
        else:
            self.mode = 'voltage'
            self.voltage_range = max_voltage

    def measure_current(self, max_current=10e-3, ac=False):
        """ Configures the instrument to measure current,
        based on a maximum current to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_current: A current in Volts to set the current range
        :param ac: False for DC current, and True for AC current
        """
        if ac:
            self.mode = 'current ac'
            self.current_ac_range = max_current
        else:
            self.mode = 'current'
            self.current_range = max_current

    def measure_resistance(self, max_resistance=10e6, wires=2):
        """ Configures the instrument to measure voltage,
        based on a maximum voltage to set the range, and
        a boolean flag to determine if DC or AC is required.

        :param max_voltage: A voltage in Volts to set the voltage range
        :param ac: False for DC voltage, and True for AC voltage
        """
        if wires == 2:
            self.mode = 'resistance'
            self.resistance_range = max_resistance
        elif wires == 4:
            self.mode = 'resistance 4w'
            self.resistance_4w_range = max_resistance
        else:
            raise ValueError("Agilent 34401A only supports 2 or 4 wire"
                             "resistance meaurements.")

    def measure_period(self):
        """ Configures the instrument to measure the period. """
        self.mode = 'period'

    def measure_frequency(self):
        """ Configures the instrument to measure the frequency. """
        self.mode = 'frequency'

    def measure_diode(self):
        """ Configures the instrument to perform diode testing.  """
        self.mode = 'diode'

    def measure_continuity(self):
        """ Configures the instrument to perform continuity testing. """
        self.mode = 'continuity'

    def _mode_command(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    def auto_range(self, mode=None):
        """ Sets the active mode to use auto-range,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Agilent34401A.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:RANG:AUTO 1" % self._mode_command(mode))

    def enable_reference(self):
        """ Enables the reference for the active mode.
        """
        self.write(":CALC:STAT 1;:CALC:FUNC NULL")

    def disable_reference(self):
        """ Disables the reference for the active mode.
        """
        self.write(":CALC:STAT 0")

    # def enable_filter(self, mode=None, type='repeat', count=1):
    #     """ Enables the averaging filter for the active mode,
    #     or can set another mode by its name.

    #     :param mode: A valid :attr:`~.Agilent34401A.mode` name, or None for the active mode
    #     :param type: The type of averaging filter, either 'repeat' or 'moving'.
    #     :param count: A number of averages, which can take take values from 1 to 100
    #     """
    #     self.write(":SENS:%s:AVER:STAT 1")
    #     self.write(":SENS:%s:AVER:TCON %s")
    #     self.write(":SENS:%s:AVER:COUN %d")

    # def disable_filter(self, mode=None):
    #     """ Disables the averaging filter for the active mode,
    #     or can set another mode by its name.

    #     :param mode: A valid :attr:`~.Agilent34401A.mode` name, or None for the active mode
    #     """
    #     self.write(":SENS:%s:AVER:STAT 0" % self._mode_command(mode))

    def local(self):
        """ Returns control to the instrument panel, and enables
        the panel if disabled. Only for RS-232. """
        self.write(":SYST:LOC")

    def remote(self):
        """ Places the instrument in the remote state, which is
        does not need to be explicity called in general. Only for RS-232. """
        self.write(":SYST:REM")

    def remote_lock(self):
        """ Disables and locks the front panel controls to prevent
        changes during remote operations. This is disabled by
        calling :meth:`~.Agilent34401A.local`. Only for RS-232. """
        self.write(":SYST:RWL")

    def reset(self):
        """ Resets the instrument state. """
        self.write("*RST;:STAT:PRES;:*CLS;")

    def beep(self):
        """ Sounds a system beep.
        """
        self.write(":SYST:BEEP")
