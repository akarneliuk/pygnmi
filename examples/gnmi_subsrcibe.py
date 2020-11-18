#!/usr/bin/env python

# Modules 
from pygnmi.client import gNMIclient, telemetryParser

# Variables
host = ('fd17:625c:f037:2::100',6030)

## Subscribe request
subscribe = {
                'subscription': [
                    {
                        'path': 'openconfig-interfaces:interfaces/interface[name=Ethernet1]',
                        'mode': 'sample',
                        'sample_interval': 10000000000,
                        'heartbeat_interval': 30000000000
                    },
                                                    {
                        'path': 'openconfig-interfaces:interfaces/interface[name=Management1]',
                        'mode': 'sample',
                        'sample_interval': 10000000000,
                        'heartbeat_interval': 30000000000
                    }
                ],
                'use_aliases': False,
                'mode': 'stream',
                'encoding': 'proto'
            }

# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='aaa', password='aaa', insecure=True) as gc:
        response = gc.subscribe(subscribe=subscribe)

        for telemetry_entry in response:
            print(telemetryParser(telemetry_entry))
