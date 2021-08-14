#!/usr/bin/env python

from lib.cmd import *
import sys

def say(what):
	sys.stdout.write("%s\r\n" % what)

targets = [Cmd(say)]
threads = [threading.Thread(target=t.start, args=(shouldStop,), daemon=True) for t in targets]
[thread.start() for thread in threads]
[thread.join() for thread in threads]



