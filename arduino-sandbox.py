#!/usr/bin/env python

import pyfirmata
import time
import threading
import sys
import readchar

def stdout(s):
    sys.stdout.write("%s\n\r" % s)

def detect(shouldStop):
    inPin = board.get_pin("d:52:i")
    stdout("read started")

    inState = 0
    while not shouldStop.is_set():
        d = inPin.read()
        if d is not inState:
            stdout("in state %d" % (0 if d != 1 else d))
            inState = d

        time.sleep(0.1)

print("starting")

board = pyfirmata.ArduinoMega("/dev/ttyACM0")
print("board loaded")
it = pyfirmata.util.Iterator(board)
it.start()

shouldStop = threading.Event()
thread = threading.Thread(target=detect, args=(shouldStop,), daemon=True)
print("read iterator started (press 'q' to stop)")
thread.start()

while not shouldStop.is_set():
    c = readchar.readchar()
    if c == "q":
        shouldStop.set()

thread.join()
