#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments import Instrument
import re

#_reg_value = re.compile(r"([-+]?[0-9]*\.?[0-9]+)\s+\w+")
_reg_value = re.compile(r"([-+]?([0-9]*[.])?[0-9]+([eE][-+]?\d+)?)")


def extract_value(reply):
    """ extract numerical value from reply. If none can be found the reply
    is returned unchanged.
    :param reply: reply string
    :returns: string with only the numerical value
    """
    r = _reg_value.search(reply)
   # r = re.search(r"([-+]?[0-9]*\.?[0-9]+)\s+\w+", reply)
    #r = re.search(r"([-+]?([0-9]*[.])?[0-9]+([eE][-+]?\d+)?)", reply)
    # print(reply, r, r.groups()[0])
    if r:
        return r.groups()[0]
    else:
        return reply


class Fluke5100B(Instrument):
    """ Represents the Fluke 5100B instrument.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Fluke 5100B",
            preprocess_reply=extract_value,
            timeout=10000,
            **kwargs
        )

    display = Instrument.measurement(
        "?", """ Reads the display. """)

    status = Instrument.measurement(
        "!?", """ Reads the status. """, cast=str)

    voltage = Instrument.control(
        "GV?", "C%GV,",
        """ A floating point property that controls the voltage
        in Volts. This property can be set.
        """
    )

    current = Instrument.control(
        "GA?", "C%GA,",
        """ A floating point property that controls the current
        in Ampere. This property can be set.
        """
    )

    resistance = Instrument.control(
        "GZ?", "X0C%GZ,",
        """ A floating point property that controls the resistance
        in Ohm. This property can be set.
        """
    )

    resistance_4w = Instrument.control(
        "GZ?", "X1C%GZ,",
        """ A floating point property that controls the resistance
        in Ohm. This property can be set.
        """
    )

    # frequency = Instrument.control(
    #     "GH?", "C%gH,",
    #     """ A floating point property that controls the voltage
    #     in Volts. This property can be set.
    #     """
    # )

    @property
    def frequency(self):
        vals = self.values("GH?")
#        return extract_value(vals)
        return vals[0]

    @frequency.setter
    def frequency(self, value):
        # print(value)
        if value == 0:
            stat = self.status
            if stat[2] == '2':
                current = self.current
                self.write(f'C+{current}A,')
            elif stat[2] == '4':
                volt = self.voltage
                self.write(f'C+{volt}V,')
        else:
            self.write(f'C{value}H,')

    def enable(self):
        """ Enables the output of the signal. """
        self.write("N")

    def disable(self):
        """ Disables the output of the signal. """
        self.write("S")

    def enable_50_overdrive(self):
        """ Enables the 50 Ohm divider override. """
        self.write("R1")

    def disable_50_overdrive(self):
        """ Disable the 50 Ohm divider override. """
        self.write("R0")

    def reset_rem(self):
        """ Reset instrument, stay in remote. """
        self.write("CC")
