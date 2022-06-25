"""
Collection of unit tests to test Capabilities() and Get() RPCs
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


# Tests
def test_capabilities_connect_method():
    """
    Unit test: test Capabilities() RPCs
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


def test_get_connect_method():
    """
    Unit test: test Get() RPC
    """
    gconn = gNMIclient(target=(ENV_ADDRESS, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       path_cert=ENV_PATH_CERT)
    gconn.connect()

    gconn.capabilities()
    result = gconn.get(path=["/"])

    gconn.close()

    assert "notification" in result
    assert isinstance(result["notification"], list)

    del gconn
