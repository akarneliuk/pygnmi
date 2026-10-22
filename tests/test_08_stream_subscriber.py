"""
Collection of unit tests for STREAM subscriptions that need no target: a fake gRPC
channel hands the subscriber the SubscribeResponse messages a target would send.
"""

# Modules
import threading

import pytest

from pygnmi.client import StreamSubscriber, gNMIclient
from pygnmi.create_gnmi_path import gnmi_path_generator
from pygnmi.spec.v080.gnmi_pb2 import (
    Notification,
    SubscribeRequest,
    SubscribeResponse,
    SubscriptionList,
    TypedValue,
    Update,
)


# Helpers
class FakeChannel:
    """Stands in for a grpc.Channel: Subscribe yields the given responses, then stays
    open (as a STREAM subscription does) until the client stops sending requests."""

    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def stream_stream(self, method, request_serializer=None, response_deserializer=None, **kwargs):
        def call(request_iterator, metadata=None, **kw):
            self.requests.append(next(request_iterator))
            yield from self.responses
            for _ in request_iterator:  # returns when the subscriber is closed
                pass

        return call

    def unary_unary(self, *args, **kwargs):
        return None

    def unary_stream(self, *args, **kwargs):
        return None

    def stream_unary(self, *args, **kwargs):
        return None


def update_response(interface: str, status: str) -> SubscribeResponse:
    return SubscribeResponse(
        update=Notification(
            timestamp=1,
            update=[
                Update(
                    path=gnmi_path_generator(f"interfaces/interface[name={interface}]/state/oper-status"),
                    val=TypedValue(string_val=status),
                )
            ],
        )
    )


def sync_response() -> SubscribeResponse:
    return SubscribeResponse(sync_response=True)


def subscriber(responses, **kwargs) -> StreamSubscriber:
    request = SubscribeRequest(subscribe=SubscriptionList(mode=0))
    return StreamSubscriber(FakeChannel(responses), request, [], **kwargs)


# Tests
def test_initial_updates_are_coalesced_until_sync_response():
    sub = subscriber([update_response("Ethernet1", "UP"), update_response("Ethernet2", "DOWN"), sync_response()])
    try:
        first = sub.get_update(timeout=2)
        assert first["sync_response"] is True
        assert len(first["update"]["update"]) == 2
    finally:
        sub.close()


def test_target_without_sync_response_blocks_the_default():
    """Some targets send no sync_response on STREAM subscriptions."""
    sub = subscriber([update_response("swp1", "UP"), update_response("swp2", "DOWN")])
    try:
        with pytest.raises(TimeoutError):
            sub.get_update(timeout=0.5)
    finally:
        sub.close()


def test_target_without_sync_response_with_wait_for_sync_false():
    sub = subscriber([update_response("swp1", "UP"), update_response("swp2", "DOWN")], wait_for_sync=False)
    try:
        first = sub.get_update(timeout=2)
        second = sub.get_update(timeout=2)
        assert len(first["update"]["update"]) == 1
        assert len(second["update"]["update"]) == 1
        assert "sync_response" not in first
    finally:
        sub.close()


def test_a_timeout_before_sync_response_keeps_the_updates_already_received():
    gate = threading.Event()

    def responses():
        yield update_response("Ethernet1", "UP")
        gate.wait(5)
        yield update_response("Ethernet2", "DOWN")
        yield sync_response()

    sub = subscriber(responses())
    try:
        with pytest.raises(TimeoutError):
            sub.get_update(timeout=0.5)
        gate.set()
        first = sub.get_update(timeout=2)
        assert first["sync_response"] is True
        assert len(first["update"]["update"]) == 2
    finally:
        sub.close()


def test_after_sync_response_updates_arrive_one_by_one():
    sub = subscriber([update_response("Ethernet1", "UP"), sync_response(), update_response("Ethernet1", "DOWN")])
    try:
        sub.get_update(timeout=2)
        change = sub.get_update(timeout=2)
        assert len(change["update"]["update"]) == 1
        assert "sync_response" not in change
    finally:
        sub.close()


def test_subscribe2_passes_wait_for_sync_to_the_stream_subscriber(monkeypatch):
    seen = {}

    def fake_subscribe_stream(self, subscribe, target=None, extension=None, wait_for_sync=True):
        seen["wait_for_sync"] = wait_for_sync

    monkeypatch.setattr(gNMIclient, "subscribe_stream", fake_subscribe_stream)
    client = gNMIclient.__new__(gNMIclient)
    client.subscribe2(subscribe={"mode": "stream", "subscription": []}, wait_for_sync=False)
    assert seen == {"wait_for_sync": False}
