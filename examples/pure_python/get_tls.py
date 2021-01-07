#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient
import json

host = ('10.127.60.177', '57400')

if __name__ == '__main__':
    with gNMIclient(target=host, username='test2', password='cisco123', path_cert='/ws/avpathak-bgl/BossHogg/openconfig/ems_BH_P2A4.pem', override='ems.cisco.com') as gc:
        raw_data = gc.get(path=['openconfig-interfaces:interfaces'], encoding='json_ietf')
        print(json.dumps(raw_data, sort_keys=True, indent=2))

        
