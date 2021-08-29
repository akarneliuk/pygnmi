#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient, telemetryParser

# Variables
from inventory import hosts

# Body
for host_entry in hosts:
    if host_entry["nos"] == "nokia-sros":
        subscribe = {
            'subscription': [
                {
                    'path': 'openconfig-interfaces:interfaces/interface[name=1/1/c1/1]',
                    'mode': 'sample',
                    'sample_interval': 10000000000
                },
                {
                    'path': 'openconfig-network-instance:network-instances/network-instance[name=Base]/interfaces/interface[id=1/1/c1/1.0]',
                    'mode': 'sample',
                    'sample_interval': 10000000000
                }
            ],
            'use_aliases': False,
            'mode': 'stream',
            'encoding': 'json'
        }

        with gNMIclient(target=(host_entry["ip_address"], host_entry["port"]),
                        username=host_entry["username"], password=host_entry["password"], insecure=True) as gc:

            telemetry_stream = gc.subscribe_stream(subscribe=subscribe)

            for telemetry_entry in telemetry_stream:
                print(telemetry_entry)
