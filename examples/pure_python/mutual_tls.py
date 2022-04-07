#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient
import json

host = ('10.127.60.177', '57400')

if __name__ == '__main__':
    # The override should match a SAN in the server side certificate.
    with gNMIclient(target=host, path_root='/Users/someuser/certs/ca.crt', path_key='/Users/someuser/certs/client.key', 
                    path_cert='/Users/someuser/certs/client.crt', override='10.10.10.10') as gc:
        raw_data = gc.get(path=['openconfig-interfaces:interfaces'], encoding='json_ietf')
        print(json.dumps(raw_data, sort_keys=True, indent=2))

        
