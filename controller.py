#!/usr/bin/env python

import sys
import math
import os
import threading
os.system("clear")
print("")

class PowerMonitor():
    def __init__(self):
        self.scale = 100
        self.height = 3
        self.msg = ""
        self.bar = 0
        self.firstValueWritten = False
        self.lock = threading.Lock()

    def _render(self):
        if self.lock.locked():
            return
        self.lock.acquire()
        fill = self.scale - self.bar

        if self.firstValueWritten:
            sys.stdout.write("\x1b[A" * (self.height + 1))
            sys.stdout.flush()
        else:
            self.firstValueWritten = True

        sys.stdout.write("%s%s\n\r" % (self.msg, " " * (self.scale - len(self.msg))))
        for h in range(self.height):
            sys.stdout.write("\033[92m%s\033[0m" % ("\u2589" * self.bar))
            sys.stdout.write("\033[0;37m%s\033[0m" % ("\u2589" * fill))
            sys.stdout.write("\n\r")

        sys.stdout.flush()
        self.lock.release()

    def setValue(self, value):
        self.bar = value
        self._render()

    def setMessage(self, m):
        self.msg = m
        self._render()


import time
import RPi.GPIO as GPIO

class Speed():
    def __init__(self, port, monitor):
        self.monitor = monitor
        GPIO.setup(port, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(port, 100)
        self.pwm.start(0)
        self.current = 0
        self.target = 0
        self.secsPerIncr = 3.0 / 50
        self.monitor.setValue(0)
        self.onDone = None

    def __del__(self):
        self.pwm.stop()

    def _setTo(self, dc):
        self.pwm.ChangeDutyCycle(dc)
        self.current = dc
        self.monitor.setValue(dc)

    def rampTo(self, dc, onDone):
        self.onDone = onDone
        self.target = max(min(dc, 100), 0)

    def start(self, shouldStop):
        while not shouldStop.is_set():
            if self.target < self.current:
                self._setTo(self.current - 1)
            elif self.target > self.current:
                self._setTo(self.current + 1)
            elif self.onDone is not None:
                self.onDone()
                self.onDone = None

            time.sleep(self.secsPerIncr)
        if shouldStop.is_set():
            self._setTo(0)

class Direction():
    def __init__(self, port):
        self.port = port
        GPIO.setup(self.port, GPIO.OUT, initial=GPIO.LOW)

    def set(self, isForwards):
        GPIO.output(self.port, 0 if isForwards else 1)

class MotionController():
    def __init__(self, speed, direction, monitor):
        self.maxSpeed = 70
        self.speed = speed
        self.direction = direction
        self.monitor = monitor
        self.isRunning = False
        self.isStopping = False
        self.isForwards = True
        self.commandsBlocked = False
        self.monitor.setMessage("set to %s" % ("forwards" if self.isForwards else "reverse"))

    def _start(self):
        self.monitor.setMessage("ramping up %s" % ("forwards" if self.isForwards else "reverse"))
        self.direction.set(self.isForwards)
        self.isRunning = True
        self.speed.rampTo(self.maxSpeed, lambda: self.monitor.setMessage("holding steady"))

    def _setStopped(self):
        self.isRunning = False
        self.isStopping = False
        self.commandsBlocked = False
        self.monitor.setMessage("stopped")

    def _stop(self):
        if not self.isRunning:
            return
        self.isStopping = True
        self.monitor.setMessage("ramping down")
        self.speed.rampTo(0, self._setStopped)
        while self.isRunning:
            time.sleep(0.05)

    def _changeDirection(self):
        wasRunning = self.isRunning
        if self.isRunning and not self.isStopping:
            self._stop()

        self.isForwards = not self.isForwards
        self.monitor.setMessage("changing to %s" % ("forwards" if self.isForwards else "reverse"))

        if wasRunning:
            self._start()

#remove this and have something layout-aware pass 's' or 'd' commands
    def onPass(self, v, pos):
        return
        if self.isStopping or not v:
            return

        self.monitor.setMessage("passed checkpoint %s" % pos)
        if (pos in ["A"] and self.isForwards) or (pos in ["B"] and not self.isForwards):
            self.commandsBlocked = True
            self._changeDirection()

    def onCmd(self, c):
        if self.commandsBlocked:
            self.monitor.setMessage("Command blocked after checkpoint")
            return

        if c in ['s', ' ']:
            if not self.isRunning:
                self._start()
            else:
                self._stop()

        if c == 'd' or (c == 'r' and self.isForwards) or (c == 'f' and not self.isForwards):
            self._changeDirection()

        if c == '+':
            self.speed.target += 1

        if c == '-':
            self.speed.target -= 1


class Detector():
    def __init__(self, port, pos, callback):
        self.callback = callback
        self.pos = pos
        self.port = port
        self.state = 0
        GPIO.setup(self.port, GPIO.IN)

    def start(self, shouldStop):
        while not shouldStop.is_set():
            v = GPIO.input(self.port)
            if v != self.state:
                self.callback(v, self.pos)
                self.state = v
            time.sleep(0.05)

class RoutingController():
    def __init__(self, checkpoints, points, sections):
        self.checkpoints = checkpoints
        self.instructions = []

    def _attemptNext(self):
        if len(self.instructions) == 0:
            return
            
        ins = self.instructions[0]
        chk = ins.checkpoint()
        if checkpoints[chk.name] != chk.state:
            return
        
        if ins.points is not None:
            points[ins.points.name].set[ins.points.select]
        if ins.section is not None:
            sections[ins.section.name].power(ins.section.direction)

        self.instructions.pop(0)

    def instruct(self, instruction):
        self.instructions.append(instruction)
         
    def start(self, shouldStop):
        while not shouldStop.is_set():
            self._attemptNext()
            time.sleep(0.4)

import readchar

class Cmd():
    def __init__(self, callback):
        self.callback = callback

    def start(self, shouldStop):
        while not shouldStop.is_set():
            c = readchar.readchar()
            if ord(c) in [3, 27, 113]: #ctrl+C, esc or q
                shouldStop.set()
            else:
                self.callback(c)


shouldStop = threading.Event()

portA = 12
portB = 18

GPIO.setmode(GPIO.BCM)

monitor = PowerMonitor()
speed = Speed(portA, monitor)
direction = Direction(23)
controller = MotionController(speed, direction, monitor)
detectorA = Detector(14, "A", controller.onPass)
detectorB = Detector(15, "B", controller.onPass)
cmd = Cmd(controller.onCmd)
threads = []
threads.append(threading.Thread(target=speed.start, args=(shouldStop,), daemon=True))
threads.append(threading.Thread(target=detectorA.start, args=(shouldStop,), daemon=True))
threads.append(threading.Thread(target=detectorB.start, args=(shouldStop,), daemon=True))
threads.append(threading.Thread(target=cmd.start, args=(shouldStop,), daemon=True))

[thread.start() for thread in threads]
[thread.join() for thread in threads]

del speed
GPIO.cleanup() 
