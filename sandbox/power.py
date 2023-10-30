#!/usr/bin/env python3

import os
import sys
parentDir = os.path.dirname(os.getcwd())
sys.path.append(parentDir)
from lib.monitor import PowerMonitor
from lib.cmd import Cmd
import time
import random
import threading


def set_power(monitor, shouldStop):
    while not shouldStop.is_set():
        monitor.setValue(int(50 + (random.random() * 40)))
        time.sleep(2 * random.random())


def set_msg(monitor, shouldStop):
    opts = [
        "Starting", "Stopping", "Running", "Speeding", "Slowing", "Crawling", "Stopped"
    ]
    while not shouldStop.is_set():
        monitor.setMessage(opts[int(random.random() * len(opts))])
        time.sleep(2 * random.random())


def nothing(monitor):
    return lambda: monitor.setMessage("reams and reams and reams")


if __name__ == '__main__':
    os.system("clear")
    monitor = PowerMonitor()
    shouldStop = threading.Event()
    cmd = Cmd(nothing(monitor))
    monitor.setMessage("starting")

    threads = [
        threading.Thread(target=set_power, args=(monitor, shouldStop), daemon=True),
        threading.Thread(target=set_msg, args=(monitor, shouldStop), daemon=True),
        threading.Thread(target=cmd.start, args=(shouldStop,), daemon=True)
    ]
    monitor.setMessage("threads ready")
    [thread.start() for thread in threads]
    monitor.setMessage("threads started")
    [thread.join() for thread in threads]
    monitor.setMessage("threads stopped")


