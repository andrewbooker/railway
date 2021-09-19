#!/usr/bin/env python

import pyfirmata
import time
import threading
import sys
import readchar

def stdout(s):
    sys.stdout.write("%s\n\r" % s)

class Input():
    def __init__(self, board, port):
        self.pin = board.get_pin("d:%d:i" % port)

    def get(self):        
        return self.pin.read()

class Output():
    def __init__(self, board, port):
        self.pin = board.get_pin("d:%d:o" % port)

    def set(self, v):        
        return self.pin.write(v)

class UsingArduino():
    def __init__(self):
        self.board = pyfirmata.ArduinoMega("/dev/ttyACM0")
        pyfirmata.util.Iterator(self.board).start()
        print("Arduino started")

    def __del__(self):
        self.board.exit()
        print("Arduino stopped")

    def input(self, port):
        return Input(self.board, port)

    def output(self, port):
        return Output(self.board, port)


def detect(shouldStop, ua, pin):
    inP = ua.input(pin)

    stdout("read started on %d" % pin)
    inState = 0
    while not shouldStop.is_set():
        d = inP.get()
        if d is not inState:
            stdout("%d in state %d" % (pin, 0 if d != 1 else d))
            inState = d

        time.sleep(0.1)
    stdout("stopping read on %d" % pin)

def blink(shouldStop, ua, pin):
    outPin = ua.output(pin)
    state = 0
    while not shouldStop.is_set():
        outPin.set(state)
        state = 1 if state == 0 else 0
        time.sleep(0.5)
    stdout("stopping blink on %d" % pin)


ua = UsingArduino()
shouldStop = threading.Event()
threads = []
threads.append(threading.Thread(target=detect, args=(shouldStop, ua, 52), daemon=True))
threads.append(threading.Thread(target=detect, args=(shouldStop, ua, 53), daemon=True))
threads.append(threading.Thread(target=blink, args=(shouldStop, ua, 5), daemon=True))
print("Started (press 'q' to stop)")
[t.start() for t in threads]

while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()

[t.join() for t in threads]
del(ua)
