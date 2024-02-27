#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

"""
This example demonstrates how to make a graphical interface, and uses
a random number generator to simulate data so that it does not require
an instrument to use.

Run the program by changing to the directory containing this file and calling:

python gui.py

"""

import sys
import random
from time import sleep

from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.instruments.agilent import Agilent34401A

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=100)
    delay = FloatParameter('Delay Time', units='s', default=0.2)
    seed = Parameter('Random Seed', default='12345')

    DATA_COLUMNS = ['Iteration', 'Random Number']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)
        self.meter = Agilent34401A("GPIB::22")

   
        self.meter.write('*RST')
        self.meter.write('*CLS')

        self.meter.write('FUNC "VOLT"')
        self.meter.write('VOLT:RES MAX')
        self.meter.write('VOLT:NPLC MIN')
        self.meter.write('VOLT:RANG:AUTO OFF')
        self.meter.write('VOLT:DC:RANG 1')

        self.meter.write('DISP OFF')
        self.meter.write('ZERO:AUTO ONCE')
        self.meter.write('CALC:STAT OFF')
        self.meter.write('TRIG:SOUR IMM')
        self.meter.write('TRIG:DEL 0')
        self.meter.write(f'SAMP:COUN {self.iterations}')

        # self.meter.mode = 'voltage'
        # self.meter.voltage_range = 1
        # self.meter.voltage_nplc = 0.02
        # self.meter.write('ZERO:AUTO ONCE')


    def execute(self):
        log.info("Starting to generate numbers")
        # self.meter.write('INIT')
        # sleep(1)
        # data = self.meter.values('FETC?')
        data = self.meter.values('READ?')

        for i, measure in enumerate(data):
            data = {
                'Iteration': i,
                'Random Number': measure
            }
            log.debug("Produced numbers: %s" % data)
            self.emit('results', data)
            self.emit('progress', 100 * i / self.iterations)
            # sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")


class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=TestProcedure,
            inputs=['iterations', 'delay', 'seed'],
            displays=['iterations', 'delay', 'seed'],
            x_axis='Iteration',
            y_axis='Random Number'
        )
        self.setWindowTitle('GUI Example')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
