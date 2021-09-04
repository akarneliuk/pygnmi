#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient
from dotenv import load_dotenv
import os


# User-defined functions (Tests)
def test_capabilities_connect_method():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    gc = gNMIclient(target=(hostname_str, port_str), username=username_str, password=password_str, path_cert=path_cert_str)
    gc.connect()

    result = gc.capabilities()

    gc.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result


def test_get_connect_method():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("CERT")

    gc = gNMIclient(target=(hostname_str, port_str), username=username_str, password=password_str, path_cert=path_cert_str)
    gc.connect()

    gc.capabilities()
    result = gc.get(path=["/"])

    gc.close()

    assert "notification" in result
    assert isinstance(result["notification"], list)
