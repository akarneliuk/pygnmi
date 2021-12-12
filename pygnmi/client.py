#(c)2019-2021, karneliuk.com

# Modules
import grpc
from pygnmi.spec.gnmi_pb2_grpc import gNMIStub
from pygnmi.spec.gnmi_pb2 import (CapabilityRequest, Encoding, GetRequest, \
    SetRequest, Update, TypedValue, SubscribeRequest, Poll, SubscriptionList, \
    SubscriptionMode, AliasList, UpdateResult)
import re
import sys
import json
import logging
import queue
import time
import threading


# Those three modules are required to retrieve cert from the router and extract cn name
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend


# Own modules
from pygnmi.path_generator import gnmi_path_generator, gnmi_path_degenerator
from pygnmi.tools import diff_openconfig


# Logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


# Classes
class gNMIclient(object):
    """
    This class instantiates the object, which interacts with the network elements over gNMI.
    """
    def __init__(self, target: tuple, username: str = None, password: str = None,
                 debug: bool = False, insecure: bool = False, path_cert: str = None, 
                 path_key: str = None, path_root: str = None, override: str = None,
                 gnmi_timeout: int = 5, grpc_options: list = [], show_diff: str = "", **kwargs ):

        """
        Initializing the object
        """
        self.__metadata = [('username', username), ('password', password)]
        self.__capabilities = None
        self.__debug = debug
        self.__insecure = insecure
        self.__path_cert = path_cert
        self.__path_key = path_key
        self.__path_root = path_root
        self.__options=([('grpc.ssl_target_name_override', override)]+grpc_options) if override else grpc_options
        self.__gnmi_timeout = gnmi_timeout
        self.__show_diff = show_diff if show_diff in {"get", "print"} else ""

        self.__target_path = f'{target[0]}:{target[1]}'
        if re.match('unix:.*', target[0]):
            self.__target = target
            self.__target_path = target[0]
        elif re.match('.*:.*', target[0]):
            self.__target = (f'[{target[0]}]', target[1])
        else:
            self.__target = target

        if 'interval_ms' in kwargs:
            self.configureKeepalive(**kwargs)

    def configureKeepalive(self, keepalive_time_ms: int, keepalive_timeout_ms: int = 20000,
                           max_pings_without_data: int = 0,
                           keepalive_permit_without_calls: bool = True):
        """
        Helper method to set relevant client-side gRPC options to control keep-alive messages
        Must be called before connect()

        See https://github.com/grpc/grpc/blob/master/doc/keepalive.md

        max_pings_without_data: default 0 to enable long idle connections
        """
        self.__options += [
          ("grpc.keepalive_time_ms", keepalive_time_ms),
          ("grpc.keepalive_timeout_ms", keepalive_timeout_ms),
          ("grpc.keepalive_permit_without_calls", 1 if keepalive_permit_without_calls else 0),
          ("grpc.http2.max_pings_without_data", max_pings_without_data),
        ]

    def __enter__(self):
        """
        Building the connectivity towards network element over gNMI (used in the with ... as ... context manager)
        """
        return self.connect()


    def connect(self,timeout:int = None):
        """
        Building the connectivity towards network element over gNMI
        timeout: optional override of the time to wait for connection, defaults to init parameter
        """

        if self.__insecure:
            self.__channel = grpc.insecure_channel(self.__target_path, self.__metadata + self.__options)

        else:
            if self.__path_cert and self.__path_key and self.__path_root:
                try:
                    cert = open(self.__path_cert, 'rb').read()
                    key = open(self.__path_key, 'rb').read()
                    root_cert = open(self.__path_root, 'rb').read()
                    cert = grpc.ssl_channel_credentials(root_certificates=root_cert, private_key=key, certificate_chain=cert)
                except:
                    logging.error('The SSL certificate cannot be opened.')
                    raise Exception('The SSL certificate cannot be opened.')

            elif self.__path_cert:
                try:
                    with open(self.__path_cert, 'rb') as f:
                        cert = grpc.ssl_channel_credentials(f.read())

                except:
                    logger.error('The SSL certificate cannot be opened.')
                    raise Exception('The SSL certificate cannot be opened.')

            else:
                try:
                    ssl_cert = ssl.get_server_certificate((self.__target[0], self.__target[1])).encode("utf-8")
                    ssl_cert_deserialized = x509.load_pem_x509_certificate(ssl_cert, default_backend())
                    ssl_cert_common_names = ssl_cert_deserialized.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
                    ssl_target_name_override = ssl_cert_common_names[0].value
                    self.__options += [("grpc.ssl_target_name_override", ssl_target_name_override)]
                    logger.warning('ssl_target_name_override is applied, should be used for testing only!')
                    cert = grpc.ssl_channel_credentials(ssl_cert)

                except:
                    logger.error(f'The SSL certificate cannot be retrieved from {self.__target}')
                    raise Exception(f'The SSL certificate cannot be retrieved from {self.__target}')

            self.__channel = grpc.secure_channel(self.__target_path,
                                                 credentials=cert, options=self.__options)

        if timeout is None:
           timeout = self.__gnmi_timeout
        if timeout is None or timeout > 0:
           self.wait_for_connect(timeout)
        self.__stub = gNMIStub(self.__channel)

        return self


    def wait_for_connect(self, timeout: int):
        """
        Wait for the gNMI connection to the server to come up, with given timeout
        """
        grpc.channel_ready_future(self.__channel).result(timeout=timeout)


    def capabilities(self):
        """
        Collecting the gNMI capabilities of the network device.
        There are no arguments needed for this call
        """
        logger.info(f'Collecting Capabilities...')

        try:
            gnmi_message_request = CapabilityRequest()

            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------")

            gnmi_message_response = self.__stub.Capabilities(gnmi_message_request, metadata=self.__metadata)

            if self.__debug:
                print("\n\n\ngNMI response:\n------------------------------------------------")
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

            logger.info(f'Collection of Capabilities is successfull')

            self.__capabilities = response
            return response

        except grpc._channel._InactiveRpcError as err:
            print(f"Host: {self.__target_path}\nError: {err.details()}")
            logger.critical(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}")

            raise Exception (err)

        except:
            logger.error(f'Collection of Capabilities is failed.')

            return None


    def get(self, prefix: str = "", path: list = [], datatype: str = 'all', encoding: str = 'json'):
        """
        Collecting the information about the resources from defined paths.

        Path is provided as a list in the following format:
          path = ['yang-module:container/container[key=value]', 'yang-module:container/container[key=value]', ..]

        Available path formats:
          - yang-module:container/container[key=value]
          - /yang-module:container/container[key=value]
          - /yang-module:/container/container[key=value]
          - /container/container[key=value]
          - /

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
        logger.info(f'Collecting info from requested paths (Get operation)...')

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
                logger.error('The GetRequst data type is not within the defined range')

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

        ## Gnmi PREFIX
        try:
            protobuf_prefix = gnmi_path_generator(prefix) if prefix else gnmi_path_generator([])

        except:
            logger.error(f'Conversion of gNMI prefix to the Protobuf format failed')
            raise Exception ('Conversion of gNMI prefix to the Protobuf format failed')

        ## Gnmi PATH
        try:
            if not path:
                protobuf_paths = []
                protobuf_paths.append(gnmi_path_generator(path))
            else:
                protobuf_paths = [gnmi_path_generator(pe) for pe in path]

        except:
            logger.error(f'Conversion of gNMI paths to the Protobuf format failed')
            raise Exception ('Conversion of gNMI paths to the Protobuf format failed')

        if self.__capabilities and 'supported_encodings' in self.__capabilities:
            if 'json' in self.__capabilities['supported_encodings']:
                pb_encoding = 0
            elif 'json_ietf' in self.__capabilities['supported_encodings']:
                pb_encoding = 4

        try:
            gnmi_message_request = GetRequest(prefix=protobuf_prefix, path=protobuf_paths, 
                                              type=pb_datatype, encoding=pb_encoding)

            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------")

            gnmi_message_response = self.__stub.Get(gnmi_message_request, metadata=self.__metadata)

            if self.__debug:
                print("\n\n\ngNMI response:\n------------------------------------------------")
                print(gnmi_message_response)
                print("------------------------------------------------")

            if gnmi_message_response:
                response = {}

                ## Message GetRespone, Key notification
                if gnmi_message_response.notification:
                    response.update({'notification': []})

                    for notification in gnmi_message_response.notification:
                        notification_container = {}

                        ## Message Notification, Key timestamp
                        notification_container.update({'timestamp': notification.timestamp}) if notification.timestamp else notification_container.update({'timestamp': 0})

                        ## Message Notification, Key prefix
                        notification_container.update({'prefix': gnmi_path_degenerator(notification.prefix)}) if notification.prefix else notification_container.update({'prefix': None})

                        ## Message Notification, Key alias
                        notification_container.update({'alias': notification.alias}) if notification.alias else notification_container.update({'alias': None})

                        ## Message Notification, Key atomic
                        notification_container.update({'atomic': notification.atomic })

                        ## Message Notification, Key update
                        if notification.update:
                            notification_container.update({'update': []})

                            for update_msg in notification.update:
                                update_container = {}

                                ## Message Update, Key path
                                update_container.update({'path': gnmi_path_degenerator(update_msg.path)}) if update_msg.path else update_container.update({'path': None})

                                ## Message Update, Key val
                                if update_msg.HasField('val'):
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

                                notification_container['update'].append(update_container)

                        response['notification'].append(notification_container)

            return response

        except grpc._channel._InactiveRpcError as err:
            print(f"Host: {self.__target_path}\nError: {err.details()}")
            logger.critical(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}")

            raise Exception (err)

        except:
            logger.error(f'Collection of Get information failed is failed.')

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
        diff_list = []

        if encoding not in encoding_set:
            logger.error(f'The encoding {encoding} is not supported. The allowed are: {", ".join(encoding_set)}.')
            raise Exception (f'The encoding {encoding} is not supported. The allowed are: {", ".join(encoding_set)}.')

        if delete:
            if isinstance(delete, list):
                try:
                    del_protobuf_paths = [gnmi_path_generator(pe) for pe in delete]

                except:
                    logger.error(f'Conversion of gNMI paths to the Protobuf format failed')
                    raise Exception (f'Conversion of gNMI paths to the Protobuf format failed')

            else:
                logger.error(f'The provided input for Set message (delete operation) is not list.')
                raise Exception (f'The provided input for Set message (delete operation) is not list.')

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
                        logger.error(f'The input element for Update message must be tuple, got {ue}.')
                        raise Exception (f'The input element for Update message must be tuple, got {ue}.')

            else:
                logger.error(f'The provided input for Set message (replace operation) is not list.')
                raise Exception ('The provided input for Set message (replace operation) is not list.')

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
                        logger.error(f'The input element for Update message must be tuple, got {ue}.')
                        raise Exception (f'The input element for Update message must be tuple, got {ue}.')

            else:
                logger.error(f'The provided input for Set message (update operation) is not list.')
                raise Exception ('The provided input for Set message (replace operation) is not list.')

        try:
            ## Adding collection of data for diff before the change
            if self.__show_diff:
                paths_to_collect_list = []

                if delete: paths_to_collect_list.extend(delete)
                if update: paths_to_collect_list.extend([path_tuple[0] for path_tuple in update])
                if replace: paths_to_collect_list.extend([path_tuple[0] for path_tuple in replace])

                pre_change_dict = self.get(path=paths_to_collect_list)

            gnmi_message_request = SetRequest(delete=del_protobuf_paths, update=update_msg, replace=replace_msg)

            if self.__debug:
                print("gNMI request:\n------------------------------------------------")
                print(gnmi_message_request)
                print("------------------------------------------------")

            gnmi_message_response = self.__stub.Set(gnmi_message_request, metadata=self.__metadata)

            if self.__debug:
                print("\n\n\ngNMI response:\n------------------------------------------------")
                print(gnmi_message_response)
                print("------------------------------------------------")

            if gnmi_message_response:
                response = {}

                ## Message SetResponse, Key timestamp
                response.update({'timestamp': gnmi_message_response.timestamp}) if gnmi_message_response.timestamp else response.update({'timestamp': 0})

                ## Message SetResponse, Key prefix
                response.update({'prefix': gnmi_path_degenerator(gnmi_message_response.prefix)}) if gnmi_message_response.prefix else response.update({'prefix': None})

                if gnmi_message_response.response:
                    response.update({'response': []})

                    for response_entry in gnmi_message_response.response:
                        response_container = {}

                        ## Message UpdateResult, Key path
                        response_container.update({'path': gnmi_path_degenerator(response_entry.path)}) if response_entry.path else response_container.update({'path': None})

                        ## Message UpdateResult, Key op
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

                ## Adding collection of data for diff before the change
                if self.__show_diff:
                    post_change_dict = self.get(path=paths_to_collect_list)

                    is_printable = True if self.__show_diff == "print" else False

                    diff_list = diff_openconfig(pre_dict=pre_change_dict,
                                                post_dict=post_change_dict,
                                                is_printable=is_printable)

                if diff_list and self.__show_diff == "get":
                    return response, diff_list

                else:
                    return response

            else:
                logger.error('Failed parsing the SetResponse.')
                return None

        except grpc._channel._InactiveRpcError as err:
            print(f"Host: {self.__target_path}\nError: {err.details()}")
            logger.critical(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}")

            raise Exception (err)

        # except:
        #     logger.error(f'Collection of Set information failed is failed.')
        #     return None


    def set_with_retry(self, delete: list = None, replace: list = None, update: list = None, encoding: str = 'json', retry_delay: int = 3):
        """
        Performs a set and retries (once) after a temporary failure with StatusCode.FAILED_PRECONDITION
        """
        try:
            return self.set( delete=delete, replace=replace, update=update, encoding=encoding )

        except Exception as rpc_ex:
            grpc_error = rpc_ex.__context__ # pygnmi wrapped this on line 528 above
            # May happen e.g. during system startup or due to lock contention, retry once

            if grpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION:
                logger.warning( f'FAILED_PRECONDITION exception during set, retrying in {retry_delay}s...' )
                time.sleep( retry_delay )

                return self.set( delete=delete, replace=replace, update=update, encoding=encoding )

            raise rpc_ex


    def _build_subscriptionrequest(self, subscribe: dict):
        if not isinstance(subscribe, dict):
            raise ValueError('Subscribe subscribe request is specified, but the value is not dict.')

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

        if subscribe['encoding'].upper() in Encoding.keys():
            request.encoding = Encoding.Value(subscribe['encoding'].upper())
        else:
            raise ValueError(f'Subscribe encoding {subscribe["encoding"]} is out of allowed ranges.')

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
        if 'subscription' not in subscribe or not subscribe['subscription']:
            raise ValueError('Subscribe:subscription value is missing.')

        for se in subscribe['subscription']:
            # path for that subscription
            if 'path' not in se:
                raise ValueError('Subscribe:subscription:path is missing')
            se_path = gnmi_path_generator(se['path'])

            # subscription entry mode; only relevent when the subscription request is stream
            if subscribe['mode'].lower() == 'stream':
                if 'mode' not in se:
                    raise ValueError('Subscribe:subscription:mode is missing')

                se_mode = SubscriptionMode.Value(se['mode'].upper())
            else:
                se_mode = 0

            if 'sample_interval' in se and isinstance(se['sample_interval'], int):
                se_sample_interval = se['sample_interval']
            else:
                se_sample_interval = 0

            if 'suppress_redundant' in se and isinstance(se['suppress_redundant'], bool):
                se_suppress_redundant = se['suppress_redundant']
            else:
                se_suppress_redundant = False

            if 'heartbeat_interval' in se and isinstance(se['heartbeat_interval'], int):
                se_heartbeat_interval = se['heartbeat_interval']
            else:
                se_heartbeat_interval = 0

            request.subscription.add(path=se_path, mode=se_mode, sample_interval=se_sample_interval,
                                     suppress_redundant=se_suppress_redundant, heartbeat_interval=se_heartbeat_interval)

        return SubscribeRequest(subscribe=request)


    def subscribe(self, subscribe: dict = None, poll: bool = False, aliases: list = None, timeout: float = 0.0):
        """
        Implementation of the subscribe gNMI RPC to pool
        """
        logger.info(f'Collecting Telemetry...')

        if (subscribe and poll) or (subscribe and aliases) or (poll and aliases):
            raise Exception('Subscribe request supports only one request at a time.')

        if poll:
            if isinstance(poll, bool):
                if poll:
                    request = Poll()

                    gnmi_message_request = SubscribeRequest(poll=request)

            else:
                logger.error('Subscribe pool request is specificed, but the value is not boolean.')

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
                logger.error('Subscribe aliases request is specified, but the value is not list.')

        if subscribe:
            gnmi_message_request = self._build_subscriptionrequest(subscribe)

        if self.__debug:
            print("gNMI request:\n------------------------------------------------")
            print(gnmi_message_request)
            print("------------------------------------------------")

        return self.__stub.Subscribe(self.__generator(gnmi_message_request), metadata=self.__metadata)


    def subscribe2(self, subscribe: dict):
        """
        New High-level method to serve temetry based on recent additions
        """

        if 'mode' not in subscribe:
            subscribe.update({'mode': 'stream'})

        if subscribe['mode'].lower() in {'stream', 'once', 'poll'}:
            if subscribe['mode'].lower() == 'stream':
                return self.subscribe_stream(subscribe=subscribe)

            elif subscribe['mode'].lower() == 'poll':
                return self.subscribe_poll(subscribe=subscribe)

            elif subscribe['mode'].lower() == 'once':
                return self.subscribe_once(subscribe=subscribe)

        else:
            raise Exception('Unknown subscription request mode.')


    def subscribe_stream(self, subscribe: dict):
        if 'mode' not in subscribe:
            subscribe['mode'] = 'STREAM'
        gnmi_message_request = self._build_subscriptionrequest(subscribe)
        return StreamSubscriber(self.__channel, gnmi_message_request, self.__metadata)


    def subscribe_poll(self, subscribe: dict):
        if 'mode' not in subscribe:
            subscribe['mode'] = 'POLL'
        gnmi_message_request = self._build_subscriptionrequest(subscribe)
        return PollSubscriber(self.__channel, gnmi_message_request, self.__metadata)


    def subscribe_once(self, subscribe: dict):
        if 'mode' not in subscribe:
            subscribe['mode'] = 'ONCE'
        gnmi_message_request = self._build_subscriptionrequest(subscribe)
        return OnceSubscriber(self.__channel, gnmi_message_request, self.__metadata)


    def __generator(self, in_message):
        """
        Private method used in the telemetry as the input to the stream RPC requires iterator
        rather than a standard element.
        """

        yield in_message


    def __exit__(self, type, value, traceback):
        self.__channel.close()


    def close(self):
        self.__channel.close()


class _Subscriber:
    """Represent a subscription to a list of paths.

    The object can be iterated over to process updates from the target as they
    are available.

    `peek` and `get_update(timeout)` allow to read updates in a time-bound
    fashion.
    """
    def __init__(self, channel, request, metadata):
        """
        Create a new object.

        channel: GRPC channel attached to a target
        request: SubscribeRequest
        metadata: gNMI metadata for that target
        """

        # Enqueue a 'POLL' when we should send an empty Poll to the
        # target, assuming the subscription has mode Poll.
        # Enqueue a 'STOP' to signal we want to stop the subscription;
        # when the grpc client sees the end of the iterator, it will
        # send a close to the target.
        self._msgs = queue.Queue()

        # updates from the target. The subscript thread pushes updates to that
        # queue, and get_one_update (called from next()) dequeues them,
        # decodes them using telemetryParser, then returns to the calling code.
        self._updates = queue.Queue()

        # start the subscription in a separate thread
        _client_stream = self._create_client_stream(request)
        def enqueue_updates():
            stub = gNMIStub(channel)
            subscription = stub.Subscribe(_client_stream, metadata=metadata)
            for update in subscription:
                self._updates.put(update)

        self._subscribe_thread = threading.Thread(target=enqueue_updates)
        self._subscribe_thread.start()


    def _create_client_stream(self, request):
        """Iterator that yields the request, then poll messages when requested.

        This iterator is consumed by grpc. Returning from this
        iterator will cancel the RPC (grpc will send_close_from_client).
        """

        def client_stream(request):
            yield request
            while True:
                msg = self._msgs.get(block=True)
                if msg == 'POLL':
                    yield SubscribeRequest(poll=Poll())
                elif msg == 'STOP':
                    return

        return client_stream(request)


    def _get_one_update(self, timeout=None):
        return telemetryParser(self._updates.get(block=True, timeout=timeout))


    def _get_updates_till_sync(self, timeout=None):
        """Read updates from streaming subscriptions, until sync_response

        Successive updates are coalesced together by merging the update/delete
        lists. Scalar values (timestamp etc.) are set to that of the last
        update.
        """
        resp = {'update': {}}
        while not 'sync_response' in resp:
            new_resp = self._get_one_update(timeout=timeout)
            self._merge_updates(resp, new_resp)
        return resp


    def _merge_updates(self, resp, new_resp):
        if 'update' in new_resp:
            for key in new_resp['update']:
                if key.upper() in UpdateResult.Operation.keys():
                    if key not in resp['update']:
                        resp['update'][key] = []
                    resp['update'][key] += new_resp['update'][key]
                else:
                    resp['update'][key] = new_resp['update'][key]
        if 'sync_response' in new_resp:
            resp['sync_response'] = new_resp['sync_response']


    def __iter__(self):
        return self


    def __next__(self):
        return self.next()


    def next(self):
        """Get the next update from the target.

        Blocks until one is available."""
        return self._next_update(timeout=None)


    def _next_update(self, timeout=None): ...
    # Overridden by each concrete class, as they each have slightly different
    # behaviour around waiting (or not) for a sync_response flag


    def get_update(self, timeout):
        """Get the next update from the target.

        Blocks at most `timeout` seconds; raises TimeoutError if that delay
        elapsed without having gotten a update from the target.
        """
        try:
            return self._next_update(timeout=timeout)
        except queue.Empty:
            raise TimeoutError(f'No update from target after {timeout}s')


    def peek(self) -> bool:
        """Return True if there are updates from the target that have not yet been
        received.
        """
        return not self._updates.empty()


    def close(self):
        """Close the subscription.

        This cancels only that SubscribeRequest RPC, but keeps the
        client session alive.
        """
        self._msgs.put('STOP')
        self._subscribe_thread.join(1)


class StreamSubscriber(_Subscriber):
    """Stream of updates from the target.

    The first time next() is called (or this object is iterated), updates from
    the target are coalesced until a message with the sync_response field is
    seen, and the update is returned. Further calls to next() return messages
    from the target as they arrive. If there has been no update from the
    target yet, next() will block.

    """
    def __init__(self, *args):
        self._first_update_seen = False
        super().__init__(*args)


    def _next_update(self, timeout):
        if not self._first_update_seen:
            self._first_update_seen = True
            return self._get_updates_till_sync(timeout=timeout)
        else:
            return self._get_one_update(timeout=timeout)


class OnceSubscriber(_Subscriber):
    """Stream of updates from the target.

    When next() is called (or this object is iterated), updates from the
    target are returned as they are received. Unlike StreamSubscriber and
    PollSubscriber, updates from the target are never coalesced. The last
    update should have the sync_response field set, at which point the calling
    code should close the subscription.

    'Once' subscriptions are used for potentially large requests, where the
    updates should be streamed in chunks.

    """
    def _next_update(self, timeout):
        return self._get_one_update(timeout=timeout)


class PollSubscriber(_Subscriber):
    """Poll stream of updates from the target.

    Each time next() is called (or this object is iterated), an empty Poll
    message is sent to the target. Updates from the target are coalesced until
    a message with the sync_response field is seen, then the update is
    returned.

    """
    def _next_update(self, timeout):
        self._msgs.put('POLL')
        return self._get_updates_till_sync(timeout=timeout)


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
                        # Use 'sorted' to have a consistent ordering of keys
                        for pk_name, pk_value in sorted(prefix_elem.key.items()):
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
                            # Use 'sorted' to have a consistent ordering of keys
                            for pk_name, pk_value in sorted(path_elem.key.items()):
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

            if in_message.update.delete:
                response['update']['delete'] = []
                for delete_msg in in_message.update.delete:
                    delete_container = {}
                    resource_path = []

                    for path_elem in delete_msg.elem:
                        tp = ''
                        if path_elem.name:
                            tp += path_elem.name

                        if path_elem.key:
                            # Use 'sorted' to have a consistent ordering of keys
                            for pk_name, pk_value in sorted(path_elem.key.items()):
                                tp += f'[{pk_name}={pk_value}]'

                        resource_path.append(tp)

                    delete_container.update({'path': '/'.join(resource_path)})
                    response['update']['delete'].append(delete_container)

            return response

        elif in_message.HasField('sync_response'):
            response['sync_response'] = in_message.sync_response

            return response

    except:
        logger.error(f'Parsing of telemetry information is failed.')

        return None
