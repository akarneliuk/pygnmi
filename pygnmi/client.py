#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
import grpc
from pygnmi.spec.gnmi_pb2_grpc import gNMIStub
from pygnmi.spec.gnmi_pb2 import CapabilityRequest, GetRequest, SetRequest, Update, TypedValue, SubscribeRequest, Poll, Subscription, SubscriptionList, SubscriptionMode, Alias, AliasList, QOSMarking
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
    def __init__(self, target: tuple, username: str = None, password: str = None, 
                 to_print: bool = False, insecure: bool = False, path_cert: str = None):
        """
        Initializing the object
        """
        self.__metadata = [('username', username), ('password', password)]
        self.__capabilities = None
        self.__to_print = to_print
        self.__insecure = insecure
        self.__path_cert = path_cert

        if re.match('.*:.*', target[0]):
            self.__target = (f'[{target[0]}]', target[1])
        else:
            self.__target = target

    
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
        Collecting the gNMI capabilities of the network device.
        There are no arguments needed for this call
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


    def get(self, path: list, datatype: str = 'all'):
        """
        Collecting the information about the resources from defined paths.

        Path is provided as a list in the following format: 
          path = ['yang-module:container/container[key=value]', 'yang-module:container/container[key=value]', ..]
        
        The datatype argument may have the following value per gNMI specification:
          - all
          - config
          - state
          - operational
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


    def set(self, delete: list = None, replace: list = None, update: list = None):
        """
        Changing the configuration on the destination network elements.
        Could provide a single attribute or multiple attributes.

        delete:
          - list of paths with the resources to delete. The format is the same as for get() request

        replace:
          - list of tuples where the first entry path provided as a string, and the second entry
            is a dictionary with the configuration to be configured

        replace:
          - list of tuples where the first entry path provided as a string, and the second entry
            is a dictionary with the configuration to be configured
        """
        del_protobuf_paths = []
        replace_msg = []
        update_msg = []

        if delete:
            if isinstance(delete, list):
                try:
                    del_protobuf_paths = [gnmi_path_generator(pe) for pe in delete]

                except:
                    logging.error(f'Conversion of gNMI paths to the Protobuf format failed')
                    sys.exit(10)

            else:
                logging.error(f'The provided input for Set message (delete operation) is not list.')
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
                logging.error(f'The provided input for Set message (replace operation) is not list.')
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
                logging.error(f'The provided input for Set message (update operation) is not list.')
                sys.exit(10)

        try:
            gnmi_message_request = SetRequest(delete=del_protobuf_paths, update=update_msg, replace=replace_msg)
            gnmi_message_response = self.__stub.Set(gnmi_message_request, metadata=self.__metadata)

            if self.__to_print:
                print(gnmi_message_response)

            if gnmi_message_response:
                response = {}

                if gnmi_message_response.response:
                    response.update({'response': []})

                    for response_entry in gnmi_message_response.response:
                        response_container = {}

                        if response_entry.path and response_entry.path.elem:
                            resource_path = []
                            for path_elem in response_entry.path.elem:
                                tp = ''
                                if path_elem.name:
                                    tp += path_elem.name

                                if path_elem.key:
                                    for pk_name, pk_value in path_elem.key.items():
                                        tp += f'[{pk_name}={pk_value}]'

                                resource_path.append(tp)
                        
                            response_container.update({'path': '/'.join(resource_path)})

                        else:
                            response_container.update({'path': None})

                        if response_entry.op:
                            if response_entry.op == 1:
                                res_op = 'DELETE'
                            elif response_entry.op == 2:
                                res_op = 'REPLACE'
                            elif response_entry.op == 3:
                                res_op = 'UPDATE'
                            else:
                                res_op = 'UNDEFINED'

                            response_container.update({'op': res_op})

                        response['response'].append(response_container)

                return response

            else:
                logging.error('Failed parsing the SetResponse.')
                return None
        
        except:
            logging.error(f'Collection of Set information failed is failed.')
            return None


    def subscribe(self, subscribe: dict = None, poll: bool = False, aliases: list = None):
        """
        Implentation of the subsrcibe gNMI RPC to pool
        """
        logging.info(f'Collecting Capabilities...')

        if (subscribe and poll) or (subscribe and aliases) or (poll and aliases):
            raise Exception('Subscribe request supports only one request at a time.')

        if isinstance(poll, bool):
            if poll:
                request = Poll()

                gnmi_message_request = SubscribeRequest(poll=request)

        else:
            logging.error('Subscribe pool request is specificed, but the value is not boolean.')

        if isinstance(aliases, list):
            request = AliasList()
            for ae in aliases:
                if isinstance(ae, tuple):
                    if re.match('^#.*', ae[1]):
                        request.alias.add(path=gnmi_path_generator(ae[0]), alias=ae[1])

                else:
                    raise ValueError('The alias is malformed. It should start with #...')

            gnmi_message_request = SubscribeRequest(aliases=request)

        else:
            logging.error('Subscribe aliases request is specified, but the value is not list.')

        if isinstance(subscribe, dict):
            request = SubscriptionList()

            # use_alias
            if 'use_alias' not in subscribe:
                subscribe.update({'use_alias': False})

            if isinstance(subscribe['use_alias'], bool):
                request.use_alias = subscribe['use_alias']
            else:
                raise ValueError('Subsricbe use_alias should have boolean type.')

            # mode
            if 'mode' not in subscribe:
                subscribe.update({'mode': 'stream'})

            if subscribe['mode'].lower() in {'stream', 'once', 'poll'}:
                if subscribe['mode'].lower() == 'stream':
                    request.mode = 0
                elif subscribe['mode'].lower() == 'once':
                    request.mode = 1
                elif subscribe['mode'].lower() == 'poll':
                    request.mode = 2
            else:
                raise ValueError('Subscribe mode is out of allowed ranges.')

            # allow_aggregation
            if 'allow_aggregation' not in subscribe:
                subscribe.update({'allow_aggregation': False})

            if isinstance(subscribe['allow_aggregation'], bool):
                request.allow_aggregation = subscribe['allow_aggregation']
            else:
                raise ValueError('Subsricbe allow_aggregation should have boolean type.')

            # updates_only
            if 'updates_only' not in subscribe:
                subscribe.update({'updates_only': False})

            if isinstance(subscribe['updates_only'], bool):
                request.updates_only = subscribe['updates_only']
            else:
                raise ValueError('Subsricbe updates_only should have boolean type.')

            # encoding
            if 'encoding' not in subscribe:
                subscribe.update({'encoding': 'json'})

            if subscribe['encoding'].lower() in {'json', 'bytes', 'proto', 'ascii', 'json_ietf'}:
                if subscribe['encoding'].lower() == 'json':
                    request.encoding = 0
                elif subscribe['encoding'].lower() == 'bytes':
                    request.encoding = 1
                elif subscribe['encoding'].lower() == 'proto':
                    request.encoding = 2
                elif subscribe['encoding'].lower() == 'ascii':
                    request.encoding = 3
                elif subscribe['encoding'].lower() == 'json_ietf':
                    request.encoding = 4
            else:
                raise ValueError('Subscribe encoding is out of allowed ranges.')

            # qos
            if 'qos' not in subscribe:
                subscribe.update({'qos': 0})

            if subscribe['qos'] >= 0 and subscribe['qos'] <= 64:
                request.qos = QOSMarking(marking=subscribe['qos'])

            # use_models
            if 'use_models' not in subscribe:
                subscribe.update({'use_models': []})

            if isinstance(subscribe['use_models'], list) and subscribe['use_models']:
                raise NotImplementedError('This will be done later at some point, if there is a need.')

            # prefix
            if 'prefix' not in subscribe:
                subscribe.update({'prefix': None})

            if subscribe['prefix']:
                request.prefix = gnmi_path_generator(subscribe['prefix'])

            # subscription
            if 'subscription' not in subscribe:
                subscribe.update({'subscription': []})

            if subscribe['subscription']:
                for se in subscribe['subscription']:
                    if 'path' in se:
                        v1 = gnmi_path_generator(se['path'])
                    else:
                        raise ValueError('Subscribe:subscription:path is missing')

                    if 'mode' in se:
                        if se['mode'].lower() in {'target_defined', 'on_change', 'sample'}:
                            if se['mode'].lower() == 'target_defined':
                                v2 = 0
                            elif se['mode'].lower() == 'on_change':
                                v2 = 1
                            elif se['mode'].lower() == 'sample':
                                v2 = 2

                        else:
                            raise ValueError('Subscribe:subscription:mode is not inside allowed range')
                    else:
                        raise ValueError('Subscribe:subscription:mode is missing')

                    if 'sample_interval' in se and isinstance(se['sample_interval'], int):
                        v3 = se['sample_interval']
                    else:
                        v3 = 0

                    if 'suppress_redundant' in se and isinstance(se['suppress_redundant'], bool):
                        v4 = se['suppress_redundant']
                    else:
                        v4 = False

                    if 'heartbeat_interval' in se and isinstance(se['heartbeat_interval'], int):
                        v5 = se['heartbeat_interval']
                    else:
                        v5 = 0

                    request.subscription.add(path=v1, mode=v2, sample_interval=v3, suppress_redundant=v4, heartbeat_interval=v5)

            else:
                raise ValueError('Subscribe:subscription value is missing.')

            gnmi_message_request = SubscribeRequest(subscribe=request)

        else:
            logging.error('Subscribe subscribe requst is specified, but the value is not list.')

        gnmi_message_response = self.__stub.Subscribe(gnmi_message_request, metadata=self.__metadata)

        print(gnmi_message_response)

        return None
    

    def __exit__(self, type, value, traceback):
        self.__channel.close()