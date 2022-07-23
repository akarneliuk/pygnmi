"""
Collection of unit tests to test various resolutions for connectivity to device
"""
# Modules
import os
from pygnmi.client import gNMIclient


# Statics
ENV_USERNAME = os.getenv("PYGNMI_USER")
ENV_PASSWORD = os.getenv("PYGNMI_PASS")
ENV_ADDRESS = os.getenv("PYGNMI_HOST")
ENV_HOSTNAME = os.getenv("PYGNMI_NAME")
ENV_PORT = os.getenv("PYGNMI_PORT")
ENV_PATH_CERT = os.getenv("PYGNMI_CERT")
ENV_FAKE_HOSTNAME = os.getenv("PYGNMI_FAKE_NAME")


# Tests
def test_ipv4_address():
    """
    Unit test: connectivity to gNMI speaking network function via IPv4 address
    """
    gconn = gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT)
    gconn.connect()

    result = gconn.capabilities()

    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_ipv4_address_override():
    """
    Unit test: connectivity to gNMI speaking network function via IPv4 address
    with overriding CN in certificate
    """
    gconn = gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT,
                       override=ENV_HOSTNAME)
    gconn.connect()

    result = gconn.capabilities()

    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_ipv4_address_skip_verify():
    """
    Unit test: connectivity to gNMI speaking network function via IPv4 address
    with automatic certifacate name pick up from CN and SANs
    """
    gconn = gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT,
                       skip_verify=True)
    gconn.connect()

    result = gconn.capabilities()

    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_fqdn_address():
    """
    Unit test: connectivity to gNMI speaking network function with FQDN resolution
    """
    gconn = gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT)
    gconn.connect()
    result = gconn.capabilities()
    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_fqdn_address_override():
    """
    Unit test: connectivity to gNMI speaking network function with FQDN resolution
    with override for a specific value
    """
    gconn = gNMIclient(target=(ENV_FAKE_HOSTNAME, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT,
                       override=ENV_ADDRESS)
    gconn.connect()
    result = gconn.capabilities()
    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn


def test_fqdn_address_skip_verify():
    """
    Unit test: connectivity to gNMI speaking network function with FQDN resolution
    with automatic certifacate name pick up from CN and SANs
    """
    gconn = gNMIclient(target=(ENV_FAKE_HOSTNAME, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT,
                       skip_verify=True)
    gconn.connect()
    result = gconn.capabilities()
    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn
