"""
Collection of unit tests to validate the 'target' argument handling of gNMIclient.

These tests do not require connectivity to a real device: they only exercise
the constructor-time validation logic.
"""
# Modules
import pytest

from pygnmi.client import gNMIclient, gNMIException


# Tests: valid targets should construct without raising
@pytest.mark.parametrize("target", [
    ("192.168.1.1", 57400),
    ("192.168.1.1", "57400"),
    ("router.example.com", 57400),
    ("2001:db8::1", 57400),
    ("unix:/tmp/gnmi.sock", 57400),
    ("unix:/tmp/gnmi.sock", "not-a-port"),  # port ignored for unix sockets
    ["192.168.1.1", 57400],  # list is also accepted
])
def test_valid_target(target):
    gconn = gNMIclient(target=target, username="admin", password="admin", insecure=True)
    assert gconn is not None


# Tests: invalid targets should raise a clear gNMIException
def test_target_not_tuple_or_list():
    with pytest.raises(gNMIException):
        gNMIclient(target="192.168.1.1:57400", username="admin", password="admin", insecure=True)


def test_target_wrong_length():
    with pytest.raises(gNMIException):
        gNMIclient(target=("192.168.1.1",), username="admin", password="admin", insecure=True)

    with pytest.raises(gNMIException):
        gNMIclient(target=("192.168.1.1", 57400, "extra"), username="admin", password="admin", insecure=True)


def test_target_empty_host():
    with pytest.raises(gNMIException):
        gNMIclient(target=("", 57400), username="admin", password="admin", insecure=True)


def test_target_non_string_host():
    with pytest.raises(gNMIException):
        gNMIclient(target=(192, 57400), username="admin", password="admin", insecure=True)


def test_target_non_numeric_port():
    with pytest.raises(gNMIException):
        gNMIclient(target=("192.168.1.1", "not-a-port"), username="admin", password="admin", insecure=True)


def test_target_port_out_of_range():
    with pytest.raises(gNMIException):
        gNMIclient(target=("192.168.1.1", 0), username="admin", password="admin", insecure=True)

    with pytest.raises(gNMIException):
        gNMIclient(target=("192.168.1.1", 70000), username="admin", password="admin", insecure=True)


def test_target_boolean_port():
    with pytest.raises(gNMIException):
        gNMIclient(target=("192.168.1.1", True), username="admin", password="admin", insecure=True)
