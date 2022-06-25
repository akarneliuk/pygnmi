"""
Collection unit tests to test pygnmi functionality
"""

# Modules
import os
from pygnmi.client import gNMIclient, telemetryParser

# Messages
from tests.messages import test_set_update_tuple, test_set_replace_tuple,\
                           test_delete_second_str, test_telemetry_dict


# Statics
ENV_USERNAME = os.getenv("PYGNMI_USER")
ENV_PASSWORD = os.getenv("PYGNMI_PASS")
ENV_ADDRESS = os.getenv("PYGNMI_HOST")
ENV_HOSTNAME = os.getenv("PYGNMI_NAME")
ENV_PORT = os.getenv("PYGNMI_PORT")
ENV_PATH_CERT = os.getenv("PYGNMI_CERT")


# Tests
def test_capabilities():
    """
    Unit test: Testing Capabilities with with/as context manager
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        result = gconn.capabilities()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_connectivity_custom_keepalive():
    """
    Unit test: Testing Capabilities with with/as context manager and custom keepalive
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    keepalive_time_ms=1000) as gconn:
        result = gconn.capabilities()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_get_signle_path_all_path_formats():
    """
    Unit test: Testing Get with multiple path formats
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        # Default GNMI path
        result = gconn.get(path=["/"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "yang-model:top_element" GNMI path notation
        result = gconn.get(path=["openconfig-interfaces:interfaces"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # "yang-model:top_element/next_element" GNMI path notation
        result = gconn.get(path=["openconfig-interfaces:interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/yang-model:top_element/next_element" GNMI path notation
        result = gconn.get(path=["/openconfig-interfaces:interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/yang-model:/top_element/next_element" GNMI path notation
        result = gconn.get(path=["/openconfig-interfaces:/interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "top_element" GNMI path notation
        result = gconn.get(path=["interfaces"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # "top_element/next_element" GNMI path notation
        result = gconn.get(path=["interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/top_element/next_element" GNMI path notation
        result = gconn.get(path=["/interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

    del gconn


def test_get_prefix_and_path():
    """
    Unit test: Testing Get with using Prefix and Path
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        # Default GNMI path
        result = gconn.get(prefix="/")
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert "timestamp" in result["notification"][0]
        assert "prefix" in result["notification"][0]
        assert "alias" in result["notification"][0]
        assert "atomic" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "yang-model:top_element" GNMI path notation
        result = gconn.get(prefix="openconfig-interfaces:interfaces")
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert "timestamp" in result["notification"][0]
        assert "prefix" in result["notification"][0]
        assert "alias" in result["notification"][0]
        assert "atomic" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # "yang-model:top_element/next_element" GNMI path notation
        result = gconn.get(prefix="openconfig-interfaces:interfaces",
                           path=["interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert "timestamp" in result["notification"][0]
        assert "prefix" in result["notification"][0]
        assert "alias" in result["notification"][0]
        assert "atomic" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/yang-model:top_element/next_element" GNMI path notation
        result = gconn.get(prefix="/openconfig-interfaces:interfaces",
                           path=["interface[name=Management1]"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert "timestamp" in result["notification"][0]
        assert "prefix" in result["notification"][0]
        assert "alias" in result["notification"][0]
        assert "atomic" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

    del gconn


def test_get_multiple_paths():
    """
    Unit test: Testing Get with multiple path arguments in one collection
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        # Two paths
        result = gconn.get(path=["/openconfig-interfaces:interfaces",
                                 "/openconfig-network-instance:network-instances"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 2
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1
        assert "update" in result["notification"][1]
        assert isinstance(result["notification"][1]["update"], list)
        assert len(result["notification"][1]["update"]) == 1

    del gconn


def test_set_update(msg1: tuple = test_set_update_tuple):
    """
    Unit test: Testing Set/Update RPC
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        # Pre-change state
        result = gconn.get(path=[msg1[0]])
        assert isinstance(result, dict)
        assert isinstance(result["notification"], list)

        # Set update
        result = gconn.set(update=[msg1])
        assert "response" in result
        assert "timestamp" in result
        assert "prefix" in result
        assert isinstance(result["response"], list)
        assert len(result["response"]) == 1
        assert "op" in result["response"][0]
        assert result["response"][0]["op"] == "UPDATE"
        assert "path" in result["response"][0]
        assert result["response"][0]["path"] in msg1[0]

        # Post-change state
        result = gconn.get(path=[msg1[0]])
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

    del gconn


def test_set_replace(msg1: tuple = test_set_update_tuple, msg2: tuple = test_set_replace_tuple):
    """
    Unit test: Testing Set/Replace RPC
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        # Pre-change state
        result = gconn.get(path=[msg1[0]])
        assert "path" in result["notification"][0]["update"][0]
        assert result["notification"][0]["update"][0]["path"] in msg1[0]
        assert "val" in result["notification"][0]["update"][0]
        assert "openconfig-interfaces:config" in result["notification"][0]["update"][0]["val"]
        assert "description" in result["notification"][0]["update"][0]["val"]["openconfig-interfaces:config"]
        assert result["notification"][0]["update"][0]["val"]["openconfig-interfaces:config"]["description"] == msg1[1]["config"]["description"]

        # Set replace
        result = gconn.set(replace=[msg2])
        assert "response" in result
        assert "timestamp" in result
        assert "prefix" in result
        assert isinstance(result["response"], list)
        assert len(result["response"]) == 1
        assert "op" in result["response"][0]
        assert result["response"][0]["op"] == "REPLACE"
        assert "path" in result["response"][0]
        assert result["response"][0]["path"] in msg2[0]

        # Post-change state
        result = gconn.get(path=[msg2[0]])
        assert "path" in result["notification"][0]["update"][0]
        assert result["notification"][0]["update"][0]["path"] in msg2[0]
        assert "val" in result["notification"][0]["update"][0]
        assert "openconfig-interfaces:description" in result["notification"][0]["update"][0]["val"]
        assert result["notification"][0]["update"][0]["val"]["openconfig-interfaces:description"] == msg2[1]["description"]

    del gconn


def test_set_delete(msg1: tuple = test_set_update_tuple, path2: str = test_delete_second_str):
    """
    Unit test: Testing Set/Delete RPC
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        # Pre-change state
        result = gconn.get(path=[msg1[0]])
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # Set delete
        result = gconn.set(delete=[path2, msg1[0]])
        assert "response" in result
        assert "timestamp" in result
        assert "prefix" in result
        assert isinstance(result["response"], list)
        assert len(result["response"]) == 2
        assert "op" in result["response"][0]
        assert result["response"][0]["op"] == "DELETE"
        assert "path" in result["response"][0]
        assert result["response"][0]["path"] in path2
        assert "op" in result["response"][1]
        assert result["response"][1]["op"] == "DELETE"
        assert "path" in result["response"][0]
        assert result["response"][1]["path"] in msg1[0]

    del gconn


def test_telemetry(subscribe1: dict = test_telemetry_dict):
    """
    Unit test: Testing Subscribe RPC
    """
    with gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT) as gconn:
        gconn.capabilities()

        telemetry_iterator = gconn.subscribe(subscribe=subscribe1)
        telemetry_entry_item = telemetryParser(telemetry_iterator.__next__())

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item

    del gconn
