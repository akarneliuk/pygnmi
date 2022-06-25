test_set_update_tuple = (
                            "openconfig-interfaces:interfaces/interface[name=Loopback51]", 
                            {
                                "config": {
                                    "name": "Loopback51", 
                                    "type": "softwareLoopback", 
                                    "description": "pytest-update-test",
                                    "enabled": True
                                }
                            }
                        )

test_set_replace_tuple = (
                            "openconfig-interfaces:interfaces/interface[name=Loopback51]/config", 
                            {
                                "name": "Loopback51", 
                                "type": "softwareLoopback", 
                                "description": "pytest-replace-test",
                                "enabled": True
                            }
                        )

test_delete_second_str = "openconfig-network-instance:network-instances/network-instance[name=default]/interfaces/interface[id=Loopback51]"

test_telemetry_dict = {
                        'subscription': [
                            {
                                'path': '/interfaces/interface[name=Ethernet1]',
                                'mode': 'sample',
                                'sample_interval': 10000000000,
                                'heartbeat_interval': 30000000000
                            }
                        ],
                        'use_aliases': False,
                        'mode': 'stream',
                        'encoding': 'proto'
                      }

test_telemetry_dict_once = {
                            'subscription': [
                                {
                                    'path': '/interfaces/interface[name=Ethernet1]',
                                    'mode': 'sample',
                                    'sample_interval': 10000000000,
                                    'heartbeat_interval': 30000000000
                                }
                            ], 
                            'use_aliases': False, 
                            'mode': 'once', 
                            'encoding': 'proto'
                           }

test_compare_add_tuple = (
                                "openconfig-interfaces:interfaces/interface[name=Loopback51]", 
                                {
                                    "config": {
                                        "name": "Loopback51", 
                                        "type": "softwareLoopback", 
                                        "description": "pytest-update-test-22",
                                        "enabled": True
                                    },
                                    "subinterfaces": {
                                        "subinterface": [
                                            {
                                                "index": "0",
                                                "openconfig-if-ip:ipv4": {
                                                    "addresses": {
                                                        "address": [
                                                            {
                                                                "ip": "10.0.250.2",
                                                                "config": {
                                                                    "ip": "10.0.250.2",
                                                                    "prefix-length": "32",
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
                            )

test_compare_change_tuple = (
                                "openconfig-interfaces:interfaces/interface[name=Loopback51]", 
                                {
                                    "config": {
                                        "name": "Loopback51", 
                                        "type": "softwareLoopback", 
                                        "description": "pytest-update-test-33",
                                        "enabled": False
                                    }
                                }
                            )

test_compare_remove_path = "openconfig-interfaces:interfaces/interface[name=Loopback51]/subinterfaces/subinterface[index=0]/openconfig-if-ip:ipv4"