#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient, telemetryParser
from dotenv import load_dotenv
import os


# Messages
from tests.messages import *


# User-defined functions (Tests)
def test_compare_add(msg1: tuple = test_compare_add_tuple):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, show_diff="get") as gc:
        gc.capabilities()

        # Test adding new interface
        result = gc.set(update=[msg1])
        assert type(result) == tuple
        assert type(result[0]) == dict
        assert type(result[1]) == list
        assert len(result[1]) > 0


def test_compare_change(msg1: tuple = test_compare_change_tuple):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, show_diff="get") as gc:
        gc.capabilities()

        # Test change description
        result = gc.set(update=[msg1])
        assert type(result) == tuple
        assert type(result[0]) == dict
        assert type(result[1]) == list
        assert len(result[1]) > 0


def test_compare_remove(msg1: str = test_compare_remove_path):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, show_diff="get") as gc:
        gc.capabilities()

        # Test remove IP from interface
        result = gc.set(delete=[msg1])
        assert type(result) == tuple
        assert type(result[0]) == dict
        assert type(result[1]) == list
        assert len(result[1]) > 0


def test_compare_add_print(msg1: tuple = test_compare_add_tuple):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, show_diff="print") as gc:
        gc.capabilities()

        # Test adding new interface
        result = gc.set(update=[msg1])
        assert type(result) == dict


def test_compare_change_print(msg1: tuple = test_compare_change_tuple):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, show_diff="print") as gc:
        gc.capabilities()

        # Test change description
        result = gc.set(update=[msg1])
        assert type(result) == dict


def test_compare_remove_print(msg1: str = test_compare_remove_path):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str, show_diff="print") as gc:
        gc.capabilities()

        # Test remove IP from interface
        result = gc.set(delete=[msg1])
        assert type(result) == dict