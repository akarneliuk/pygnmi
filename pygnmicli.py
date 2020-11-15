#!/usr/bin/env python
#(c)2020, Anton Karneliuk


# Modules
import sys
import logging
import json
import os


# Own modules
from pygnmi.arg_parser import NFData
from pygnmi.client import gNMIclient
from pygnmi.artefacts.messages import msg


# Variables
path_msg = 'artefacts/messages.json'
path_log = 'log/execution.log'


# Body
if __name__ == "__main__":
    # Setting logger
    if not os.path.exists(path_log.split('/')[0]):
        os.mkdir(path_log.split('/')[0])

    logging.basicConfig(filename=path_log, level=logging.INFO, format='%(asctime)s.%(msecs)03d+01:00,%(levelname)s,%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    logging.info('Starting application...')

    # Collecting inputs
    del sys.argv[0]
    DD = NFData(sys.argv, msg)

    # gNMI operation
#    try:
    with gNMIclient(DD.targets, username=DD.username, password=DD.password, 
                    to_print=DD.to_print, insecure=DD.insecure, path_cert=DD.certificate) as GC:
        result = None
        
        if DD.operation == 'capabilities':
            print(f'Doing {DD.operation} request to {DD.targets}...')
            result = GC.capabilities()

        elif DD.operation == 'get':
            print(f'Doing {DD.operation} request to {DD.targets}...')
            result = GC.get(DD.gnmi_path, datatype='all')

        elif DD.operation == 'set':
            print(f'Doing {DD.operation} request to {DD.targets}...')
            deletes = DD.gnmi_path if DD.gnmi_path else None
            updates = DD.update if DD.update else None
            replaces = DD.replace if DD.replace else None

            result = GC.set(delete=deletes, update=updates, replace=replaces)

        elif DD.operation == 'subscribe':
            poll = True
#            aliases = [('openconfig-interfaces:interfaces', '#interfaces'), ('openconfig-acl:acl', '#acl')]
            subscribe = {
                            'subscription': [
                                {
                                    'path': 'openconfig-interfaces:interfaces/interface[name=Ethernet1]',
                                    'mode': 'sample',
                                    'sample_interval': 10000000000,
                                    'heartbeat_interval': 30000000000
                                },
                                                                {
                                    'path': 'openconfig-interfaces:interfaces/interface[name=Management1]',
                                    'mode': 'sample',
                                    'sample_interval': 10000000000,
                                    'heartbeat_interval': 30000000000
                                }
                            ], 
                            'use_aliases': False, 
                            'mode': 'stream', 
                            'encoding': 'proto'}

            result = GC.subscribe(subscribe=subscribe)
            for ent in result:
                print(GC.telemetry_parser(ent))


        if result:
            print(result)

#    except:
#        logging.critical(f'The connectivity towards {DD.targets} cannot be established. The execution is terminated.')
#        sys.exit(1)


