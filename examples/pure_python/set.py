#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient

# Variables
from inventory import hosts
from messages import *

# Body
if __name__ == "__main__":
    for host in hosts:
        with gNMIclient(target=(host["ip_address"], host["port"]), username=host["username"],
                        password=host["password"], insecure=True) as gc:

            if host["nos"] == "arista-eos":
                m = arista_update
                d = arista_delete
            elif host["nos"] == "nokia-sros":
                m = nokia_update
                d = nokia_delete                

            result = gc.set(update=m, encoding='json_ietf')

        print(f"{host['ip_address']}: {result}\n\n")