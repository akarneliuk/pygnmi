"""
Collection of unit tests to test various authentication methods
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
def test_authentication_token():
    """
    Unit test to test authentication with token
    """
    gconn = gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       token="ABC")
    gconn.connect()

    result = gconn.capabilities()

    gconn.close()

    assert "supported_models" in result
    assert "supported_encodings" in result
    assert "gnmi_version" in result

    del gconn
