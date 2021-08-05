#!/usr/bin env python

# Modules
from pygnmi.client import gNMIclient

# Variables
host = ('192.168.56.31',50051)

# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='admin', password='admin1', insecure=False) as gc:
        response = gc.capabilities()

    print(response)