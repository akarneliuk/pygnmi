#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient

# Variables
from inventory import hosts

# Body
if __name__ == "__main__":

    for host in hosts:
        with gNMIclient(target=(host["ip_address"], host["port"]), username=host["username"],
                        password=host["password"], insecure=True) as gc:

            result = gc.capabilities()

        print(f"{host['ip_address']}: {result}\n\n")