#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
import grpc
from pygnmi.spec.gnmi_pb2_grpc import gNMIStub
from pygnmi.spec.gnmi_pb2 import CapabilityRequest, GetRequest, SetRequest, Update, TypedValue
import re
import sys
import json
import logging


# Own modules
from pygnmi.path_generator import gnmi_path_generator


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
        Collecting the gNMI capabilities of the network device
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

            return None


    def get(self, path, datatype='all'):
        """
        Collecting the information about the resources from defined paths.
        Path is provided as a list in format: ['yanf-module:container/container[key=value]', 'yanf-module:container/container[key=value]', ..]
        """
        logging.info(f'Collecting info from requested paths (Get opertaion)...')

        datatype = datatype.lower()
        type_dict = {'all', 'config', 'state', 'operational'}

        if datatype in type_dict:
            if datatype == 'all':
                pb_datatype = 0
            elif datatype == 'config':
                pb_datatype = 1
            elif datatype == 'state':
                pb_datatype = 2
            elif datatype == 'operational':
                pb_datatype = 3
            else:
                logging.error('The GetRequst data type is not within the dfined range')

        try:
            protobuf_paths = [gnmi_path_generator(pe) for pe in path]

        except:
            logging.error(f'Conversion of gNMI paths to the Protobuf format failed')
            sys.exit(10)

        if self.__capabilities and 'supported_encodings' in self.__capabilities:
            if 0 in self.__capabilities['supported_encodings']:
                enc = 0
            elif 4 in self.__capabilities['supported_encodings']:
                enc = 4

        else:
            enc = 0

        try:
            gnmi_message_request = GetRequest(path=protobuf_paths, type=pb_datatype, encoding=enc)
            gnmi_message_response = self.__stub.Get(gnmi_message_request, metadata=self.__metadata)

            if self.__to_print:
                print(gnmi_message_response)

            if gnmi_message_response:
                response = {}

                if gnmi_message_response.notification:
                    response.update({'notification': []})

                    for notification in gnmi_message_response.notification:
                        notification_container = {}

                        notification_container.update({'timestamp': notification.timestamp}) if notification.timestamp else notification_container.update({'timestamp': 0})

                        if notification.update:
                            notification_container.update({'update': []})

                            for update_msg in notification.update:
                                update_container = {}

                                if update_msg.path and update_msg.path.elem:
                                    resource_path = []
                                    for path_elem in update_msg.path.elem:
                                        tp = ''
                                        if path_elem.name:
                                            tp += path_elem.name

                                        if path_elem.key:
                                            for pk_name, pk_value in path_elem.key.items():
                                                tp += f'[{pk_name}={pk_value}]'

                                        resource_path.append(tp)
                                
                                    update_container.update({'path': '/'.join(resource_path)})

                                else:
                                    update_container.update({'path': None})

                                if update_msg.val:
                                    if update_msg.val.json_ietf_val:
                                        update_container.update({'json_ietf_val': json.loads(update_msg.val.json_ietf_val)})

                                    elif update_msg.val.json_val:
                                        update_container.update({'json_val': json.loads(update_msg.val.json_val)})

                                notification_container['update'].append(update_container)

                        response['notification'].append(notification_container)

            return response
        
        except:
            logging.error(f'Collection of Get information failed is failed.')

            return None


    def set(self, delete=None, replace=None, update=None):
        """
        Changing the configuration on the destination network elements.
        Could provide a single attribute or multiple attributes.
        """
        del_protobuf_paths = []
        replace_msg = []
        update_msg = []

        if delete:
            if isinstance(replace, list):
                try:
                    del_protobuf_paths = [gnmi_path_generator(pe) for pe in delete]

                except:
                    logging.error(f'Conversion of gNMI paths to the Protobuf format failed')
                    sys.exit(10)

            else:
                logging.error(f'The provided input for Set Update message is not list.')
                sys.exit(10)

        if replace:
            if isinstance(replace, list):
                for ue in replace:
                    if isinstance(ue, tuple):
                        u_path = gnmi_path_generator(ue[0])
                        u_val = json.dumps(ue[1]).encode('utf-8')

                        replace_msg.append(Update(path=u_path, val=TypedValue(json_val=u_val)))

                    else:
                        logging.error(f'The input element for Update message must be tuple, got {ue}.')
                        sys.exit(10)

            else:
                logging.error(f'The provided input for Set Update message is not list.')
                sys.exit(10)

        if update:
            if isinstance(update, list):
                for ue in update:
                    if isinstance(ue, tuple):
                        u_path = gnmi_path_generator(ue[0])
                        u_val = json.dumps(ue[1]).encode('utf-8')

                        update_msg.append(Update(path=u_path, val=TypedValue(json_val=u_val)))

                    else:
                        logging.error(f'The input element for Update message must be tuple, got {ue}.')
                        sys.exit(10)

            else:
                logging.error(f'The provided input for Set Update message is not list.')
                sys.exit(10)

#        try:
        gnmi_message_request = SetRequest(delete=del_protobuf_paths, update=update_msg, replace=replace_msg)
        gnmi_message_response = self.__stub.Set(gnmi_message_request, metadata=self.__metadata)

        if self.__to_print:
            print(gnmi_message_response)

        if gnmi_message_response:
            response = {}

            return response

        else:
            logging.error('Failed parsing of SetResponse.')
            return None
        
#        except:
#            logging.error(f'Collection of Set information failed is failed.')

            return None


    def __exit__(self, type, value, traceback):
        self.__channel.close()