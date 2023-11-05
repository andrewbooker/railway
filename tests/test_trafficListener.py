from application.trafficListener import TrafficListener
from lib.detectionRouter import DetectionRouter
from lib.ports import Ports


class DetectionRouterSpy(DetectionRouter):
    def __init__(self):
        DetectionRouter.__init__(self)
        self.last_call = None

    def receiveUpdate(self, portId, value):
        self.last_call = (portId, value)


class ConstInput:
    def __init__(self, v):
        self.v = v

    def get(self):
        return self.v


class DeviceWithConstInput(Ports):
    def __init__(self, i: ConstInput):
        self.i = i

    def input(self, port):
        return self.i


def test_polling_does_nothing_given_no_devices_or_registered_ports():
    router = DetectionRouterSpy()
    listener = TrafficListener(router)

    listener.poll()
    assert router.last_call is None


def test_polling_sends_value_read_from_port_to_receiver():
    router = DetectionRouterSpy()
    listener = TrafficListener(router)

    listener.registerInputDevices("inputbox", DeviceWithConstInput(ConstInput(8)))
    listener.registerPorts("inputbox", [66])

    listener.poll()

    assert router.last_call == ("inputbox_66", 8)


def test_polling_only_sends_value_if_it_changes():
    router = DetectionRouterSpy()
    listener = TrafficListener(router)
    device = DeviceWithConstInput(ConstInput(8))

    listener.registerInputDevices("inputbox", device)
    listener.registerPorts("inputbox", [66])

    assert router.last_call is None
    listener.poll()
    assert router.last_call == ("inputbox_66", 8)
    router.last_call = None
    listener.poll()
    assert router.last_call is None

    device.i.v = 7
    listener.poll()
    assert router.last_call == ("inputbox_66", 7)
