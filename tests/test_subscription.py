#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient, telemetryParser
from dotenv import load_dotenv
import os


# Messages
from tests.messages import test_set_update_tuple, test_set_replace_tuple, test_delete_second_str, test_telemetry_dict, test_telemetry_dict_once


# User-defined functions (Tests)
def test_telemetry_stream(subscribe1: dict = test_telemetry_dict):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        telemetry_iterator = gc.subscribe2(subscribe=subscribe1)
        telemetry_entry_item = telemetry_iterator.__next__()

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item

        telemetry_iterator.close()


def test_telemetry_once(subscribe1: dict = test_telemetry_dict_once):
    load_dotenv()
    username_str = os.getenv("PYGNMI_USER")
    password_str = os.getenv("PYGNMI_PASS")
    hostname_str = os.getenv("PYGNMI_HOST")
    port_str = os.getenv("PYGNMI_PORT")
    path_cert_str = os.getenv("PYGNMI_CERT")

    with gNMIclient(target=(hostname_str, port_str), username=username_str, 
                    password=password_str, path_cert=path_cert_str) as gc:
        gc.capabilities()

        telemetry_iterator = gc.subscribe2(subscribe=subscribe1)
        telemetry_entry_item = telemetry_iterator.__next__()

        assert "update" in telemetry_entry_item or "sync_response" in telemetry_entry_item

        telemetry_iterator.close()