#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
import grpc
from bin.gnmi_pb2_grpc import gNMIStub
from bin.gnmi_pb2 import CapabilityRequest, GetRequest, SetRequest
import re
import sys
import json
import logging


# Own modules
from path_generator import gnmi_path_generator


# Classes
class gNMIclient(object):
    """
    This class instantiates the object, which interacts with the network elements over gNMI.
    """
    def __init__(self, target, username=None, password=None, to_print=False, insecure=False, path_cert=None):
        """
        Initializing the object
        """
        self.__metadata = [('username', username), ('password', password)]
        self.__target = target
        self.__capabilities = None
        self.__to_print = to_print
        self.__insecure = insecure
        self.__path_cert = path_cert

    
    def __enter__(self):
        """
        Building the connectivity towards network element over gNMI
        """
        if self.__insecure:
            self.__channel = grpc.insecure_channel(f'{self.__target[0]}:{self.__target[1]}', self.__metadata)
            grpc.channel_ready_future(self.__channel).result(timeout=5)
            self.__stub = gNMIStub(self.__channel)

        else:
            if self.__path_cert:
                try:
                    with open(self.__path_cert, 'rb') as f:
                        cert = grpc.ssl_channel_credentials(f.read())

                except:
                    logging.error('The SSL certificate cannot be opened.')
                    sys.exit(10)

            self.__channel = grpc.secure_channel(f'{self.__target[0]}:{self.__target[1]}', cert)
            grpc.channel_ready_future(self.__channel).result(timeout=5)
            self.__stub = gNMIStub(self.__channel)

        return self


    def capabilities(self):
        """
        Collecting capabilities
        """
        logging.info(f'Collecting Capabilities...')

        try:
            gnmi_message_request = CapabilityRequest()
            gnmi_message_response = self.__stub.Capabilities(gnmi_message_request, metadata=self.__metadata)

            if self.__to_print:
                print(gnmi_message_response)

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

            logging.info(f'Collection of Capabilities is successfull')

            self.__capabilities = response
            return response

        except:
            logging.error(f'Collection of Capabilities is failed.')


    def get(self, path):
        """
        Collecting path information
        """
        logging.info(f'Collecting info from requested paths (Get opertaion)...')

        protobuf_paths = [gnmi_path_generator(pe) for pe in path]

        if self.__capabilities and 'supported_encodings' in self.__capabilities:
            if 0 in self.__capabilities['supported_encodings']:
                enc = 0
            elif 4 in self.__capabilities['supported_encodings']:
                enc = 4

        else:
            enc = 0

        gnmi_message_request = GetRequest(path=protobuf_paths, type=0, encoding=enc)
        gnmi_message_response = self.__stub.Get(gnmi_message_request, metadata=self.__metadata)

        if self.__to_print:
            print(gnmi_message_response)


    def __exit__(self, type, value, traceback):
        self.__channel.close()