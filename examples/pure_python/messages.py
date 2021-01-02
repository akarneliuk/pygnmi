# Nokia messages
nokia_update = [
    (
        "openconfig-interfaces:interfaces/interface[name=1/1/c1/2]",
        {
            "config": {
                "name": "1/1/c1/2",
                "enabled": True,
                "type": "ethernetCsmacd",
                "description": "Test Interface @ pygnmi"
            },
            "subinterfaces":{
                "subinterface": [
                    {
                        "index": 0,
                        "config": {
                            "index": 0,
                            "enabled": True
                        },
                        "ipv4": {
                            "addresses": {
                                "address": [
                                    {
                                        "ip": "10.0.1.1",
                                        "config": {
                                            "ip": "10.0.1.1",
                                            "prefix-length": 31
                                        }
                                    }
                                ]
                            }
                        },
                        "ipv6": {
                            "addresses": {
                                "address": [
                                    {
                                        "ip": "fc00:10:0:1::1",
                                        "config": {
                                            "ip": "fc00:10:0:1::1",
                                            "prefix-length": 64
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    ),
    (
        "openconfig-network-instance:network-instances/network-instance[name=Base]/interfaces/interface[id=1/1/c1/2.0]",
        {
            "config": {
                "id": "1/1/c1/2.0",
                "interface": "1/1/c1/2",
                "subinterface": 0,
                "associated-address-families": ["IPV4", "IPV6"]
            }
        }
    )
]

nokia_delete = [
                    "openconfig-network-instance:network-instances/network-instance[name=Base]/interfaces/interface[id=1/1/c1/2.0]", 
                    "openconfig-interfaces:interfaces/interface[name=1/1/c1/2]"
               ]

subscribe = {
    'subscription': [
        {
            'path': 'openconfig-interfaces:interfaces/interface[name=1/1/c1/1]',
            'mode': 'sample',
            'sample_interval': 10000000000
        },
        {
            'path': 'openconfig-network-instance:network-instances/network-instance[name=Base]/interfaces/interface[id=1/1/c1/1.0]',
            'mode': 'sample',
            'sample_interval': 10000000000
        }
    ],
    'mode': 'stream',
    'encoding': 'json'
}

# Arista messages
arista_update = [
    (
        "openconfig-interfaces:interfaces/interface[name=Loopback0]",
        {
            "config": {
                "name": "Loopback0",
                "enabled": True,
                "type": "softwareLoopback",
                "description": "Test Interface @ pygnmi"
            },
            "subinterfaces":{
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
                                        "ip": "10.0.255.1",
                                        "config": {
                                            "ip": "10.0.255.1",
                                            "arista-intf-augments:addr-type": "PRIMARY",
                                            "prefix-length": 32
                                        }
                                    }
                                ]
                            }
                        },
                        "openconfig-if-ip:ipv6": {
                            "addresses": {
                                "address": [
                                    {
                                        "ip": "fc00:10:0:255::1",
                                        "config": {
                                            "ip": "fc00:10:0:255::1",
                                            "prefix-length": 128
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    )
]

arista_delete = [
                    "openconfig-network-instance:network-instances/network-instance[name=default]/interfaces/interface[id=Loopback0]", 
                    "openconfig-interfaces:interfaces/interface[name=Loopback0]"
                ]

arista_subscribe = {
    'subscription': [
        {
            'path': 'openconfig-interfaces:interfaces/interface[name=Ethernet1]',
            'mode': 'sample',
            'sample_interval': 10000000000
        },
                                        {
            'path': 'openconfig-interfaces:interfaces/interface[name=Management1]',
            'mode': 'sample',
            'sample_interval': 10000000000
        }
    ],
    'use_aliases': False,
    'mode': 'stream',
    'encoding': 'proto'
}