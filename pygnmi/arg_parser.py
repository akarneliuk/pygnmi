#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
import re
from getpass import getpass
import logging
import sys

# Classes
class NFData(object):
    """
    This object stores the prameters related to the specific network element.
    It includes credentials, IP, port, operation type, path and JSON object, and others.
    """

    def __init__(self, input_vars, msg):
        allowed_operations = {'capabilities', 'set', 'get', 'subscribe'}

        self.username = False
        self.password = False
        self.targets = None
        self.insecure = False
        self.certificate = None
        self.operation = False
        self.gnmi_path = None
        self.to_print = False
        self.update = None
        self.replace = None

        ind = 0
        while ind < len(input_vars):
            if re.match('^-', input_vars[ind]):
                if input_vars[ind] == '-u' or input_vars[ind] == '--user':
                    try:
                        self.username = str(input_vars[ind + 1])
                        ind += 2

                    except IndexError:
                        print(msg['not_enough_arg'])
                        logging.critical(msg['not_enough_arg'])
                        sys.exit(3)

                elif input_vars[ind] == '-p' or input_vars[ind] == '--pass':
                    try:
                        self.password = str(input_vars[ind + 1])
                        ind += 2

                    except IndexError:
                        print(msg['not_enough_arg'])
                        logging.critical(msg['not_enough_arg'])
                        sys.exit(3)

                elif input_vars[ind] == '-t' or input_vars[ind] == '--target':
                    try:
                        if re.match('\[.*\]', input_vars[ind + 1]):
                            self.targets = re.sub('^\[([0-9a-f:]+?)\]:(\d+?)$', '\g<1> \g<2>', input_vars[ind + 1]).split(' ')

                        else:
                            self.targets = (str(input_vars[ind + 1].split(':')[0]), int(input_vars[ind + 1].split(':')[1]))

                        ind += 2

                    except IndexError:
                        print(msg['bad_host'])
                        logging.error(msg['bad_host'])
                        sys.exit(2)

                    except ValueError:
                        print(msg['wrong_data'])
                        logging.error(msg['wrong_data'])
                        sys.exit(2)


                elif input_vars[ind] == '-o' or input_vars[ind] == '--operation':
                    try:
                        self.operation = str(input_vars[ind + 1]).lower()

                        if self.operation not in allowed_operations:
                            print(msg['not_allowed_op'])
                            logging.critical(msg['not_allowed_op'])
                            sys.exit(2)                            

                        ind += 2

                    except IndexError:
                        print(msg['not_enough_arg'])
                        logging.critical(msg['not_enough_arg'])
                        sys.exit(3)

                elif input_vars[ind] == '-c' or input_vars[ind] == '--cert':
                    try:
                        self.certificate = str(input_vars[ind + 1])
                        ind += 2

                    except IndexError:
                        print(msg['not_enough_arg'])
                        logging.critical(msg['not_enough_arg'])
                        sys.exit(3)

                elif input_vars[ind] == '--insecure':
                    self.insecure = True
                    ind += 1

                elif input_vars[ind] == '--print':
                    self.to_print = True
                    ind += 1

                elif input_vars[ind] == '--gnmi-path':
                    try:
                        paths = input_vars[ind + 1].split(',')
                        try:
                            self.gnmi_path = [str(path) for path in paths]

                        except IndexError:
                            print(msg['bad_host'])
                            logging.error(msg['bad_host'])
                            sys.exit(2)

                        except ValueError:
                            print(msg['wrong_data'])
                            logging.error(msg['wrong_data'])
                            sys.exit(2)

                        ind += 2

                    except IndexError:
                        print(msg['not_enough_arg'])
                        logging.critical(msg['not_enough_arg'])
                        sys.exit(3)

                elif input_vars[ind] == '-h' or input_vars[ind] == '--help':
                    print(msg['help'])
                    logging.info(f'Help is triggered. The execution is terminated.')
                    sys.exit(2)

                else:
                    print(msg['unknown_arg'])
                    logging.error(msg['unknown_arg'])
                    sys.exit(2)

            else:
                print(f'Key {input_vars[ind]} is malformed. It must start with "-" or "--".')
                sys.exit(2)

        if not self.username:
            print(msg['not_defined_user'])
            logging.critical(msg['not_defined_user'])
            sys.exit(3)

        if not self.password:
            print(msg['not_defined_pass'])
            logging.warning(msg['not_defined_pass'])
            self.password = str(getpass('gRPC password:'))

        if not self.targets:
            print(msg['not_defined_target'])
            logging.critical(msg['not_defined_target'])
            sys.exit(3)
        
        if not self.operation:
            print(msg['not_defined_op'])
            logging.critical(msg['not_defined_op'])
            sys.exit(3)

        if not self.gnmi_path and (self.operation == 'get' or self.operation == 'set'):
            print(msg['not_defined_path'])
            logging.critical(msg['not_defined_path'])
            sys.exit(3)

        if self.operation == 'set' and not (self.update or self.gnmi_path or self.replace):
            print(msg['not_defined_set'])
            logging.critical(msg['not_defined_set'])
            sys.exit(3)