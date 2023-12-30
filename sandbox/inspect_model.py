#!/usr/bin/env python

import sys
import os
parentDir = os.path.dirname(os.getcwd())
if "railway" not in parentDir:
    print("needs to run in sandbox")
    exit()

sys.path.append(parentDir)

from lib.model import Model

layoutStr = None
if len(sys.argv) < 2:
    print("specify layout json file")
    exit()
with open(sys.argv[1], "r") as layoutSpec:
    layoutStr = layoutSpec.read()

model = Model(layoutStr)

print("Relay ports", model.relayPorts())
print("Detection ports", model.detectionPorts())
print("Sections:")
for s in model.sections:
    print(s)
    section = model.sections[s]
    print(type(section), section.name, section.direction)

print(model.sectionFrom("arduino_41"))
