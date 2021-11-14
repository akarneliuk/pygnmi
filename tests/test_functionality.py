#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient, telemetryParser
from dotenv import load_dotenv
import os


# Messages
from tests.messages import test_set_update_tuple, test_set_replace_tuple, test_delete_second_str, test_telemetry_dict


# User-defined functions (Tests)
def test_capabilities():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        result = gc.capabilities()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result


def test_connectivity_custom_keepalive():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, keepalive_time_ms=1000) as gc:
        result = gc.capabilities()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result


def test_get_signle_path_all_path_formats():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        # Default GNMI path
        result = gc.get(path=["/"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "yang-model:top_element" GNMI path notation
        result = gc.get(path=["openconfig-interfaces:interfaces"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # "yang-model:top_element/next_element" GNMI path notation
        result = gc.get(path=["openconfig-interfaces:interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/yang-model:top_element/next_element" GNMI path notation
        result = gc.get(path=["/openconfig-interfaces:interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/yang-model:/top_element/next_element" GNMI path notation
        result = gc.get(path=["/openconfig-interfaces:/interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "top_element" GNMI path notation
        result = gc.get(path=["interfaces"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # "top_element/next_element" GNMI path notation
        result = gc.get(path=["interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0

        # "/top_element/next_element" GNMI path notation
        result = gc.get(path=["/interfaces/interface"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 1
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) > 0


def test_get_prefix_and_path():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        # Default GNMI path
        result = gc.get(prefix="/")
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
        result = gc.get(prefix="openconfig-interfaces:interfaces")
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
        result = gc.get(prefix="openconfig-interfaces:interfaces", path=["interface"])
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
        result = gc.get(prefix="/openconfig-interfaces:interfaces", path=["interface[name=Management1]"])
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


def test_get_multiple_paths():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        # Two paths
        result = gc.get(path=["/openconfig-interfaces:interfaces", "/openconfig-network-instance:network-instances"])
        assert "notification" in result
        assert isinstance(result["notification"], list)
        assert len(result["notification"]) == 2
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1
        assert "update" in result["notification"][1]
        assert isinstance(result["notification"][1]["update"], list)
        assert len(result["notification"][1]["update"]) == 1


def test_set_update(msg1: tuple = test_set_update_tuple):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        # Pre-change state
        result = gc.get(path=[msg1[0]])
        assert not "update" in result["notification"][0]

        # Set update
        result = gc.set(update=[msg1])
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
        result = gc.get(path=[msg1[0]])
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1


def test_set_replace(msg1: tuple = test_set_update_tuple, msg2: tuple = test_set_replace_tuple):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        # Pre-change state
        result = gc.get(path=[msg1[0]])
        assert "path" in result["notification"][0]["update"][0]
        assert result["notification"][0]["update"][0]["path"] in msg1[0]
        assert "val" in result["notification"][0]["update"][0]
        assert "openconfig-interfaces:config" in result["notification"][0]["update"][0]["val"]
        assert "description" in result["notification"][0]["update"][0]["val"]["openconfig-interfaces:config"]
        assert result["notification"][0]["update"][0]["val"]["openconfig-interfaces:config"]["description"] == msg1[1]["config"]["description"]

        # Set replace
        result = gc.set(replace=[msg2])
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
        result = gc.get(path=[msg2[0]])
        assert "path" in result["notification"][0]["update"][0]
        assert result["notification"][0]["update"][0]["path"] in msg2[0]
        assert "val" in result["notification"][0]["update"][0]
        assert "openconfig-interfaces:description" in result["notification"][0]["update"][0]["val"]
        assert result["notification"][0]["update"][0]["val"]["openconfig-interfaces:description"] == msg2[1]["description"]


def test_set_delete(msg1: tuple = test_set_update_tuple, path2: str = test_delete_second_str):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        # Pre-change state
        result = gc.get(path=[msg1[0]])
        assert "update" in result["notification"][0]
        assert isinstance(result["notification"][0]["update"], list)
        assert len(result["notification"][0]["update"]) == 1

        # Set delete
        result = gc.set(delete=[path2, msg1[0]])
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


def test_telemetry(subscribe1: dict = test_telemetry_dict):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        telemetry_iterator = gc.subscribe(subscribe=subscribe1)

        telemetry_entry_item = telemetryParser(telemetry_iterator.__next__())

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item