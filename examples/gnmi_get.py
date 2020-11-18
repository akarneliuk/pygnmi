#!/usr/bin/env python

# Modules 
from pygnmi.client import gNMIclient

# Variables
host = ('fd17:625c:f037:2::100',6030)

path = ['openconfig-network-instance:network-instances/network-instance[name=default]/interfaces/interface[name=Ethernet1]', 'openconfig-interfaces:interfaces/interface[name=Ethernet1]']
datatype = 'all'

# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='aaa', password='aaa', insecure=True) as gc:
        response = gc.get(path=path, datatype=datatype)

    print(response)
