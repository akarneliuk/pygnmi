"""This example shows how to authenticate against the device
using token instead of username/password"""
# Modules
from pygnmi.client import gNMIclient

# Variables
from inventory import hosts

# Body
if __name__ == "__main__":

    # Get Token
    with open("token.tok") as f:
        TOKEN = f.read().strip('\n')

    for host in hosts:
        with gNMIclient(target=(host["ip_address"], host["port"]),
                        token=TOKEN, skip_verify=False) as gc:

            result = gc.capabilities()

        print(f"{host['ip_address']}: {result}\n\n")
