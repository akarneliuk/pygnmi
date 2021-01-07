
#!/usr/bin/env python

# Modules 
from pygnmi.client import gNMIclient, telemetryParser
# import json
import pprint
# Variables
host = ('10.127.60.177', '57400')

## Subscribe request
subscribe = {
                'subscription': [
                    {
                        'path': 'openconfig-interfaces:interfaces/interface/state',
                        'mode': 'sample',
                        'sample_interval': 10000000000
                    }
                ],
                'use_aliases': False,
                'mode': 'once',
                'encoding': 'proto'
            }

# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='test2', password='cisco123', path_cert='/ws/avpathak-bgl/BossHogg/openconfig/ems_BH_P2A4.pem',server='ems.cisco.com') as gc:
        response = gc.subscribe(subscribe=subscribe)

        for telemetry_entry in response:
            raw_data = telemetryParser(telemetry_entry)
            #print(json.dumps(raw_data, sort_keys=True, indent=4))
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(raw_data)
