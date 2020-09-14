#!/usr/bin/env python
#(c)2020, Anton Karneliuk


# Modules
import sys
import logging
import json
import os


# Own modules
from bin.ArgParser import NFData
from bin.GnmiClient import gNMIclient

# Variables
__version__ = '0.1.0'
path_msg = 'artefacts/messages.json'
path_log = 'log/execution.log'


# Body
if __name__ == "__main__":
    # Setting logger
    if not os.path.exists(path_log.split('/')[0]):
        os.mkdir(path_log.split('/')[0])

    logging.basicConfig(filename=path_log, level=logging.INFO, format='%(asctime)s.%(msecs)03d+01:00,%(levelname)s,%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    logging.info('Starting application...')

    # Importing messages
    try:
        with open(path_msg, 'r') as f:
            msg = json.loads(f.read())

    except:
        print(f'Can\'t import messages. Execution is terminated')
        logging.error(f'Can\'t import messages. Execution is terminated')

    # Collecting inputs
    del sys.argv[0]
    DD = NFData(sys.argv, msg)

    # gNMI operations
    GC = gNMIclient(DD)
    try:
        GC.connect(DD.certificate)

    except:
        logging.critical(f'The connectivity towards {DD.targerts} cannot be established. The execution is terminated.')
        sys.exit(1)

    if DD.operation == 'capabilities':
        result = GC.capabilities()
        print(result)
