#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
import grpc
from bin.gnmi_pb2_grpc import *
from bin.gnmi_pb2 import *
import re
import sys
import json
import logging

# Own modules
from bin.PathGenerator import gnmi_path_generator


# Classes
class gNMIclient(object):
    """
    This class instantiates the object, which interacts with the network elements over gNMI.
    """
    def __init__(self, dev_data):
        self.__metadata = [('username', dev_data.username), ('password', dev_data.password)]
        self.__targets = dev_data.targets
        self.__op = dev_data.operation
        self.__insecure = dev_data.insecure


    def connect(self, path_cert=None):
        for he in self.__targets:
            if self.__insecure:
                channel = grpc.insecure_channel(f'{he[0]}:{he[1]}', self.__metadata)
                grpc.channel_ready_future(channel).result(timeout=5)
                self.__stub = gNMIStub(channel)

            else:
                if path_cert:
                    try:
                        with open(path_cert, 'rb') as f:
                            cert = grpc.ssl_channel_credentials(f.read())

                    except:
                        logging.error('The SSL certificate cannot be opened.')
                        sys.exit(10)

                channel = grpc.secure_channel(f'{he[0]}:{he[1]}', credentials=cert)
                grpc.channel_ready_future(channel).result(timeout=5)
                self.__stub = gNMIStub(channel)


    def capabilities(self):
        gnmi_message_request = CapabilityRequest()
        print(gnmi_message_request)
        gnmi_message_response = self.__stub.Capabilities(gnmi_message_request, metadata=self.__metadata)

        if gnmi_message_response:
            response = {}
            
            if gnmi_message_response.supported_models:
                response.update({'supported_models': []})

                for ree in gnmi_message_response.supported_models:
                    response['supported_models'].append({'name': ree.name, 'organization': ree.organization, 'version': ree.version})

            if gnmi_message_response.supported_encodings:
                response.update({'supported_encodings': []})

                for ree in gnmi_message_response.supported_encodings:
                    response['supported_encodings'].append(ree)

            if gnmi_message_response.gNMI_version:
                response.update({'gnmi_version': gnmi_message_response.gNMI_version})

        return response