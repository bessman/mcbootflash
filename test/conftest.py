import json

import mock_serial
import pytest


@pytest.fixture
def device(request):
    with open(request.param, "r") as fp:
        traffic = json.load(fp)

    device = mock_serial.MockSerial()
    device.open()
    proto_stub = {}

    for tx, rx in zip(traffic["tx"], traffic["rx"]):
        try:
            proto_stub[bytes(tx)] = proto_stub[bytes(tx)] + [bytes(rx)]
        except KeyError:
            proto_stub[bytes(tx)] = [bytes(rx)]

    for k, v in proto_stub.items():
        if len(v) == 1:
            device.stub(receive_bytes=k, send_bytes=v[0])
            continue
        device.stub(receive_bytes=k, send_fn=lambda n, v=v: ([None] + v)[n])

    yield device
    device.close()
