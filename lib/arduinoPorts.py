import pyfirmata

from lib.monitor import StatusComponent
from lib.ports import Ports


class Input:
    def __init__(self, board, port):
        self.pin = board.get_pin("d:%d:i" % port)

    def get(self):
        return self.pin.read()


class Output:
    def __init__(self, board, port):
        self.pin = board.get_pin("d:%d:o" % port)

    def set(self, v):
        return self.pin.write(v)


class ServoPwmPort:
    def __init__(self, board, port, initVal):
        self.pin = board.get_pin("d:%d:p" % port)
        self.set(initVal)

    def set(self, v):
        self.pin.write(v / 100.0)


class StdOutStatus(StatusComponent):
    def setValue(self, v):
        print(v)


class UsingArduino(Ports):
    def __init__(self, status: StatusComponent = StdOutStatus(0)):
        self.status = status
        self.board = pyfirmata.ArduinoMega("/dev/ttyACM0")
        pyfirmata.util.Iterator(self.board).start()
        self.status.setValue("Arduino started")

    def __del__(self):
        self.board.exit()
        self.status.setValue("Arduino stopped")

    def input(self, port):
        return Input(self.board, port)

    def output(self, port):
        return Output(self.board, port)

    def servoPwmPort(self, port, initVal):
        return ServoPwmPort(self.board, port, initVal)
