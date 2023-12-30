from lib.detectionRouter import DetectionRouter


class Callback:
    def __init__(self):
        self.was_called = False

    def cb(self):
        self.was_called = True


def test_does_nothing_on_receipt_of_update_if_nothing_is_awaiting_that_port():
    router = DetectionRouter()
    router.waitFor("dev_0", 9, "nothing")
    assert router.awaiting.keys() == {("dev_0", 9)}

    router.receiveUpdate("dev_1", 9)
    assert router.awaiting.keys() == {("dev_0", 9)}
    assert router.awaiting[("dev_0", 9)][0] == "nothing"
    assert router.awaiting[("dev_0", 9)][1].canExec() is False


def test_does_nothing_on_receipt_of_update_if_nothing_is_awaiting_that_value():
    router = DetectionRouter()
    router.waitFor("dev_0", 9, "nothing")

    router.receiveUpdate("dev_0", 1)
    assert router.awaiting.keys() == {("dev_0", 9)}
    assert router.awaiting[("dev_0", 9)][0] == "nothing"
    assert router.awaiting[("dev_0", 9)][1].canExec() is False


def test_does_nothing_on_receipt_of_expected_update_if_no_callback_is_defined():
    router = DetectionRouter()
    router.waitFor("dev_0", 2, "something")

    router.receiveUpdate("dev_0", 2)
    assert len(router.awaiting.keys()) == 0


def test_invokes_built_in_callback_on_receipt_of_update_it_is_waiting_for():
    callback = Callback()

    router = DetectionRouter()
    router.setCallback(callback.cb)
    router.waitFor("dev_0", 2, "something")

    assert callback.was_called is False
    router.receiveUpdate("dev_0", 2)
    assert callback.was_called is True
    assert len(router.awaiting.keys()) == 0


def test_invokes_generated_callback_on_receipt_of_update_it_is_waiting_for():
    callback = Callback()

    router = DetectionRouter()
    cb = router.waitFor("dev_0", 2, "something")
    cb.then(callback.cb)

    assert callback.was_called is False
    router.receiveUpdate("dev_0", 2)
    assert callback.was_called is True
    assert len(router.awaiting.keys()) == 0


def test_does_nothing_if_internal_callback_is_expected_but_not_defined():
    router = DetectionRouter()

    router.setNextDetector("dev_0", 2, "something")
    router.receiveUpdate("dev_0", 2)
    assert len(router.awaiting.keys()) == 0


def test_invokes_internal_callback_on_receipt_of_update():
    callback = Callback()

    router = DetectionRouter()
    router.setCallback(callback.cb)
    router.setNextDetector("dev_0", 2, "something")

    assert callback.was_called is False
    router.receiveUpdate("dev_0", 2)
    assert callback.was_called is True
    assert len(router.awaiting.keys()) == 0
