"""This example shows how to use the History extension
with range option

Per GNMI spec, /extension/history/range requires 
`STREAM` mode of telemetery subscription"""
# Modules
from pygnmi.client import gNMIclient


# Variables
TELEMETRY_REQUEST2 = {
                        'subscription': [
                            {
                                'path': 'openconfig:/interfaces/interface/state/counters',
                                'mode': 'target_defined'
                            }
                        ],
                        'mode': 'stream',
                        'encoding': 'proto'
                    }

EXTENSION2 = {
                'history': {
                    'range': {
                        'start': '2022-07-23T09:47:00Z',
                        'end': '2022-07-24T8:57:00Z'
                    }
                }
            }


# Body
with open("token.tok") as f:
    TOKEN = f.read().strip('\n')

with gNMIclient(target=('192.168.0.5', '443'), token=TOKEN, skip_verify=True) as gconn:
    for item in gconn.subscribe2(subscribe=TELEMETRY_REQUEST2, target="leaf1", extension=EXTENSION2):
        print(item)