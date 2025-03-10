"""
pyGNMI module to manage network devices with gNMI
(c)2020-2024, Karneliuk
"""

# Modules
import re
import sys
import json
import logging
import queue
import struct
import time
import threading
import os
from typing import Any
import cryptography
import grpc
from pygnmi.spec.v080.gnmi_pb2_grpc import gNMIStub
from pygnmi.spec.v080.gnmi_pb2 import (
    CapabilityRequest,
    Encoding,
    GetRequest,
    SetRequest,
    Subscription,
    Update,
    TypedValue,
    SubscribeRequest,
    Poll,
    SubscriptionList,
    SubscriptionMode,
    AliasList,
    UpdateResult,
)


# Those three modules are required to retrieve cert from the router and extract cn name
import socket
import ssl
from urllib.parse import urlparse
from cryptography import x509
from cryptography.hazmat.backends import default_backend


# Own modules
from pygnmi.create_gnmi_path import gnmi_path_generator, gnmi_path_degenerator
from pygnmi.create_gnmi_extension import get_gnmi_extension
from pygnmi.tools import diff_openconfig


# Logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


# Classes
class gNMIclient(object):
    """
    This class instantiates the object, which interacts with the network elements over gNMI.
    """

    def __init__(
        self,
        target: tuple,
        username: str = "",
        password: str = "",
        debug: bool = False,
        insecure: bool = False,
        path_cert: str = None,
        path_key: str = None,
        path_root: str = None,
        override: str = None,
        skip_verify=False,
        gnmi_timeout: int = 5,
        grpc_options: list = None,
        show_diff: str = None,
        token: str = None,
        no_qos_marking: bool = False,
        **kwargs,
    ):
        """
        Initializing the object
        """
        self.__metadata = [("username", username), ("password", password)]
        self.__encoding = "json"  # default, may get overridden based on capabilities
        self.__debug = debug
        self.__insecure = insecure
        self.__path_cert = path_cert
        self.__path_key = path_key
        self.__path_root = path_root
        if grpc_options is None:
            grpc_options = []
        self.__options = ([("grpc.ssl_target_name_override", override)] + grpc_options) if override else grpc_options
        self.__token = token
        self.__gnmi_timeout = gnmi_timeout
        self.__show_diff = show_diff if show_diff in {"get", "print"} else ""
        self.__skip_verify = skip_verify
        self.__no_qos_marking = no_qos_marking

        if re.match("unix:.*", target[0]):
            self.__target = target
            self.__target_path = target[0]
        elif re.match(".*:.*", target[0]):
            self.__target = (f"[{target[0]}]", target[1])
        else:
            self.__target = target
        self.__target_path = f"{self.__target[0]}:{target[1]}"

        if "keepalive_time_ms" in kwargs:
            self.configureKeepalive(**kwargs)

        self.__grpc_proxy = os.getenv("grpc_proxy")

    def configureKeepalive(
        self,
        keepalive_time_ms: int,
        keepalive_timeout_ms: int = 20000,
        max_pings_without_data: int = 0,
        keepalive_permit_without_calls: bool = True,
    ):
        """
        Helper method to set relevant client-side gRPC options to control keep-alive messages
        Must be called before connect()

        See https://github.com/grpc/grpc/blob/master/doc/keepalive.md

        max_pings_without_data: default 0 to enable long idle connections
        """
        self.__options += [
            ("grpc.keepalive_time_ms", keepalive_time_ms),
            ("grpc.keepalive_timeout_ms", keepalive_timeout_ms),
            (
                "grpc.keepalive_permit_without_calls",
                1 if keepalive_permit_without_calls else 0,
            ),
            ("grpc.http2.max_pings_without_data", max_pings_without_data),
        ]

    def __enter__(self):
        """
        Building the connectivity towards network element over gNMI
        (used in the with ... as ... context manager)
        """
        return self.connect()

    def connect(self, timeout: int = None):
        """
        Building the connectivity towards network element over gNMI
        timeout: optional override of the time to wait for connection,
        defaults to init parameter
        """
        # Insecure GRPC channel
        if self.__insecure:
            # Print if debug enabled
            debug_gnmi_msg(self.__debug, self.__target_path, "GRPC Target")
            debug_gnmi_msg(self.__debug, self.__options, "GRPC Channel options")

            self.__channel = grpc.insecure_channel(self.__target_path, self.__metadata + self.__options)

        # Secure GRPC channel
        else:
            # Certificates-based authentication
            if self.__path_cert and self.__path_key and self.__path_root:
                try:
                    ssl_cert = open(self.__path_cert, "rb").read()
                    key = open(self.__path_key, "rb").read()
                    root_cert = open(self.__path_root, "rb").read()

                except FileNotFoundError as e:
                    logger.error("The SSL certificate cannot be opened.")
                    raise gNMIException("The SSL certificate cannot be opened.", e)

            elif self.__path_cert:
                try:
                    with open(self.__path_cert, "rb") as f:
                        ssl_cert = f.read()

                except FileNotFoundError as e:
                    logger.error("The SSL certificate cannot be opened.")
                    raise gNMIException("The SSL certificate cannot be opened.", e)

            # Download a certficate from device if it is not provided
            else:
                try:
                    if self.__grpc_proxy:
                        logger.debug(f"Using proxy {self.__grpc_proxy}")
                        grpc_proxy = urlparse(self.__grpc_proxy)
                        s = socket.socket()
                        s.connect((grpc_proxy.hostname, grpc_proxy.port))
                        # create tunnel to target
                        s.send(f"CONNECT {self.__target[0]}:{self.__target[1]} HTTP/1.0\r\n\r\n".encode())
                        buf = s.recv(8192)
                        if buf[9:12] != b"200":
                            raise gNMIException(f"Didn't get a 200 from the proxy, instead: {buf})")
                        # upgrade socket to ssl - ignore certifcate errors since we only want
                        # to get the certificate and don't transfer sensitive data
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        cert = ctx.wrap_socket(s, server_hostname=self.__target[0]).getpeercert(True)
                        ssl_cert = ssl.DER_cert_to_PEM_cert(cert).encode("utf-8")
                    else:
                        ssl_cert = ssl.get_server_certificate(
                            (
                                re.sub(r"[\[\]]", "", self.__target[0]),
                                self.__target[1],
                            )
                        ).encode("utf-8")

                except Exception as e:
                    logger.error(f"The SSL certificate cannot be retrieved from {self.__target}")
                    raise gNMIException(
                        f"The SSL certificate cannot be retrieved from {self.__target}",
                        e,
                    )

            if self.__skip_verify:
                # Work with the certificate contents
                ssl_cert_deserialized = x509.load_pem_x509_certificate(ssl_cert, default_backend())

                # Collect Certificate's Comman Name
                ssl_cert_common_name = None
                try:
                    ssl_cert_common_name = ssl_cert_deserialized.subject.get_attributes_for_oid(
                        (x509.oid.NameOID.COMMON_NAME)
                    )[0].value

                except BaseException as err:
                    logger.warning(f"Cannot get Common Name: {err}")

                # Collect Certificate's Subject Alternative Names

                ssl_cert_subject_alt_names = None
                try:
                    ssl_cert_subject_alt_names = ssl_cert_deserialized.extensions.get_extension_for_oid(
                        x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                    )

                except cryptography.x509.extensions.ExtensionNotFound as err:
                    logger.warning(f"Cannot get Subject Alternative Names: {err}")

                self.__cert_sans = []
                list_of_sans = [x509.IPAddress, x509.DNSName, x509.RFC822Name]

                # Set list of overrides for SANs
                if ssl_cert_subject_alt_names:
                    for entry in list_of_sans:
                        try:
                            sans = ssl_cert_subject_alt_names.value.get_values_for_type(entry)
                            self.__cert_sans.extend([str(san) for san in sans])

                        except:
                            logger.warning(f"There is no Extensions for {entry}")

                # Set list of overides for CN
                if ssl_cert_common_name:
                    self.__cert_sans.append(ssl_cert_common_name)

                # Set auto overrides
                for san in self.__cert_sans:
                    self.__options.append(("grpc.ssl_target_name_override", san))

                # Set empty override if neither CN ans SARs exist
                if not ssl_cert_common_name and not self.__cert_sans:
                    self.__options.append(("grpc.ssl_target_name_override", ""))

                logger.warning("ssl_target_name_override is applied, should be used for testing only!")

            # Set up SSL channel credentials
            if self.__path_key and self.__path_root:
                cert = grpc.ssl_channel_credentials(
                    root_certificates=root_cert,
                    private_key=key,
                    certificate_chain=ssl_cert,
                )

            else:
                cert = grpc.ssl_channel_credentials(ssl_cert)

            # Build composed credentials if needed
            if self.__token:
                call_credentials = grpc.access_token_call_credentials(access_token=self.__token)
                credentials = grpc.composite_channel_credentials(cert, call_credentials)

            else:
                credentials = cert

            # Print if debug enabled
            debug_gnmi_msg(self.__debug, self.__target_path, "GRPC Target")
            debug_gnmi_msg(self.__debug, self.__options, "GRPC Channel options")

            self.__channel = grpc.secure_channel(self.__target_path, credentials=credentials, options=self.__options)

        if timeout is None:
            timeout = self.__gnmi_timeout
        if timeout is None or timeout > 0:
            self.wait_for_connect(timeout)
        self.__stub = gNMIStub(self.__channel)

        caps = self.capabilities()
        if "supported_encodings" in caps:
            self.__supported_encodings = caps["supported_encodings"]
            # Automatically pick encoding, in order of prefence
            for p in ["json", "json_ietf", "bytes", "proto", "ascii"]:
                if p in self.__supported_encodings:
                    self.__encoding = p
                    logger.info(f"Selected encoding '{p}' based on capabilities")
                    break
        else:
            logger.warning(f"Unable to detect supported encodings, defaulting to '{self.__encoding}'")

        return self

    def wait_for_connect(self, timeout: int):
        """
        Wait for the gNMI connection to the server to come up, with given timeout
        """
        try:
            grpc.channel_ready_future(self.__channel).result(timeout=timeout)

        except grpc.FutureTimeoutError:
            if not self.__insecure:
                logger.error("Failed to setup gRPC channel, trying change cipher")

                try:
                    os.environ["GRPC_SSL_CIPHER_SUITES"] = "HIGH"
                    grpc.channel_ready_future(self.__channel).result(timeout=timeout)

                except grpc.FutureTimeoutError:
                    raise

            else:
                raise

    def capabilities(self):
        """
        Collecting the gNMI capabilities of the network device.
        There are no arguments needed for this call
        """
        logger.info("Collecting Capabilities...")

        try:
            gnmi_message_request = CapabilityRequest()
            debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

            gnmi_message_response = self.__stub.Capabilities(gnmi_message_request, metadata=self.__metadata)
            debug_gnmi_msg(self.__debug, gnmi_message_response, "gNMI response")

            if gnmi_message_response:
                response = {}

                if gnmi_message_response.supported_models:
                    response.update({"supported_models": []})

                    for ree in gnmi_message_response.supported_models:
                        response["supported_models"].append(
                            {
                                "name": ree.name,
                                "organization": ree.organization,
                                "version": ree.version,
                            }
                        )

                if gnmi_message_response.supported_encodings:
                    response.update({"supported_encodings": []})

                    for ree in gnmi_message_response.supported_encodings:
                        if ree == 0:
                            dree = "json"
                        elif ree == 1:
                            dree = "bytes"
                        elif ree == 2:
                            dree = "proto"
                        elif ree == 3:
                            dree = "ascii"
                        else:
                            dree = "json_ietf"

                        response["supported_encodings"].append(dree)

                if gnmi_message_response.gNMI_version:
                    response.update({"gnmi_version": gnmi_message_response.gNMI_version})

            logger.info(f"Collection of Capabilities is successfull")

            return response

        except grpc._channel._InactiveRpcError as err:
            logger.critical(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}")
            raise gNMIException(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}", err)

        except:
            logger.error("Collection of Capabilities is failed.")

            return None

    def convert_encoding(self, requested_encoding: str, is_encoding_explicitly_set: bool = False):
        if (
            not is_encoding_explicitly_set
            and requested_encoding
            and self.__supported_encodings
            and requested_encoding.lower() not in self.__supported_encodings
        ):
            raise ValueError(
                f"Requested encoding '{requested_encoding}' not in supported encodings '{self.__supported_encodings}'"
            )

        encoding = requested_encoding or self.__encoding
        return Encoding.Value(encoding.upper())  # may raise ValueError

    def get(
        self,
        prefix: str = None,
        path: list = None,
        target: str = None,
        datatype: str = "all",
        encoding: str = None,
    ):
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
        logger.info("Collecting info from requested paths (Get operation)...")

        # Set Protobuf value for information type
        try:
            pb_datatype = GetRequest.DataType.Value(datatype.upper())
        except ValueError:
            logger.error(
                f"The GetRequest data type \"{datatype}\" is not within the defined range. Using default type 'all'."
            )
            pb_datatype = 0

        # Set Protobuf value for encoding
        pb_encoding = self.convert_encoding(encoding)

        # Gnmi PREFIX
        try:
            protobuf_prefix = gnmi_path_generator(prefix, target)

        except Exception as e:
            logger.error("Conversion of gNMI prefix to the Protobuf format failed")
            raise gNMIException("Conversion of gNMI prefix to the Protobuf format failed", e)

        # Gnmi PATH
        try:
            if not path:
                protobuf_paths = []
                protobuf_paths.append(gnmi_path_generator(path))
            else:
                protobuf_paths = [gnmi_path_generator(pe) for pe in path]

        except Exception as e:
            logger.error("Conversion of gNMI paths to the Protobuf format failed")
            raise gNMIException("Conversion of gNMI paths to the Protobuf format failed", e)

        try:
            if prefix is None and target is None:
                gnmi_message_request = GetRequest(
                    path=protobuf_paths,
                    type=pb_datatype,
                    encoding=pb_encoding,
                )
            else:
                gnmi_message_request = GetRequest(
                    prefix=protobuf_prefix,
                    path=protobuf_paths,
                    type=pb_datatype,
                    encoding=pb_encoding,
                )
            debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

            gnmi_message_response = self.__stub.Get(gnmi_message_request, metadata=self.__metadata)
            debug_gnmi_msg(self.__debug, gnmi_message_response, "gNMI response")

            if gnmi_message_response:
                response = {}

                ## Message GetRespone, Key notification
                if gnmi_message_response.notification:
                    response.update({"notification": []})

                    for notification in gnmi_message_response.notification:
                        notification_container = {}

                        # Message Notification, Key timestamp
                        (
                            notification_container.update({"timestamp": notification.timestamp})
                            if notification.timestamp
                            else notification_container.update({"timestamp": 0})
                        )

                        # Message Notification, Key prefix
                        (
                            notification_container.update({"prefix": gnmi_path_degenerator(notification.prefix)})
                            if notification.prefix
                            else notification_container.update({"prefix": None})
                        )

                        # Message Notification, Key alias
                        (
                            notification_container.update({"alias": notification.alias})
                            if notification.alias
                            else notification_container.update({"alias": None})
                        )

                        # Message Notification, Key target
                        notification_container.update(
                            {"target": notification.prefix.target}
                        ) if notification.prefix.target else notification_container.update({"target": None})

                        # Message Notification, Key atomic
                        notification_container.update({"atomic": notification.atomic})

                        # Message Notification, Key update
                        if notification.update:
                            notification_container.update({"update": []})

                            for update_msg in notification.update:
                                update_container = {}

                                # Message Update, Key path
                                (
                                    update_container.update({"path": gnmi_path_degenerator(update_msg.path)})
                                    if update_msg.path
                                    else update_container.update({"path": None})
                                )

                                # Message Update, Key val
                                if update_msg.HasField("val"):
                                    if update_msg.val.HasField("json_ietf_val"):
                                        update_container.update(
                                            {"val": process_potentially_json_value(update_msg.val.json_ietf_val)}
                                        )

                                    elif update_msg.val.HasField("json_val"):
                                        update_container.update(
                                            {"val": process_potentially_json_value(update_msg.val.json_val)}
                                        )

                                    elif update_msg.val.HasField("string_val"):
                                        update_container.update({"val": update_msg.val.string_val})

                                    elif update_msg.val.HasField("int_val"):
                                        update_container.update({"val": update_msg.val.int_val})

                                    elif update_msg.val.HasField("uint_val"):
                                        update_container.update({"val": update_msg.val.uint_val})

                                    elif update_msg.val.HasField("bool_val"):
                                        update_container.update({"val": update_msg.val.bool_val})

                                    elif update_msg.val.HasField("float_val"):
                                        update_container.update({"val": update_msg.val.float_val})

                                    elif update_msg.val.HasField("decimal_val"):
                                        update_container.update({"val": update_msg.val.decimal_val})

                                    elif update_msg.val.HasField("any_val"):
                                        update_container.update({"val": update_msg.val.any_val})

                                    elif update_msg.val.HasField("ascii_val"):
                                        update_container.update({"val": update_msg.val.ascii_val})

                                    elif update_msg.val.HasField("proto_bytes"):
                                        update_container.update({"val": update_msg.val.proto_bytes})

                                    elif update_msg.val.HasField("leaflist_val"):
                                        val_leaflist = update_msg.val
                                        element_val = None
                                        if all([isinstance(e, TypedValue) for e in val_leaflist.leaflist_val.element]):
                                            element_val = {}
                                            for e in val_leaflist.leaflist_val.element:
                                                if hasattr(e, "json_val"):
                                                    element_val.update(json.loads(e.json_val))
                                                elif hasattr(e, "json_ietf_val"):
                                                    element_val.update(json.loads(e.json_ietf_val))
                                                else:
                                                    raise TypeError(f"Neither json_val nor json_ietf_val found in element {e}.")
                                        elif all([isinstance(e, str) for e in val_leaflist.leaflist_val.element]):
                                            element_val = ""
                                            for e in val_leaflist.leaflist_val.element:
                                                element_val += e
                                        else:
                                            raise Exception("leaflist elements have differing types. Only str and TypedValue are supported.")

                                        update_container.update({"val": element_val})

                                notification_container["update"].append(update_container)

                        response["notification"].append(notification_container)

            return response

        except grpc._channel._InactiveRpcError as err:
            logger.critical(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}")
            raise gNMIException(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}", err)

        except Exception as e:
            logger.error("Collection of Get information failed: %s.", e)
            raise gNMIException(f"Collection of Get information failed: {e}", e)

    def set(
        self,
        delete: list = None,
        replace: list = None,
        update: list = None,
        encoding: str = None,
        prefix: str = None,
        target: str = None,
        extension: dict = None,
    ):
        """
        Changing the configuration on the destination network elements.
        Could provide a single attribute or multiple attributes.

        delete:
          - list of paths with the resources to delete. The format is the same as for get() request

        replace:
          - list of tuples where the first entry path provided as a string, and the second entry
            is a dictionary with the configuration to be configured

        update:
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
        diff_list = []

        # Set the encoding to auto-discovered value, unless overridden
        encoding = encoding or self.__encoding
        gnmi_extension = get_gnmi_extension(ext=extension)

        # Gnmi PREFIX
        try:
            protobuf_prefix = gnmi_path_generator(prefix, target)

        except Exception as e:
            logger.error("Conversion of gNMI prefix to the Protobuf format failed")
            raise gNMIException("Conversion of gNMI prefix to the Protobuf format failed", e)

        # Delete operation
        if delete:
            if isinstance(delete, list):
                try:
                    del_protobuf_paths = [gnmi_path_generator(pe) for pe in delete]
                except Exception as e:
                    logger.error(f"Conversion of gNMI paths to the Protobuf format failed")
                    raise gNMIException(f"Conversion of gNMI paths to the Protobuf format failed", e)

            else:
                logger.error(f"The provided input for Set message (delete operation) is not list.")
                raise gNMIException(f"The provided input for Set message (delete operation) is not list.")

        # Replace operation
        if replace:
            replace_msg = construct_update_message(user_list=replace, encoding=encoding)

        # Update operation
        if update:
            update_msg = construct_update_message(user_list=update, encoding=encoding)

        try:
            # Adding collection of data for diff before the change
            if self.__show_diff:
                paths_to_collect_list = []

                if delete:
                    paths_to_collect_list.extend(delete)
                if update:
                    paths_to_collect_list.extend([path_tuple[0] for path_tuple in update])
                if replace:
                    paths_to_collect_list.extend([path_tuple[0] for path_tuple in replace])

                pre_change_dict = self.get(
                    prefix=prefix,
                    path=paths_to_collect_list,
                    encoding=encoding,
                    datatype="config",
                )

            if gnmi_extension:
                if prefix is None and target is None:
                    gnmi_message_request = SetRequest(
                        delete=del_protobuf_paths,
                        update=update_msg,
                        replace=replace_msg,
                        extension=[gnmi_extension],
                    )
                else:
                    gnmi_message_request = SetRequest(
                        prefix=protobuf_prefix,
                        delete=del_protobuf_paths,
                        update=update_msg,
                        replace=replace_msg,
                        extension=[gnmi_extension],
                    )
            else:
                if prefix is None and target is None:
                    gnmi_message_request = SetRequest(
                        delete=del_protobuf_paths,
                        update=update_msg,
                        replace=replace_msg,
                    )
                else:
                    gnmi_message_request = SetRequest(
                        prefix=protobuf_prefix,
                        delete=del_protobuf_paths,
                        update=update_msg,
                        replace=replace_msg,
                    )
            debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

            gnmi_message_response = self.__stub.Set(gnmi_message_request, metadata=self.__metadata)
            debug_gnmi_msg(self.__debug, gnmi_message_response, "gNMI response")

            if gnmi_message_response:
                response = {}

                # Message SetResponse, Key timestamp
                (
                    response.update({"timestamp": gnmi_message_response.timestamp})
                    if gnmi_message_response.timestamp
                    else response.update({"timestamp": 0})
                )

                # Message SetResponse, Key prefix
                (
                    response.update({"prefix": gnmi_path_degenerator(gnmi_message_response.prefix)})
                    if gnmi_message_response.prefix
                    else response.update({"prefix": None})
                )

                # Message SetResponse, Key target
                response.update(
                    {"target": gnmi_message_response.prefix.target}
                ) if gnmi_message_response.prefix.target else response.update({"target": None})

                if gnmi_message_response.response:
                    response.update({"response": []})

                    for response_entry in gnmi_message_response.response:
                        response_container = {}

                        # Message UpdateResult, Key path
                        (
                            response_container.update({"path": gnmi_path_degenerator(response_entry.path)})
                            if response_entry.path
                            else response_container.update({"path": None})
                        )

                        ## Message UpdateResult, Key op
                        if response_entry.op:
                            if response_entry.op == 1:
                                res_op = "DELETE"
                            elif response_entry.op == 2:
                                res_op = "REPLACE"
                            elif response_entry.op == 3:
                                res_op = "UPDATE"
                            else:
                                res_op = "UNDEFINED"

                            response_container.update({"op": res_op})

                        response["response"].append(response_container)

                ## Adding collection of data for diff before the change
                if self.__show_diff:
                    post_change_dict = self.get(path=paths_to_collect_list, encoding=encoding, datatype="config")

                    is_printable = True if self.__show_diff == "print" else False

                    diff_list = diff_openconfig(
                        pre_dict=pre_change_dict,
                        post_dict=post_change_dict,
                        is_printable=is_printable,
                    )

                if diff_list and self.__show_diff == "get":
                    return response, diff_list

                else:
                    return response

            else:
                logger.error("Failed parsing the SetResponse.")
                return None

        except grpc._channel._InactiveRpcError as err:
            logger.critical(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}")
            raise gNMIException(f"GRPC ERROR Host: {self.__target_path}, Error: {err.details()}", err)
        except Exception as e:
            logger.error("Set failed: %s", e)
            raise gNMIException(f"Set failed: {e}", e)

    def set_with_retry(
        self,
        delete: list = None,
        replace: list = None,
        update: list = None,
        encoding: str = None,
        retry_delay: int = 3,
    ):
        """
        Performs a set and retries (once) after a temporary failure with StatusCode.FAILED_PRECONDITION
        """
        try:
            return self.set(delete=delete, replace=replace, update=update, encoding=encoding)
        except gNMIException as e:
            grpc_error = e.orig_exc
            if isinstance(grpc_error, grpc._channel._InactiveRpcError):
                # May happen e.g. during system startup or due to lock contention, retry once
                if grpc_error.code() == grpc.StatusCode.FAILED_PRECONDITION:
                    logger.warning("FAILED_PRECONDITION exception during set, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)

                    return self.set(delete=delete, replace=replace, update=update, encoding=encoding)

            raise

    def _build_subscriptionrequest(self, subscribe: dict, target: str = None, extension: list = None):
        if not isinstance(subscribe, dict):
            raise ValueError("Subscribe subscribe request is specified, but the value is not dict.")

        gnmi_extension = get_gnmi_extension(ext=extension)

        # use_alias
        if "use_aliases" not in subscribe:
            subscribe.update({"use_aliases": False})

        if not isinstance(subscribe["use_aliases"], bool):
            raise ValueError("Subsricbe use_aliases should have boolean type.")

        # mode
        if "mode" not in subscribe:
            subscribe.update({"mode": "stream"})

        if subscribe["mode"].lower() in {"stream", "once", "poll"}:
            if subscribe["mode"].lower() == "stream":
                subscribe_mode = 0
            elif subscribe["mode"].lower() == "once":
                subscribe_mode = 1
            elif subscribe["mode"].lower() == "poll":
                subscribe_mode = 2
        else:
            raise ValueError("Subscribe mode is out of allowed ranges.")

        # allow_aggregation
        if "allow_aggregation" not in subscribe:
            subscribe.update({"allow_aggregation": False})

        if not isinstance(subscribe["allow_aggregation"], bool):
            raise ValueError("Subscribe allow_aggregation should have boolean type.")

        # updates_only
        if "updates_only" not in subscribe:
            subscribe.update({"updates_only": False})

        if not isinstance(subscribe["updates_only"], bool):
            raise ValueError("Subsricbe updates_only should have boolean type.")

        # encoding
        is_encoding_explicitly_set = True
        if "encoding" not in subscribe:
            subscribe.update({"encoding": self.__encoding})
            is_encoding_explicitly_set = False

        pb_encoding = self.convert_encoding(subscribe["encoding"], is_encoding_explicitly_set)

        # qos
        if self.__no_qos_marking:
            subscribe.update({"qos": None})
        elif "qos" not in subscribe or not subscribe["qos"]:
            subscribe.update({"qos": {"marking": 0}})
        else:
            if not (
                isinstance(subscribe["qos"], dict)
                and "marking" in subscribe["qos"]
                and isinstance(subscribe["qos"]["marking"], int)
                and subscribe["qos"]["marking"] in list(range(0, 65))
            ):
                raise ValueError(f'Subscribe qos/marking {subscribe["qos"]["marking"]} is out of allowed ranges.')

        # use_models
        if "use_models" not in subscribe:
            subscribe.update({"use_models": []})

        if isinstance(subscribe["use_models"], list) and subscribe["use_models"]:
            raise NotImplementedError("This will be done later at some point, if there is a need.")

        # prefix
        if "prefix" not in subscribe:
            subscribe.update({"prefix": ""})

        # Create message for eveyrhting besides subscriptions
        request = SubscriptionList(
            prefix=gnmi_path_generator(subscribe["prefix"], target),
            use_aliases=subscribe["use_aliases"],
            qos=subscribe["qos"],
            mode=subscribe_mode,
            allow_aggregation=subscribe["allow_aggregation"],
            use_models=subscribe["use_models"],
            encoding=pb_encoding,
            updates_only=subscribe["updates_only"],
        )

        # subscription
        if "subscription" not in subscribe or not subscribe["subscription"]:
            raise ValueError("Subscribe:subscription value is missing.")

        for se in subscribe["subscription"]:
            # path for that subscription
            if "path" not in se:
                raise ValueError("Subscribe:subscription:path is missing")
            se_path = gnmi_path_generator(se["path"])

            # subscription entry mode; only relevent when the subscription request is stream
            if subscribe["mode"].lower() == "stream":
                if "mode" not in se:
                    raise ValueError("Subscribe:subscription:mode is missing")

                se_mode = SubscriptionMode.Value(se["mode"].upper())
            else:
                se_mode = 0

            if "sample_interval" in se and isinstance(se["sample_interval"], int):
                se_sample_interval = se["sample_interval"]
            else:
                se_sample_interval = 0

            if "suppress_redundant" in se and isinstance(se["suppress_redundant"], bool):
                se_suppress_redundant = se["suppress_redundant"]
            else:
                se_suppress_redundant = False

            if "heartbeat_interval" in se and isinstance(se["heartbeat_interval"], int):
                se_heartbeat_interval = se["heartbeat_interval"]
            else:
                se_heartbeat_interval = 0

            request.subscription.add(
                path=se_path,
                mode=se_mode,
                sample_interval=se_sample_interval,
                suppress_redundant=se_suppress_redundant,
                heartbeat_interval=se_heartbeat_interval,
            )

        if gnmi_extension:
            return SubscribeRequest(subscribe=request, extension=[gnmi_extension])

        else:
            return SubscribeRequest(subscribe=request)

    def subscribe(
        self,
        subscribe: dict = None,
        poll: bool = False,
        aliases: list = None,
        timeout: float = 0.0,
    ):
        """
        Implementation of the subscribe gNMI RPC to pool
        """
        logger.info(f"Collecting Telemetry...")

        if (subscribe and poll) or (subscribe and aliases) or (poll and aliases):
            raise gNMIException("Subscribe request supports only one request at a time.")

        if poll:
            if isinstance(poll, bool):
                if poll:
                    request = Poll()

                    gnmi_message_request = SubscribeRequest(poll=request)

            else:
                logger.error("Subscribe pool request is specificed, but the value is not boolean.")

        if aliases:
            if isinstance(aliases, list):
                request = AliasList()
                for ae in aliases:
                    if isinstance(ae, tuple):
                        if re.match("^#.*", ae[1]):
                            request.alias.add(path=gnmi_path_generator(ae[0]), alias=ae[1])

                    else:
                        raise ValueError("The alias is malformed. It should start with #...")

                gnmi_message_request = SubscribeRequest(aliases=request)

            else:
                logger.error("Subscribe aliases request is specified, but the value is not list.")

        if subscribe:
            gnmi_message_request = self._build_subscriptionrequest(subscribe)
            debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

        return self.__stub.Subscribe(self.__generator(gnmi_message_request), metadata=self.__metadata, timeout=timeout)

    def subscribe2(self, subscribe: dict, target: str = None, extension: list = None):
        """
        New High-level method to serve temetry based on recent additions
        """

        if "mode" not in subscribe:
            subscribe.update({"mode": "stream"})

        if subscribe["mode"].lower() in {"stream", "once", "poll"}:
            if subscribe["mode"].lower() == "stream":
                return self.subscribe_stream(subscribe=subscribe, target=target, extension=extension)

            elif subscribe["mode"].lower() == "poll":
                return self.subscribe_poll(subscribe=subscribe, target=target, extension=extension)

            elif subscribe["mode"].lower() == "once":
                return self.subscribe_once(subscribe=subscribe, target=target, extension=extension)

        else:
            raise gNMIException("Unknown subscription request mode.")

    def subscribe_stream(self, subscribe: dict, target: str = None, extension: list = None):
        if "mode" not in subscribe:
            subscribe["mode"] = "STREAM"
        gnmi_message_request = self._build_subscriptionrequest(subscribe, target, extension)
        debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

        return StreamSubscriber(self.__channel, gnmi_message_request, self.__metadata)

    def subscribe_poll(self, subscribe: dict, target: str = None, extension: list = None):
        if "mode" not in subscribe:
            subscribe["mode"] = "POLL"
        gnmi_message_request = self._build_subscriptionrequest(subscribe, target, extension)
        debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

        return PollSubscriber(self.__channel, gnmi_message_request, self.__metadata)

    def subscribe_once(self, subscribe: dict, target: str = None, extension: list = None):
        if "mode" not in subscribe:
            subscribe["mode"] = "ONCE"
        gnmi_message_request = self._build_subscriptionrequest(subscribe, target, extension)
        debug_gnmi_msg(self.__debug, gnmi_message_request, "gNMI request")

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

    def __init__(self, channel, request, metadata, once: bool = False):
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

        # Initialize error attribute to None. Used to catch errors in _subscribe_thread.
        self.error = None

        def enqueue_updates():
            try:
                stub = gNMIStub(channel)
                subscription = stub.Subscribe(_client_stream, metadata=metadata)
                for update in subscription:
                    self._updates.put(update)
            except Exception as error:
                self.error = error
                
                # The connection was terminated by the server. This is generally okay and
                # shouldn't raise an exception.
                if isinstance(error, grpc._channel._MultiThreadedRendezvous) and error.code() == grpc.StatusCode.CANCELLED:
                    return
                
                raise error

        self._subscribe_thread = threading.Thread(target=enqueue_updates)
        self._subscribe_thread.start()

        # Add the handling corner case for ONCE telemtry
        self._once = once
        self._once_end = False

    def _create_client_stream(self, request):
        """Iterator that yields the request, then poll messages when requested.

        This iterator is consumed by grpc. Returning from this
        iterator will cancel the RPC (grpc will send_close_from_client).
        """

        def client_stream(request):
            yield request
            while True:
                msg = self._msgs.get(block=True)
                if msg == "POLL":
                    yield SubscribeRequest(poll=Poll())
                elif msg == "STOP":
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
        resp = {"update": {}}
        while not "sync_response" in resp:
            new_resp = self._get_one_update(timeout=timeout)
            self._merge_updates(resp, new_resp)
        return resp

    def _merge_updates(self, resp, new_resp):
        if "update" in new_resp:
            for key in new_resp["update"]:
                if key.upper() in UpdateResult.Operation.keys():
                    if key not in resp["update"]:
                        resp["update"][key] = []
                    resp["update"][key] += new_resp["update"][key]
                else:
                    resp["update"][key] = new_resp["update"][key]
        if "sync_response" in new_resp:
            resp["sync_response"] = new_resp["sync_response"]

    def __iter__(self):
        return self

    def __next__(self):
        # Add handling of Once - 2
        if self._once_end:
            raise StopIteration

        result = self.next()

        # Add handling of Once - 1
        if self._once and "sync_response" in result:
            self._once_end = True

        return result

    def next(self):
        """Get the next update from the target.

        Blocks until one is available."""
        return self._next_update(timeout=None)

    def _next_update(self, timeout=None):
        ...

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
            raise TimeoutError(f"No update from target after {timeout}s")

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
        self._msgs.put("STOP")
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

    def __init__(self, *args):
        args = args + (True,)
        super().__init__(*args)

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
        self._msgs.put("POLL")
        return self._get_updates_till_sync(timeout=timeout)


class gNMIException(Exception):
    """Raised when a generic error in pygnmi occurred

    Represents a generic pygnmi library error, described with a text what
    the library tried to do. Optionally, an original exception can be added,
    so the user of this library can further distinguish what happened in the
    backend.
    """

    def __init__(self, message, orig_exc=None):
        super().__init__(message)
        self.orig_exc = orig_exc


# User-defined functions
def telemetryParser(in_message=None, debug: bool = False):
    """
    The telemetry parser is method used to covert the Protobuf message
    """
    debug_gnmi_msg(debug, in_message, "gNMI response")

    try:
        response = {}
        if in_message.HasField("update"):
            response.update({"update": {"update": []}})

            (
                response["update"].update({"timestamp": in_message.update.timestamp})
                if in_message.update.timestamp
                else in_message.update({"timestamp": 0})
            )

            if in_message.update.HasField("prefix"):
                resource_prefix = []
                for prefix_elem in in_message.update.prefix.elem:
                    tp = ""
                    if prefix_elem.name:
                        tp += prefix_elem.name

                    if prefix_elem.key:
                        # Use 'sorted' to have a consistent ordering of keys
                        for pk_name, pk_value in sorted(prefix_elem.key.items()):
                            tp += f"[{pk_name}={pk_value}]"

                    resource_prefix.append(tp)

                response["update"].update({"prefix": "/".join(resource_prefix)})

            for update_msg in in_message.update.update:
                update_container = {}

                # Message Update, Key path
                (
                    update_container.update({"path": gnmi_path_degenerator(update_msg.path)})
                    if update_msg.path
                    else update_container.update({"path": None})
                )

                if update_msg.val:
                    if update_msg.val.HasField("json_ietf_val"):
                        update_container.update({"val": json.loads(update_msg.val.json_ietf_val)})

                    elif update_msg.val.HasField("json_val"):
                        update_container.update({"val": json.loads(update_msg.val.json_val)})

                    elif update_msg.val.HasField("string_val"):
                        update_container.update({"val": update_msg.val.string_val})

                    elif update_msg.val.HasField("int_val"):
                        update_container.update({"val": update_msg.val.int_val})

                    elif update_msg.val.HasField("uint_val"):
                        update_container.update({"val": update_msg.val.uint_val})

                    elif update_msg.val.HasField("bool_val"):
                        update_container.update({"val": update_msg.val.bool_val})

                    elif update_msg.val.HasField("float_val"):
                        update_container.update({"val": update_msg.val.float_val})

                    elif update_msg.val.HasField("double_val"):
                        update_container.update({"val": update_msg.val.double_val})

                    elif update_msg.val.HasField("decimal_val"):
                        update_container.update({"val": update_msg.val.decimal_val})

                    elif update_msg.val.HasField("any_val"):
                        update_container.update({"val": update_msg.val.any_val})

                    elif update_msg.val.HasField("ascii_val"):
                        update_container.update({"val": update_msg.val.ascii_val})

                    elif update_msg.val.HasField("proto_bytes"):
                        update_container.update({"val": update_msg.val.proto_bytes})

                    elif update_msg.val.HasField("bytes_val"):
                        val_binary = "".join(format(byte, "08b") for byte in update_msg.val.bytes_val)
                        val_decimal = struct.unpack("f", struct.pack("I", int(val_binary, 2)))[0]
                        update_container.update({"val": val_decimal})

                    elif update_msg.val.HasField("leaflist_val"):
                        val_leaflist = update_msg.val
                        element_val = None
                        if all([isinstance(e, TypedValue) for e in val_leaflist.leaflist_val.element]):
                            element_val = {}
                            for e in val_leaflist.leaflist_val.element:
                                if hasattr(e, "json_val"):
                                    element_val.update(json.loads(e.json_val))
                                elif hasattr(e, "json_ietf_val"):
                                    element_val.update(json.loads(e.json_ietf_val))
                                else:
                                    raise TypeError(f"Neither json_val nor json_ietf_val found in element {e}.")
                        elif all([isinstance(e, str) for e in val_leaflist.leaflist_val.element]):
                            element_val = ""
                            for e in val_leaflist.leaflist_val.element:
                                element_val += e
                        else:
                            raise Exception("leaflist elements have differing types. Only str and TypedValue are supported.")

                        update_container.update({"val": element_val})

                response["update"]["update"].append(update_container)

            if in_message.update.delete:
                response["update"]["delete"] = []
                for delete_msg in in_message.update.delete:
                    delete_container = {}
                    resource_path = []

                    for path_elem in delete_msg.elem:
                        tp = ""
                        if path_elem.name:
                            tp += path_elem.name

                        if path_elem.key:
                            # Use 'sorted' to have a consistent ordering of keys
                            for pk_name, pk_value in sorted(path_elem.key.items()):
                                tp += f"[{pk_name}={pk_value}]"

                        resource_path.append(tp)

                    delete_container.update({"path": "/".join(resource_path)})
                    response["update"]["delete"].append(delete_container)

            return response

        elif in_message.HasField("sync_response"):
            response["sync_response"] = in_message.sync_response

            return response

    except Exception as exc:
        logger.error(f"Parsing of telemetry information is failed: {exc}")

        return None


def debug_gnmi_msg(is_printable: bool, what_to_print: str, message_name: str) -> None:
    """This helper function prints debug output"""
    if is_printable:
        try:
            columns = os.get_terminal_size().columns
        except OSError:
            # NOTE: this happens if we run an application on non-tty
            # The symptom would be OSError(25, 'Inappropriate ioctl for device')
            columns = 40
        print(message_name)
        print("-" * columns)
        print(what_to_print)
        print("-" * columns, end="\n\n\n")


def process_potentially_json_value(input_val) -> Any:
    """This helper function converts value from bytestream"""
    unprocessed_value = input_val.decode(encoding="utf-8")

    if unprocessed_value:
        try:
            processed_val = json.loads(unprocessed_value)
        except json.decoder.JSONDecodeError:
            processed_val = unprocessed_value
    else:
        processed_val = None

    return processed_val


def construct_update_message(user_list: list, encoding: str) -> list:
    """This is a helper method to construct the Update() GNMI message"""
    result = []

    if isinstance(user_list, list):
        for ue in user_list:
            if isinstance(ue, tuple):
                u_path = gnmi_path_generator(ue[0])
                u_val = json.dumps(ue[1]).encode("utf-8")
                u_ascii_val = str(ue[1]).encode("utf-8")
                encoding = encoding.lower()  # Normalize to lower case
                if encoding == "json":
                    result.append(Update(path=u_path, val=TypedValue(json_val=u_val)))
                elif encoding == "bytes":
                    result.append(Update(path=u_path, val=TypedValue(bytes_val=u_val)))
                elif encoding == "proto":
                    result.append(Update(path=u_path, val=TypedValue(proto_bytes=u_val)))
                elif encoding == "ascii":
                    result.append(Update(path=u_path, val=TypedValue(ascii_val=u_ascii_val)))
                elif encoding == "json_ietf":
                    result.append(Update(path=u_path, val=TypedValue(json_ietf_val=u_val)))
                else:
                    raise ValueError(f"Unsupported encoding: '{encoding}'")

            else:
                logger.error(f"The input element for Update message must be tuple, got {ue}.")
                raise gNMIException(f"The input element for Update message must be tuple, got {ue}.")

    else:
        logger.error(f"The provided input for Set message (replace operation) is not list.")
        raise gNMIException("The provided input for Set message (replace operation) is not list.")

    return result
