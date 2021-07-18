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
                        'path': 'openconfig-interfaces:interfaces/interface[name=Ethernet1]',
                        'mode': 'sample',
                        'sample_interval': 10000000000,
                        'heartbeat_interval': 30000000000
                    }
                ], 
                'use_aliases': False, 
                'mode': 'stream', 
                'encoding': 'proto'}