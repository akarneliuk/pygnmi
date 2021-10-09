#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient
from dotenv import load_dotenv
import os


# User-defined functions (Tests)
def test_fqdn_address():
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


def test_ipv4_address_override():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST_2")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    gc = gNMIclient(target=(hostname_str, port_str), username=username_str, password=password_str, path_cert=path_cert_str, override="EOS425")
    gc.connect()

    result = gc.capabilities()

    gc.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result


def test_ipv4_address_certificate_download():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST_2")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    gc = gNMIclient(target=(hostname_str, port_str), username=username_str, password=password_str)
    gc.connect()

    result = gc.capabilities()

    gc.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result


def test_ipv6_address_override():
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST_3")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    gc = gNMIclient(target=(hostname_str, port_str), username=username_str, password=password_str, path_cert=path_cert_str, override="EOS425")
    gc.connect()

    result = gc.capabilities()

    gc.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result