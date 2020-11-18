#!/usr/bin/env python

# Modules 
from pygnmi.client import gNMIclient

# Variables
host = ('fd17:625c:f037:2::100',6030)

## Update call
update_message = []
vv1 = 'openconfig-interfaces:interfaces/interface[name=Loopback10]'
vv2 = {
                "name": "Loopback10",
                "config": {
                    "name": "Loopback10",
                    "enabled": True,
                    "type": "iana-if-type:softwareLoopback",
                    "description": "pygnmi-lo-10"
                },
                "subinterfaces": {
                    "subinterface": [
                        {
                            "index": 0,
                            "config": {
                                "index": 0,
                                "enabled": True
                            },
                            "openconfig-if-ip:ipv4": {
                                "addresses": {
                                    "address": [
                                        {
                                            "ip": "10.10.10.10",
                                            "config": {
                                                 "ip": "10.10.10.10",
                                                 "prefix-length": 32,
                                                 "addr-type": "PRIMARY"
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }

update_message.append((vv1, vv2))

vv3 = 'openconfig-interfaces:interfaces/interface[name=Loopback20]'
vv4 = {
                "name": "Loopback20",
                "config": {
                    "name": "Loopback20",
                    "enabled": True,
                    "type": "iana-if-type:softwareLoopback",
                    "description": "pygnmi-lo-20"
                },
                "subinterfaces": {
                    "subinterface": [
                        {
                            "index": 0,
                            "config": {
                                "index": 0,
                                "enabled": True
                            },
                            "openconfig-if-ip:ipv4": {
                                "addresses": {
                                    "address": [
                                        {
                                            "ip": "10.10.10.20",
                                            "config": {
                                                 "ip": "10.10.10.20",
                                                 "prefix-length": 32,
                                                 "addr-type": "PRIMARY"
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }

update_message.append((vv3, vv4))

## Replace
replace_message = []

vv5 = 'openconfig-interfaces:interfaces/interface[name=Ethernet1]'
vv6 = {
                "name": "Ethernet1",
                "config": {
                    "name": "Ethernet1",
                    "enabled": True, 
                    "type": "iana-if-type:ethernetCsmacd",
                    "description": "pygnmi-replace"
                },
                "subinterfaces": {
                    "subinterface": [
                        {
                            "index": 0,
                            "config": {
                                "index": 0,
                                "enabled": True
                            },
                            "openconfig-if-ip:ipv4": {
                                "addresses": {
                                    "address": [
                                        {
                                            "ip": "10.1.2.10",
                                            "config": {
                                                 "ip": "10.1.2.10",
                                                 "prefix-length": 31,
                                                 "addr-type": "PRIMARY"
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }

replace_message.append((vv5, vv6))


## Delete
delete_paths = ['openconfig-network-instance:network-instances/network-instance[name=default]/interfaces/interface[name=Loopback30]', 'openconfig-interfaces:interfaces/interface[name=Loopback30]']


# Body
if __name__ == '__main__':
    with gNMIclient(target=host, username='aaa', password='aaa', insecure=True) as gc:
        response = gc.set(update=update_message, replace=replace_message, delete=delete_paths)

    print(response)
