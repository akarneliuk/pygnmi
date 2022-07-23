"""
Collection unit tests to test streaming functionality
"""

# Modules
import os
from pygnmi.client import gNMIclient


# Messages
from tests.messages import test_telemetry_dict, test_telemetry_dict_once, test_telemetry_dict_poll


# Statics
ENV_USERNAME = os.getenv("PYGNMI_USER")
ENV_PASSWORD = os.getenv("PYGNMI_PASS")
ENV_ADDRESS = os.getenv("PYGNMI_HOST")
ENV_HOSTNAME = os.getenv("PYGNMI_NAME")
ENV_PORT = os.getenv("PYGNMI_PORT")
ENV_PATH_CERT = os.getenv("PYGNMI_CERT")


# Tests
def test_telemetry_stream(subscribe1: dict = test_telemetry_dict):
    """
    Unit test: Testing Subscribe with steraming telemetry
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        telemetry_iterator = gconn.subscribe2(subscribe=subscribe1)
        telemetry_entry_item = telemetry_iterator.__next__()

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item

        telemetry_iterator.close()

    del gconn


def test_telemetry_once(subscribe1: dict = test_telemetry_dict_once):
    """
    Unit test: Testing Subscribe with once polling
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        telemetry_iterator = gconn.subscribe2(subscribe=subscribe1)
        telemetry_entry_item = telemetry_iterator.__next__()

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item

        telemetry_iterator.close()

    del gconn


def test_telemetry_poll(subscribe1: dict = test_telemetry_dict_poll):
    """
    Unit test: Testing Subscribe with once polling
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        telemetry_iterator = gconn.subscribe2(subscribe=subscribe1)
        telemetry_entry_item = telemetry_iterator.__next__()

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item

        telemetry_iterator.close()

    del gconn
