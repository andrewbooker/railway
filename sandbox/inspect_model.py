#!/usr/bin/env python
from _imports import *
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
