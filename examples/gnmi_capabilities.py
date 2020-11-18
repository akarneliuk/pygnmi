#!/usr/bin/env python
#(c)2020, karneliuk.com

# Modules 
from pygnmi.client import gNMIclient

# Variables
host = ('fd17:625c:f037:2::100',6030)

# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='aaa', password='aaa', insecure=True) as gc:
        response = gc.capabilities()

    print(response)