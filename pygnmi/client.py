#!/usr/bin/env python
#(c)2019-2021, karneliuk.com

# Modules
import grpc
from pygnmi.spec.gnmi_pb2_grpc import gNMIStub
from pygnmi.spec.gnmi_pb2 import CapabilityRequest, GetRequest, SetRequest, Update, TypedValue, SubscribeRequest, Poll, Subscription, SubscriptionList, SubscriptionMode, Alias, AliasList, QOSMarking, SubscribeResponse
import re
import sys
import json
import logging
import time


# Own modules
from pygnmi.path_generator import gnmi_path_generator


# Classes
class gNMIclient(object):
    """
    This class instantiates the object, which interacts with the network elements over gNMI.
    """
    def __init__(self, target: tuple, username: str = None, password: str = None, 
                 debug: bool = False, insecure: bool = False, path_cert: str = None, override: str = None):
        """
        Initializing the object
        """
        self.__metadata = [('username', username), ('password', password)]
        self.__capabilities = None
        self.__debug = debug
        self.__insecure = insecure
        self.__path_cert = path_cert
        self.__override = override
        self.__options=[('grpc.ssl_target_name_override', self.__override)]

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

            self.__channel = grpc.secure_channel(f'{self.__target[0]}:{self.__target[1]}', cert, self.__options)
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

            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------\n\n\ngNMI response:\n------------------------------------------------")
                print(gnmi_message_response)
                print("------------------------------------------------")

            if gnmi_message_response:
                response = {}
                
                if gnmi_message_response.supported_models:
                    response.update({'supported_models': []})

                    for ree in gnmi_message_response.supported_models:
                        response['supported_models'].append({'name': ree.name, 'organization': ree.organization, 'version': ree.version})

                if gnmi_message_response.supported_encodings:
                    response.update({'supported_encodings': []})

                    for ree in gnmi_message_response.supported_encodings:
                        if ree == 0:
                            dree = 'json'
                        elif ree == 1:
                            dree = 'bytes'
                        elif ree == 2:
                            dree = 'proto'
                        elif ree == 3:
                            dree = 'ascii'
                        else:
                            dree = 'json_ietf'

                        response['supported_encodings'].append(dree)

                if gnmi_message_response.gNMI_version:
                    response.update({'gnmi_version': gnmi_message_response.gNMI_version})

            logging.info(f'Collection of Capabilities is successfull')

            self.__capabilities = response
            return response

        except grpc._channel._InactiveRpcError as err:
            print(f"Host: {self.__target[0]}:{self.__target[1]}\nError: {err.details()}")
            logging.critical(f"Host: {self.__target[0]}:{self.__target[1]}, Error: {err.details()}")
            sys.exit(10)

        except:
            logging.error(f'Collection of Capabilities is failed.')

            return None


    def get(self, path: list, datatype: str = 'all', encoding: str = 'json'):
        """
        Collecting the information about the resources from defined paths.

        Path is provided as a list in the following format: 
          path = ['yang-module:container/container[key=value]', 'yang-module:container/container[key=value]', ..]
        
        The datatype argument may have the following values per gNMI specification:
          - all
          - config
          - state
          - operational

        The encoding argument may have the following values per gNMI specification:
          - json
          - bytes
          - proto
          - ascii
          - json_ietf
        """
        logging.info(f'Collecting info from requested paths (Get opertaion)...')

        datatype = datatype.lower()
        type_dict = {'all', 'config', 'state', 'operational'}
        encoding_set = {'json', 'bytes', 'proto', 'ascii', 'json_ietf'}

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

        if encoding in encoding_set:
            if encoding.lower() == 'json':
                pb_encoding = 0
            elif encoding.lower() == 'bytes':
                pb_encoding = 1
            elif encoding.lower() == 'proto':
                pb_encoding = 2
            elif encoding.lower() == 'ascii':
                pb_encoding = 3
            else:
                pb_encoding = 4

        try:
            if not path:
                protobuf_paths = []
                protobuf_paths.append(gnmi_path_generator(path))
            else:
                protobuf_paths = [gnmi_path_generator(pe) for pe in path]

        except:
            logging.error(f'Conversion of gNMI paths to the Protobuf format failed')
            sys.exit(10)

        if self.__capabilities and 'supported_encodings' in self.__capabilities:
            if 'json' in self.__capabilities['supported_encodings']:
                pb_encoding = 0
            elif 'json_ietf' in self.__capabilities['supported_encodings']:
                pb_encoding = 4

        try:
            gnmi_message_request = GetRequest(path=protobuf_paths, type=pb_datatype, encoding=pb_encoding)
            gnmi_message_response = self.__stub.Get(gnmi_message_request, metadata=self.__metadata)

            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------\n\n\ngNMI response:\n------------------------------------------------")
                print(gnmi_message_response)
                print("------------------------------------------------")

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

                                if update_msg.HasField('val'):
                                    if update_msg.val.HasField('json_ietf_val'):
                                        update_container.update({'val': json.loads(update_msg.val.json_ietf_val)})

                                    elif update_msg.val.HasField('json_val'):
                                        update_container.update({'val': json.loads(update_msg.val.json_val)})

                                    elif update_msg.val.HasField('ascii_val'):
                                        update_container.update({'val': json.loads(update_msg.val.ascii_val)})

                                    elif update_msg.val.HasField('bytes_val'):
                                        update_container.update({'val': json.loads(update_msg.val.bytes_val)})

                                    elif update_msg.val.HasField('proto_bytes'):
                                        update_container.update({'val': json.loads(update_msg.val.proto_bytes)})

                                notification_container['update'].append(update_container)

                        response['notification'].append(notification_container)

            return response

        except grpc._channel._InactiveRpcError as err:
            print(f"Host: {self.__target[0]}:{self.__target[1]}\nError: {err.details()}")
            logging.critical(f"Host: {self.__target[0]}:{self.__target[1]}, Error: {err.details()}")
            sys.exit(10)

        except:
            logging.error(f'Collection of Get information failed is failed.')

            return None


    def set(self, delete: list = None, replace: list = None, update: list = None, encoding: str = 'json'):
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

        The encoding argument may have the following values per gNMI specification:
          - json
          - bytes
          - proto
          - ascii
          - json_ietf
        """
        del_protobuf_paths = []
        replace_msg = []
        update_msg = []
        encoding_set = {'json', 'bytes', 'proto', 'ascii', 'json_ietf'}

        if encoding not in encoding_set:
            logging.error(f'The encoding {encoding} is not supported. The allowed are: {", ".join(encoding_set)}.')
            sys.exit(11)

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

                        if encoding == 'json':
                            replace_msg.append(Update(path=u_path, val=TypedValue(json_val=u_val)))
                        elif encoding == 'bytes':
                            replace_msg.append(Update(path=u_path, val=TypedValue(bytes_val=u_val)))
                        elif encoding == 'proto':
                            replace_msg.append(Update(path=u_path, val=TypedValue(proto_bytes=u_val)))
                        elif encoding == 'ascii':
                            replace_msg.append(Update(path=u_path, val=TypedValue(ascii_val=u_val)))
                        elif encoding == 'json_ietf':
                            replace_msg.append(Update(path=u_path, val=TypedValue(json_ietf_val=u_val)))

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

                        if encoding == 'json':
                            update_msg.append(Update(path=u_path, val=TypedValue(json_val=u_val)))
                        elif encoding == 'bytes':
                            update_msg.append(Update(path=u_path, val=TypedValue(bytes_val=u_val)))
                        elif encoding == 'proto':
                            update_msg.append(Update(path=u_path, val=TypedValue(proto_bytes=u_val)))
                        elif encoding == 'ascii':
                            update_msg.append(Update(path=u_path, val=TypedValue(ascii_val=u_val)))
                        elif encoding == 'json_ietf':
                            update_msg.append(Update(path=u_path, val=TypedValue(json_ietf_val=u_val)))

                    else:
                        logging.error(f'The input element for Update message must be tuple, got {ue}.')
                        sys.exit(10)

            else:
                logging.error(f'The provided input for Set message (update operation) is not list.')
                sys.exit(10)

        try:
            gnmi_message_request = SetRequest(delete=del_protobuf_paths, update=update_msg, replace=replace_msg)
            gnmi_message_response = self.__stub.Set(gnmi_message_request, metadata=self.__metadata)

            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------\n\n\ngNMI response:\n------------------------------------------------")
                print(gnmi_message_response)
                print("------------------------------------------------")

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

        except grpc._channel._InactiveRpcError as err:
            print(f"Host: {self.__target[0]}:{self.__target[1]}\nError: {err.details()}")
            logging.critical(f"Host: {self.__target[0]}:{self.__target[1]}, Error: {err.details()}")
            sys.exit(10)

        except:
            logging.error(f'Collection of Set information failed is failed.')
            return None


    def subscribe(self, subscribe: dict = None, poll: bool = False, aliases: list = None):
        """
        Implentation of the subsrcibe gNMI RPC to pool
        """
        logging.info(f'Collecting Telemetry...')

        if (subscribe and poll) or (subscribe and aliases) or (poll and aliases):
            raise Exception('Subscribe request supports only one request at a time.')

        if poll:
            if isinstance(poll, bool):
                if poll:
                    request = Poll()

                    gnmi_message_request = SubscribeRequest(poll=request)

            else:
                logging.error('Subscribe pool request is specificed, but the value is not boolean.')

        if aliases:
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

        if subscribe:
            if isinstance(subscribe, dict):
                request = SubscriptionList()

                # use_alias
                if 'use_aliases' not in subscribe:
                    subscribe.update({'use_aliases': False})

                if isinstance(subscribe['use_aliases'], bool):
                    request.use_aliases = subscribe['use_aliases']
                else:
                    raise ValueError('Subsricbe use_aliases should have boolean type.')

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
                    subscribe.update({'encoding': 'proto'})

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

    #            if subscribe['qos'] >= 0 and subscribe['qos'] <= 64:
    #                request.qos = QOSMarking(marking=subscribe['qos'])

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


            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------")

        return self.__stub.Subscribe(self.__generator(gnmi_message_request), metadata=self.__metadata)


    def __generator(self, in_message=None):
        """
        Private method used in the telemetry as the input to the stream RPC requires iterator
        rather than a standard element.
        """
        yield in_message


    def __exit__(self, type, value, traceback):
        self.__channel.close()


    def close(self):
        self.__channel.close()


# User-defined functions
def telemetryParser(in_message=None, debug: bool = False):
    """
    The telemetry parser is method used to covert the Protobuf message
    """

    if debug:
        print("gNMI response:\n------------------------------------------------")
        print(in_message)
        print("------------------------------------------------")

    try:
        response = {}
        if in_message.HasField('update'):
            response.update({'update': {'update': []}})
            
            response['update'].update({'timestamp': in_message.update.timestamp}) if in_message.update.timestamp else in_message.update({'timestamp': 0})

            if in_message.update.HasField('prefix'):
                resource_prefix = []
                for prefix_elem in in_message.update.prefix.elem:
                    tp = ''
                    if prefix_elem.name:
                        tp += prefix_elem.name

                    if prefix_elem.key:
                        for pk_name, pk_value in prefix_elem.key.items():
                            tp += f'[{pk_name}={pk_value}]'

                    resource_prefix.append(tp)

                response['update'].update({'prefix': '/'.join(resource_prefix)})

            for update_msg in in_message.update.update:
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
                    if update_msg.val.HasField('json_ietf_val'):
                        update_container.update({'val': json.loads(update_msg.val.json_ietf_val)})

                    elif update_msg.val.HasField('json_val'):
                        update_container.update({'val': json.loads(update_msg.val.json_val)})

                    elif update_msg.val.HasField('string_val'):
                        update_container.update({'val':update_msg.val.string_val})

                    elif update_msg.val.HasField('int_val'):
                        update_container.update({'val': update_msg.val.int_val})

                    elif update_msg.val.HasField('uint_val'):
                        update_container.update({'val': update_msg.val.uint_val})

                    elif update_msg.val.HasField('bool_val'):
                        update_container.update({'val': update_msg.val.bool_val})

                    elif update_msg.val.HasField('float_val'):
                        update_container.update({'val': update_msg.val.float_val})

                    elif update_msg.val.HasField('decimal_val'):
                        update_container.update({'val': update_msg.val.decimal_val})

                    elif update_msg.val.HasField('any_val'):
                        update_container.update({'val': update_msg.val.any_val})

                    elif update_msg.val.HasField('ascii_val'):
                        update_container.update({'val': update_msg.val.ascii_val})

                    elif update_msg.val.HasField('proto_bytes'):
                        update_container.update({'val': update_msg.val.proto_bytes})

                response['update']['update'].append(update_container)

            return response

        elif in_message.HasField('sync_response'):
            response['sync_response'] = in_message.sync_response

            return response

    except:
        logging.error(f'Parsing of telemetry information is failed.')

        return None