"""
Collection of unit tests to test change of cipher
"""
# Modules
import os
import grpc
from pygnmi.client import gNMIclient


# Statics
ENV_USERNAME = os.getenv("PYGNMI_USER")
ENV_PASSWORD = os.getenv("PYGNMI_PASS")
ENV_ADDRESS = os.getenv("PYGNMI_HOST")
ENV_HOSTNAME = os.getenv("PYGNMI_NAME")
ENV_PORT = os.getenv("PYGNMI_PORT_2")
ENV_PATH_CERT = os.getenv("PYGNMI_CERT")


# Tests
def test_cipher_change_on_failure():
    """
    Unit test to test authentication with token
    """
    gconn = gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                       username=ENV_USERNAME,
                       password=ENV_PASSWORD,
                       override=ENV_ADDRESS,
                       path_cert=ENV_PATH_CERT)

    cipher_value_1 = None
    cipher_value_2 = None

    os.environ["GRPC_SSL_CIPHER_SUITES"] = ""

    try:
        cipher_value_1 = os.getenv("GRPC_SSL_CIPHER_SUITES")
        gconn.connect()

    except grpc.FutureTimeoutError:
        cipher_value_2 = os.getenv("GRPC_SSL_CIPHER_SUITES")

    assert cipher_value_1 != cipher_value_2

    del gconn
