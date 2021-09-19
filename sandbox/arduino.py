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


def detect(shouldStop, pin):
    inP = Input(board, pin)

    stdout("read started on %d" % pin)
    inState = 0
    while not shouldStop.is_set():
        d = inP.get()
        if d is not inState:
            stdout("%d in state %d" % (pin, 0 if d != 1 else d))
            inState = d

        time.sleep(0.1)
    stdout("stopping read on %d" % pin)

def blink(shouldStop, pin):
    outPin = Output(board, pin)
    state = 0
    while not shouldStop.is_set():
        outPin.set(state)
        state = 1 if state == 0 else 0
        time.sleep(0.5)
    stdout("stopping blink on %d" % pin)

print("starting")

board = pyfirmata.ArduinoMega("/dev/ttyACM0")
print("board loaded")
it = pyfirmata.util.Iterator(board)
it.start()

shouldStop = threading.Event()
threads = []
threads.append(threading.Thread(target=detect, args=(shouldStop,52), daemon=True))
threads.append(threading.Thread(target=detect, args=(shouldStop,53), daemon=True))
threads.append(threading.Thread(target=blink, args=(shouldStop,5), daemon=True))
print("read iterator started (press 'q' to stop)")
[t.start() for t in threads]

while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()

[t.join() for t in threads]
