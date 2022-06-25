"""
Collection of unit tests to validate operation of diff function
"""
# Modules
import os
from pygnmi.client import gNMIclient


# Messages
import tests.messages as tm


# Statics
ENV_USERNAME = os.getenv("PYGNMI_USER")
ENV_PASSWORD = os.getenv("PYGNMI_PASS")
ENV_ADDRESS = os.getenv("PYGNMI_HOST")
ENV_HOSTNAME = os.getenv("PYGNMI_HOST")
ENV_PORT = os.getenv("PYGNMI_PORT")
ENV_PATH_CERT = os.getenv("PYGNMI_CERT")


# User-defined functions (Tests)
def test_compare_add(msg1: tuple = tm.test_compare_add_tuple):
    """
    Unit test: Validation of adding configuration
    """
    with gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    show_diff="get") as gconn:
        gconn.capabilities()

        # Test adding new interface
        result = gconn.set(update=[msg1])
        assert isinstance(result, tuple)
        assert isinstance(result[0], dict)
        assert isinstance(result[1], list)
        assert len(result[1]) > 0


def test_compare_change(msg1: tuple = tm.test_compare_change_tuple):
    """
    Unit test: Validation of configuration changes
    """
    with gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    show_diff="get") as gconn:
        gconn.capabilities()

        # Test change description
        result = gconn.set(update=[msg1])
        assert isinstance(result, tuple)
        assert isinstance(result[0], dict)
        assert isinstance(result[1], list)
        assert len(result[1]) > 0


def test_compare_remove(msg1: str = tm.test_compare_remove_path):
    """
    Unit test: Validation of configuration removal
    """
    with gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    show_diff="get") as gconn:
        gconn.capabilities()

        # Test remove IP from interface
        result = gconn.set(delete=[msg1])
        assert isinstance(result, tuple)
        assert isinstance(result[0], dict)
        assert isinstance(result[1], list)
        assert len(result[1]) > 0


def test_compare_add_print(msg1: tuple = tm.test_compare_add_tuple):
    """
    Unit test: Validation of configuration addition (print)
    """
    with gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    show_diff="print") as gconn:
        gconn.capabilities()

        # Test adding new interface
        result = gconn.set(update=[msg1])
        assert isinstance(result, dict)


def test_compare_change_print(msg1: tuple = tm.test_compare_change_tuple):
    """
    Unit test: Validation of configuration modification (print)
    """
    with gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    show_diff="print") as gconn:
        gconn.capabilities()

        # Test change description
        result = gconn.set(update=[msg1])
        assert isinstance(result, dict)


def test_compare_remove_print(msg1: str = tm.test_compare_remove_path):
    """
    Unit test: Validation of configuration removal (print)
    """
    with gNMIclient(target=(ENV_HOSTNAME, ENV_PORT),
                    username=ENV_USERNAME,
                    password=ENV_PASSWORD,
                    path_cert=ENV_PATH_CERT,
                    show_diff="print") as gconn:
        gconn.capabilities()

        # Test remove IP from interface
        result = gconn.set(delete=[msg1])
        assert isinstance(result, dict)
