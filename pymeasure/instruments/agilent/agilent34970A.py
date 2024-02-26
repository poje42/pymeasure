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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import (
    truncated_range, truncated_discrete_set,
    strict_discrete_set
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class BaseChannel(Channel):

    def insert_id(self, command):
        """Insert the channel id in a command replacing `placeholder`.

        Subclass this method if you want to do something else,
        like always prepending the channel id.
        """
        print(command.format_map({self.placeholder: self.id}))
        if "READ?" in command:
            ch = self.parent.working_ch
            if ch != self.id:
                self.parent.write(f'ROUT:SCAN (@{self.id})')
                self.parent.working_ch = self.id

        return command.format_map({self.placeholder: self.id})

    reading = Instrument.measurement(
        ":READ?",
        """ Reads a measurement based on the active :attr:`~.Agilent34970A.mode`. """
    )
    reference = Instrument.control(
        ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
        """ A floating point property that controls the reference
        value, which can take values from -1E15 to 1E15. """,
        validator=truncated_range,
        values=[-1E15, 1E15],
        set_process=lambda v: -v,  # 34970 has no ref functions, use offset with changed sign
        get_process=lambda v: -v
    )
    gain = Instrument.control(
        ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
        """ A floating point property that controls the gain of the
        value, which can take values from -1E15 to 1E15. """,
        validator=truncated_range,
        values=[-1E15, 1E15]
    )
    unit = Instrument.control(
        ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
        """ A string property that controls a custom label of 3 characters. """
    )

    # def __init__(self, adapter, name="Agilent 34970A Multimeter", **kwargs):
    #     super().__init__(
    #         adapter, name, **kwargs
    #     )

    def _mode_command(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.MODES[mode]

    def auto_range(self, mode=None):
        """ Sets the active mode to use auto-range,
        or can set another mode by its name.

        :param mode: A valid :attr:`~.Agilent34970A.mode` name, or None for the active mode
        """
        self.write(":SENS:%s:RANG:AUTO 1" % self._mode_command(mode))

    def enable_reference(self):
        """ Enables the reference for the active mode.
        """
        self.write(":CALC:SCAL:STAT 1;:CALC:FUNC NULL")

    def disable_reference(self):
        """ Disables the reference for the active mode.
        """
        self.write(":CALC:SCAL:STAT 0")


class VoltageChannel(BaseChannel):
    MODES = {
        'voltage': 'VOLT', 'voltage ac': 'VOLT:AC',
        'resistance': 'RES',
        'period': 'PER', 'frequency': 'FREQ',
        'temperature': 'TEMP'
    }
    mode = Instrument.control(
        ":FUNC? (@{ch})", ':CONF:%s (@{ch})',
        """ A string property that controls the configuration mode for measurements,
        which can take the values:  ``voltage`` (DC),  ``voltage ac``, ``resistance`` (2-wire),
        ``period``, ``temperature``, and ``frequency``.""",
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )

    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC voltage measurement in Volts, based on the
        active :attr:`~.Agilent34970A.mode`. """
    )
    voltage_range = Instrument.control(
        ":VOLT:DC:RANG? (@{ch})", ":VOLT:DC:RANG:AUTO 0,(@{ch});:VOLT:DC:RANG %g,(@{ch})",
        """ A floating point property that controls the DC voltage range in
        Volts, which can take values from 0 to 300 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 300]
    )
    voltage_nplc = Instrument.control(
        ":VOLT:DC:NPLC? (@{ch})", ":VOLT:DC:NPLC %g, (@{ch})",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC voltage measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 200, where 0.02, 0.2, 1,
        2, 10, 20, 100 and 200 are defined levels. """
    )
    voltage_resolution = Instrument.control(
        ":VOLT:DC:RES? (@{ch})", ":VOLT:DC:RES %g,(@{ch})",
        """ A floating property that controls the resolution in Volts. """,
        validator=truncated_range,
        values=[0, 300.0]
    )
    voltage_reference = BaseChannel.reference
    voltage_gain = BaseChannel.gain
    voltage_unit = BaseChannel.unit
    voltage_high_input_impedance = Instrument.control(
        "INP:IMP:AUTO? (@{ch})", "INP:IMP:AUTO %s,(@{ch})",
        """Control if high input resistance mode is enabled.

        Only valid for dc voltage measurements.
        When disabled (default), the input resistance is fixed
        at 10 MOhms for all ranges. If enabled, the input resistance is set to
        >10 GOhms for the 100 mV, 1 V, and 10 V ranges.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )
    voltage_aperature = Instrument.control(
        ":VOLT:APER? (@{ch})", ":VOLT:APER %g, (@{ch})",
        """ A floating point property that controls the aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 300µs to 1.0 s. """,
        validator=truncated_range,
        values=[300e-6, 1.0]
    )
    voltage_ac_range = Instrument.control(
        ":VOLT:AC:RANG? (@{ch})", ":VOLT:AC:RANG:AUTO 0,(@{ch});:VOLT:AC:RANG %g,(@{ch})",
        """ A floating point property that controls the AC voltage range in
        Volts, which can take values from 0 to 300 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 300]
    )
    voltage_ac_resolution = Instrument.control(
        ":VOLT:AC:RES? (@{ch})", ":VOLT:AC:RES %g,(@{ch})",
        """ A floating property that controls the resolution in Volts. """,
        validator=truncated_range,
        values=[0, 300.0]
    )
    voltage_ac_reference = BaseChannel.reference
    voltage_ac_gain = BaseChannel.gain
    voltage_ac_unit = BaseChannel.unit
    # voltage_ac_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the DC current reference
    #     value in Volts, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # voltage_ac_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the DC current reference
    #     value in Volts, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # voltage_ac_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )
    voltage_ac_bandwidth = Instrument.control(
        ":VOLT:AC:BAND? (@{ch})", ":VOLT:AC:BAND %g,(@{ch})",
        """ A floating point property that sets the AC current detector
        to the lowest frequency in Hz, which can take the values 3, 20, and 200 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 20, 200]
    )

    ###############
    # Temperature #
    ###############

    temperature = Instrument.measurement(
        ":READ?",
        """ Reads a temperature measurement, based on the
        active :attr:`~.Agilent34970A.mode`. """
    )
    temperature_nplc = Instrument.control(
        ":TEMP:NPLC? (@{ch})", ":TEMP:NPLC %g, (@{ch})",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the temperature measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 200, where 0.02, 0.2, 1,
        2, 10, 20, 100 and 200 are defined levels. """
    )
    temperature_thermocouple = Instrument.control(
        ":TEMP:TRAN:TC:TYPE? (@{ch})", ":TEMP:TRAN:TYPE TC,(@{ch});:TEMP:TRAN:TC:TYPE %s,(@{ch})",
        """ A character that defines the thermocoupler type B|E|J|K|N|R|S|T """
    )
    temperature_reference = BaseChannel.reference
    temperature_gain = BaseChannel.gain
    temperature_unit = BaseChannel.unit
    # temperature_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the temperature reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # temperature_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the temperature reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # temperature_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )
    temperature_aperature = Instrument.control(
        ":TEMP:APER? (@{ch})", ":TEMP:APER %g, (@{ch})",
        """ A floating point property that controls the aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 400µs to 1.0 s. """,
        validator=truncated_range,
        values=[400e-6, 1.0]
    )

    ####################
    # Resistance (Ohm) #
    ####################

    resistance = Instrument.measurement(
        ":READ?",
        """ Reads a resistance measurement in Ohms for both 2-wire and 4-wire
        configurations, based on the active :attr:`~.Agilent34970A.mode`. """
    )
    resistance_range = Instrument.control(
        ":RES:RANG? (@{ch})", ":RES:RANG:AUTO 0,(@{ch});:RES:RANG %g,(@{ch})",
        """ A floating point property that controls the 2-wire resistance range
        in Ohms, which can take values from 0 to 100 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_nplc = Instrument.control(
        ":RES:NPLC? (@{ch})", ":RES:NPLC %g,(@{ch})",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 2-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1,
        10 and 100 are defined levels. """
    )
    resistance_resolution = Instrument.control(
        ":RES:RES? (@{ch})", ":RES:RES %g,(@{ch})",
        """ A floating property that controls the resolution in Ohms. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_reference = BaseChannel.reference
    resistance_gain = BaseChannel.gain
    resistance_unit = BaseChannel.unit
    # resistance_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the resistance reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # resistance_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the resistance gain
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # resistance_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )

    ##################
    # Frequency (Hz) #
    ##################

    frequency = Instrument.measurement(
        ":READ?",
        """ Reads a frequency measurement in Hz, based on the
        active :attr:`~.Agilent34970A.mode`. """
    )
    frequency_range = Instrument.control(
        ":FREQ:VOLT:RANG? (@{ch})", ":FREQ:VOLT:RANG:AUTO 0,(@{ch});:FREQ:VOLT:RANG %g,(@{ch})",
        """ A floating point property that controls the voltage range in
        Volts, which can take values from 0 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1000]
    )
    frequency_aperature = Instrument.control(
        ":FREQ:APER? (@{ch})", ":FREQ:APER %g,(@{ch})",
        """ A floating point property that controls the frequency aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )
    frequency_reference = BaseChannel.reference
    frequency_gain = BaseChannel.gain
    frequency_unit = BaseChannel.unit
    # frequency_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the frequency reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # frequency_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the frequency gain
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # frequency_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )

    ##############
    # Period (s) #
    ##############

    period = Instrument.measurement(
        ":READ?",
        """ Reads a period measurement in seconds, based on the
        active :attr:`~.Agilent34970A.mode`. """
    )
    period_range = Instrument.control(
        ":PER:VOLT:RANG? (@{ch})", ":PER:VOLT:RANG:AUTO 0,(@{ch});:PER:VOLT:RANG %g,(@{ch})",
        """ A floating point property that controls the voltage range in
        Volts, which can take values from 0 to 1000 V.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1000]
    )
    period_aperature = Instrument.control(
        ":PER:APER? (@{ch})", ":PER:APER %g,(@{ch})",
        """ A floating point property that controls the period aperature in seconds,
        which sets the integration period and measurement speed. Takes values
        from 0.01 to 1.0 s. """,
        validator=truncated_range,
        values=[0.01, 1.0]
    )
    period_reference = BaseChannel.reference
    period_gain = BaseChannel.gain
    period_unit = BaseChannel.unit
    # period_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the period reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # period_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the period gain
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # period_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )

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
            self.mode = 'resistance 4W'
            self.resistance_4W_range = max_resistance
        else:
            raise ValueError("Agilent 34970A only supports 2 or 4 wire"
                             "resistance meaurements.")

    def measure_period(self):
        """ Configures the instrument to measure the period. """
        self.mode = 'period'

    def measure_frequency(self):
        """ Configures the instrument to measure the frequency. """
        self.mode = 'frequency'


class Voltage4wChannel(VoltageChannel):
    MODES = {
        'voltage': 'VOLT', 'voltage ac': 'VOLT:AC',
        'resistance': 'RES', 'resistance 4W': 'FRES',
        'period': 'PER', 'frequency': 'FREQ',
        'temperature': 'TEMP'
    }
    mode = Instrument.control(
        ":FUNC? (@{ch})", ':CONF:%s (@{ch})',
        """ A string property that controls the configuration mode for measurements,
        which can take the values:
        ``voltage`` (DC),  ``voltage ac``, ``resistance`` (2-wire),
        ``resistance 4W`` (4-wire), ``period``,
        ``temperature``, and ``frequency``.""",
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )

    resistance_4W_range = Instrument.control(
        ":FRES:RANG? (@{ch})", ":FRES:RANG:AUTO 0,(@{ch});:FRES:RANG %g,(@{ch})",
        """ A floating point property that controls the 4-wire resistance range
        in Ohms, which can take values from 0 to 100 MOhms.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_4W_nplc = Instrument.control(
        ":FRES:NPLC? (@{ch})", ":FRES:NPLC %g,(@{ch})",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the 4-wire resistance measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1,
        10 and 100 are defined levels. """
    )
    resistance_4W_resolution = Instrument.control(
        ":FRES:RES? (@{ch})", ":FRES:RES %g,(@{ch})",
        """ A floating property that controls the resolution in Ohms. """,
        validator=truncated_range,
        values=[0, 100e6]
    )
    resistance_4W_reference = BaseChannel.reference
    resistance_4W_gain = BaseChannel.gain
    resistance_4W_unit = BaseChannel.unit
    # resistance_4W_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the resistance reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # resistance_4W_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the resistance gain
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # resistance_4W_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )


class CurrentChannel(BaseChannel):
    MODES = {
        'current': 'CURR', 'current ac': 'CURR:AC'
    }
    mode = Instrument.control(
        ":FUNC? (@{ch})", ':CONF:%s (@{ch})',
        """ A string property that controls the configuration mode for measurements,
        which can take the values: ``current`` (DC), ``current ac``. """,
        validator=strict_discrete_set,
        values=MODES,
        map_values=True,
        get_process=lambda v: v.replace('"', '')
    )
    ###############
    # Current (A) #
    ###############

    current = Instrument.measurement(
        ":READ?",
        """ Reads a DC or AC current measurement in Amps, based on the
        active :attr:`~.Agilent34970A.mode`. """
    )
    current_range = Instrument.control(
        ":CURR:DC:RANG? (@{ch})", ":CURR:DC:RANG:AUTO 0,(@{ch});:CURR:DC:RANG %g,(@{ch})",
        """ A floating point property that controls the DC current range in
        Amps, which can take values from 0.01 to 1.0 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1.0]
    )
    current_nplc = Instrument.control(
        ":CURR:DC:NPLC? (@{ch})", ":CURR:DC:NPLC %g,(@{ch})",
        """ A floating point property that controls the number of power line cycles
        (NPLC) for the DC current measurements, which sets the integration period
        and measurement speed. Takes values from 0.02 to 100, where 0.02, 0.2, 1, 2,
        10, 20, 100 and 200 are defined levels. """
    )
    current_resolution = Instrument.control(
        ":CURR:DC:RES? (@{ch})", ":CURR:DC:RES %g,(@{ch})",
        """ A floating property that controls the resolution in Amps. """,
        validator=truncated_range,
        values=[0, 1.0]
    )
    current_reference = BaseChannel.reference
    current_gain = BaseChannel.gain
    current_unit = BaseChannel.unit
    # current_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the current reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # current_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the current gain
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # current_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )
    current_ac_range = Instrument.control(
        ":CURR:AC:RANG? (@{ch})", ":CURR:AC:RANG:AUTO 0,(@{ch});:CURR:AC:RANG %g,(@{ch})",
        """ A floating point property that controls the AC current range in
        Amps, which can take values from 0 to 1.0 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[0, 1.0]
    )
    current_ac_resolution = Instrument.control(
        ":CURR:AC:RES? (@{ch})", ":CURR:AC:RES %g,(@{ch})",
        """ A floating property that controls the resolution in Amps. """,
        validator=truncated_range,
        values=[0, 3.0]
    )
    current_ac_reference = BaseChannel.reference
    current_ac_gain = BaseChannel.gain
    current_ac_unit = BaseChannel.unit
    # current_ac_reference = Instrument.control(
    #     ":CALC:SCAL:OFFS? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:OFFS %g,(@{ch})",
    #     """ A floating point property that controls the current reference
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # current_ac_gain = Instrument.control(
    #     ":CALC:SCAL:GAIN? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:GAIN %g,(@{ch})",
    #     """ A floating point property that controls the current gain
    #     value, which can take values from -1E15 to 1E15. """,
    #     validator=truncated_range,
    #     values=[-1E15, 1E15]
    # )
    # current_ac_unit = Instrument.control(
    #     ":CALC:SCAL:UNIT? (@{ch})", ":CALC:SCAL:STAT ON,(@{ch});:CALC:SCAL:UNIT '%s',(@{ch})",
    #     """ A string property that controls a custom label of 3 characters. """
    # )
    current_ac_bandwidth = Instrument.control(
        ":CURR:AC:BAND? (@{ch})", ":CURR:AC:BAND %g,(@{ch})",
        """ A floating point property that sets the AC current detector
        to the lowest frequency in Hz, which can take the values 3, 20, and 200 Hz. """,
        validator=truncated_discrete_set,
        values=[3, 20, 200]
    )

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

    # def enable_filter(self, mode=None, type='repeat', count=1):
    #     """ Enables the averaging filter for the active mode,
    #     or can set another mode by its name.

    #     :param mode: A valid :attr:`~.Agilent34970A.mode` name, or None for the active mode
    #     :param type: The type of averaging filter, either 'repeat' or 'moving'.
    #     :param count: A number of averages, which can take take values from 1 to 100
    #     """
    #     self.write(":SENS:%s:AVER:STAT 1")
    #     self.write(":SENS:%s:AVER:TCON %s")
    #     self.write(":SENS:%s:AVER:COUN %d")

    # def disable_filter(self, mode=None):
    #     """ Disables the averaging filter for the active mode,
    #     or can set another mode by its name.

    #     :param mode: A valid :attr:`~.Agilent34970A.mode` name, or None for the active mode
    #     """
    #     self.write(":SENS:%s:AVER:STAT 0" % self._mode_command(mode))


class Agilent34970A(Instrument):
    """ Represents the Agilent 34970A Data Acq and provides a high-level
    interface for interacting with the instrument.

    .. code-block:: python

        meter = Agilent34970A("GPIB::1")
        meter.ch_101.mode = 'voltage'
        print(meter.ch_101.voltage)

    """
    def __init__(self, adapter, name="Agilent 34970A", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )
        for slot in [100, 200, 300]:
            card = self.card_type(slot)
            if card == '34901A':
                for ch in range(1, 11):    # Channels 1 to 10 have full support
                    child = self.add_child(Voltage4wChannel, slot+ch)
                    child._protected = True
                for ch in range(11, 21):   # Channels 11 to 20 don't support 4W
                    child = self.add_child(VoltageChannel, slot+ch)
                    child._protected = True
                for ch in range(21, 23):   # Channels 21 and 22 are current only
                    child = self.add_child(CurrentChannel, slot+ch)
                    child._protected = True
            if card == '34902A':          # Untested card!
                for ch in range(1, 9):     # Channels 1 to 8 have full support
                    child = self.add_child(Voltage4wChannel, slot+ch)
                    child._protected = True
                for ch in range(9, 17):    # Channels 9 to 16 don't support 4W
                    child = self.add_child(VoltageChannel, slot+ch)
                    child._protected = True
        self.working_ch = None

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

    scan_list = Instrument.control(
        'ROUT:SCAN?', 'ROUT:SCAN (@%s)',
        """ A string property that controls the configuration of the
        scan list. The string is a list of channels or a range
        101, 102, 108 or 101:110 """)

    def card_type(self, slot):
        """ Get the card type for a slot.
        :param slot: A valid slot number (100, 200 or 300). """
        return self.ask(f'SYST:CTYP? {slot}').split(',')[1]

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
        calling :meth:`~.Agilent34970A.local`. Only for RS-232. """
        self.write(":SYST:RWL")

    def reset(self):
        """ Resets the instrument state. """
        self.write("*RST;:STAT:PRES;:*CLS;")
