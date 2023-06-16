"""
To use the pigpio daemon.
"""

import pigpio as io

class IO(io.pi):
    """
    The parent of this class must be instantiated to interface with pigpio daemon. This is done by the instance of IO in motor.py.
    """

    def set_low(self, pin):
        super().write(pin, 0)

    def set_high(self, pin):
        super().write(pin, 1)

    def set_output(self, pin):
        super().set_mode(pin, io.OUTPUT)

    def set_input(self, pin):
        super().set_mode(pin, io.INPUT)
