# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: gnmi.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import any_pb2 as google_dot_protobuf_dot_any__pb2
from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
import pygnmi.spec.v080.gnmi_ext_pb2 as gnmi__ext__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ngnmi.proto\x12\x04gnmi\x1a\x19google/protobuf/any.proto\x1a google/protobuf/descriptor.proto\x1a\x0egnmi_ext.proto\"\x96\x01\n\x0cNotification\x12\x11\n\ttimestamp\x18\x01 \x01(\x03\x12\x1a\n\x06prefix\x18\x02 \x01(\x0b\x32\n.gnmi.Path\x12\r\n\x05\x61lias\x18\x03 \x01(\t\x12\x1c\n\x06update\x18\x04 \x03(\x0b\x32\x0c.gnmi.Update\x12\x1a\n\x06\x64\x65lete\x18\x05 \x03(\x0b\x32\n.gnmi.Path\x12\x0e\n\x06\x61tomic\x18\x06 \x01(\x08\"u\n\x06Update\x12\x18\n\x04path\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12\x1e\n\x05value\x18\x02 \x01(\x0b\x32\x0b.gnmi.ValueB\x02\x18\x01\x12\x1d\n\x03val\x18\x03 \x01(\x0b\x32\x10.gnmi.TypedValue\x12\x12\n\nduplicates\x18\x04 \x01(\r\"\x83\x03\n\nTypedValue\x12\x14\n\nstring_val\x18\x01 \x01(\tH\x00\x12\x11\n\x07int_val\x18\x02 \x01(\x03H\x00\x12\x12\n\x08uint_val\x18\x03 \x01(\x04H\x00\x12\x12\n\x08\x62ool_val\x18\x04 \x01(\x08H\x00\x12\x13\n\tbytes_val\x18\x05 \x01(\x0cH\x00\x12\x17\n\tfloat_val\x18\x06 \x01(\x02\x42\x02\x18\x01H\x00\x12\x14\n\ndouble_val\x18\x0e \x01(\x01H\x00\x12*\n\x0b\x64\x65\x63imal_val\x18\x07 \x01(\x0b\x32\x0f.gnmi.Decimal64B\x02\x18\x01H\x00\x12)\n\x0cleaflist_val\x18\x08 \x01(\x0b\x32\x11.gnmi.ScalarArrayH\x00\x12\'\n\x07\x61ny_val\x18\t \x01(\x0b\x32\x14.google.protobuf.AnyH\x00\x12\x12\n\x08json_val\x18\n \x01(\x0cH\x00\x12\x17\n\rjson_ietf_val\x18\x0b \x01(\x0cH\x00\x12\x13\n\tascii_val\x18\x0c \x01(\tH\x00\x12\x15\n\x0bproto_bytes\x18\r \x01(\x0cH\x00\x42\x07\n\x05value\"Y\n\x04Path\x12\x13\n\x07\x65lement\x18\x01 \x03(\tB\x02\x18\x01\x12\x0e\n\x06origin\x18\x02 \x01(\t\x12\x1c\n\x04\x65lem\x18\x03 \x03(\x0b\x32\x0e.gnmi.PathElem\x12\x0e\n\x06target\x18\x04 \x01(\t\"j\n\x08PathElem\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\x03key\x18\x02 \x03(\x0b\x32\x17.gnmi.PathElem.KeyEntry\x1a*\n\x08KeyEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"8\n\x05Value\x12\r\n\x05value\x18\x01 \x01(\x0c\x12\x1c\n\x04type\x18\x02 \x01(\x0e\x32\x0e.gnmi.Encoding:\x02\x18\x01\"N\n\x05\x45rror\x12\x0c\n\x04\x63ode\x18\x01 \x01(\r\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\"\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32\x14.google.protobuf.Any:\x02\x18\x01\".\n\tDecimal64\x12\x0e\n\x06\x64igits\x18\x01 \x01(\x03\x12\x11\n\tprecision\x18\x02 \x01(\r\"0\n\x0bScalarArray\x12!\n\x07\x65lement\x18\x01 \x03(\x0b\x32\x10.gnmi.TypedValue\"\xb2\x01\n\x10SubscribeRequest\x12+\n\tsubscribe\x18\x01 \x01(\x0b\x32\x16.gnmi.SubscriptionListH\x00\x12\x1a\n\x04poll\x18\x03 \x01(\x0b\x32\n.gnmi.PollH\x00\x12\"\n\x07\x61liases\x18\x04 \x01(\x0b\x32\x0f.gnmi.AliasListH\x00\x12&\n\textension\x18\x05 \x03(\x0b\x32\x13.gnmi_ext.ExtensionB\t\n\x07request\"\x06\n\x04Poll\"\xa8\x01\n\x11SubscribeResponse\x12$\n\x06update\x18\x01 \x01(\x0b\x32\x12.gnmi.NotificationH\x00\x12\x17\n\rsync_response\x18\x03 \x01(\x08H\x00\x12 \n\x05\x65rror\x18\x04 \x01(\x0b\x32\x0b.gnmi.ErrorB\x02\x18\x01H\x00\x12&\n\textension\x18\x05 \x03(\x0b\x32\x13.gnmi_ext.ExtensionB\n\n\x08response\"\xd7\x02\n\x10SubscriptionList\x12\x1a\n\x06prefix\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12(\n\x0csubscription\x18\x02 \x03(\x0b\x32\x12.gnmi.Subscription\x12\x13\n\x0buse_aliases\x18\x03 \x01(\x08\x12\x1d\n\x03qos\x18\x04 \x01(\x0b\x32\x10.gnmi.QOSMarking\x12)\n\x04mode\x18\x05 \x01(\x0e\x32\x1b.gnmi.SubscriptionList.Mode\x12\x19\n\x11\x61llow_aggregation\x18\x06 \x01(\x08\x12#\n\nuse_models\x18\x07 \x03(\x0b\x32\x0f.gnmi.ModelData\x12 \n\x08\x65ncoding\x18\x08 \x01(\x0e\x32\x0e.gnmi.Encoding\x12\x14\n\x0cupdates_only\x18\t \x01(\x08\"&\n\x04Mode\x12\n\n\x06STREAM\x10\x00\x12\x08\n\x04ONCE\x10\x01\x12\x08\n\x04POLL\x10\x02\"\x9f\x01\n\x0cSubscription\x12\x18\n\x04path\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12$\n\x04mode\x18\x02 \x01(\x0e\x32\x16.gnmi.SubscriptionMode\x12\x17\n\x0fsample_interval\x18\x03 \x01(\x04\x12\x1a\n\x12suppress_redundant\x18\x04 \x01(\x08\x12\x1a\n\x12heartbeat_interval\x18\x05 \x01(\x04\"\x1d\n\nQOSMarking\x12\x0f\n\x07marking\x18\x01 \x01(\r\"0\n\x05\x41lias\x12\x18\n\x04path\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12\r\n\x05\x61lias\x18\x02 \x01(\t\"\'\n\tAliasList\x12\x1a\n\x05\x61lias\x18\x01 \x03(\x0b\x32\x0b.gnmi.Alias\"\xa9\x01\n\nSetRequest\x12\x1a\n\x06prefix\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12\x1a\n\x06\x64\x65lete\x18\x02 \x03(\x0b\x32\n.gnmi.Path\x12\x1d\n\x07replace\x18\x03 \x03(\x0b\x32\x0c.gnmi.Update\x12\x1c\n\x06update\x18\x04 \x03(\x0b\x32\x0c.gnmi.Update\x12&\n\textension\x18\x05 \x03(\x0b\x32\x13.gnmi_ext.Extension\"\xac\x01\n\x0bSetResponse\x12\x1a\n\x06prefix\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12$\n\x08response\x18\x02 \x03(\x0b\x32\x12.gnmi.UpdateResult\x12 \n\x07message\x18\x03 \x01(\x0b\x32\x0b.gnmi.ErrorB\x02\x18\x01\x12\x11\n\ttimestamp\x18\x04 \x01(\x03\x12&\n\textension\x18\x05 \x03(\x0b\x32\x13.gnmi_ext.Extension\"\xca\x01\n\x0cUpdateResult\x12\x15\n\ttimestamp\x18\x01 \x01(\x03\x42\x02\x18\x01\x12\x18\n\x04path\x18\x02 \x01(\x0b\x32\n.gnmi.Path\x12 \n\x07message\x18\x03 \x01(\x0b\x32\x0b.gnmi.ErrorB\x02\x18\x01\x12(\n\x02op\x18\x04 \x01(\x0e\x32\x1c.gnmi.UpdateResult.Operation\"=\n\tOperation\x12\x0b\n\x07INVALID\x10\x00\x12\n\n\x06\x44\x45LETE\x10\x01\x12\x0b\n\x07REPLACE\x10\x02\x12\n\n\x06UPDATE\x10\x03\"\x97\x02\n\nGetRequest\x12\x1a\n\x06prefix\x18\x01 \x01(\x0b\x32\n.gnmi.Path\x12\x18\n\x04path\x18\x02 \x03(\x0b\x32\n.gnmi.Path\x12\'\n\x04type\x18\x03 \x01(\x0e\x32\x19.gnmi.GetRequest.DataType\x12 \n\x08\x65ncoding\x18\x05 \x01(\x0e\x32\x0e.gnmi.Encoding\x12#\n\nuse_models\x18\x06 \x03(\x0b\x32\x0f.gnmi.ModelData\x12&\n\textension\x18\x07 \x03(\x0b\x32\x13.gnmi_ext.Extension\";\n\x08\x44\x61taType\x12\x07\n\x03\x41LL\x10\x00\x12\n\n\x06\x43ONFIG\x10\x01\x12\t\n\x05STATE\x10\x02\x12\x0f\n\x0bOPERATIONAL\x10\x03\"\x7f\n\x0bGetResponse\x12(\n\x0cnotification\x18\x01 \x03(\x0b\x32\x12.gnmi.Notification\x12\x1e\n\x05\x65rror\x18\x02 \x01(\x0b\x32\x0b.gnmi.ErrorB\x02\x18\x01\x12&\n\textension\x18\x03 \x03(\x0b\x32\x13.gnmi_ext.Extension\";\n\x11\x43\x61pabilityRequest\x12&\n\textension\x18\x01 \x03(\x0b\x32\x13.gnmi_ext.Extension\"\xaa\x01\n\x12\x43\x61pabilityResponse\x12)\n\x10supported_models\x18\x01 \x03(\x0b\x32\x0f.gnmi.ModelData\x12+\n\x13supported_encodings\x18\x02 \x03(\x0e\x32\x0e.gnmi.Encoding\x12\x14\n\x0cgNMI_version\x18\x03 \x01(\t\x12&\n\textension\x18\x04 \x03(\x0b\x32\x13.gnmi_ext.Extension\"@\n\tModelData\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x14\n\x0corganization\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t*D\n\x08\x45ncoding\x12\x08\n\x04JSON\x10\x00\x12\t\n\x05\x42YTES\x10\x01\x12\t\n\x05PROTO\x10\x02\x12\t\n\x05\x41SCII\x10\x03\x12\r\n\tJSON_IETF\x10\x04*A\n\x10SubscriptionMode\x12\x12\n\x0eTARGET_DEFINED\x10\x00\x12\r\n\tON_CHANGE\x10\x01\x12\n\n\x06SAMPLE\x10\x02\x32\xe3\x01\n\x04gNMI\x12\x41\n\x0c\x43\x61pabilities\x12\x17.gnmi.CapabilityRequest\x1a\x18.gnmi.CapabilityResponse\x12*\n\x03Get\x12\x10.gnmi.GetRequest\x1a\x11.gnmi.GetResponse\x12*\n\x03Set\x12\x10.gnmi.SetRequest\x1a\x11.gnmi.SetResponse\x12@\n\tSubscribe\x12\x16.gnmi.SubscribeRequest\x1a\x17.gnmi.SubscribeResponse(\x01\x30\x01\x62\x06proto3')

_ENCODING = DESCRIPTOR.enum_types_by_name['Encoding']
Encoding = enum_type_wrapper.EnumTypeWrapper(_ENCODING)
_SUBSCRIPTIONMODE = DESCRIPTOR.enum_types_by_name['SubscriptionMode']
SubscriptionMode = enum_type_wrapper.EnumTypeWrapper(_SUBSCRIPTIONMODE)
JSON = 0
BYTES = 1
PROTO = 2
ASCII = 3
JSON_IETF = 4
TARGET_DEFINED = 0
ON_CHANGE = 1
SAMPLE = 2


_NOTIFICATION = DESCRIPTOR.message_types_by_name['Notification']
_UPDATE = DESCRIPTOR.message_types_by_name['Update']
_TYPEDVALUE = DESCRIPTOR.message_types_by_name['TypedValue']
_PATH = DESCRIPTOR.message_types_by_name['Path']
_PATHELEM = DESCRIPTOR.message_types_by_name['PathElem']
_PATHELEM_KEYENTRY = _PATHELEM.nested_types_by_name['KeyEntry']
_VALUE = DESCRIPTOR.message_types_by_name['Value']
_ERROR = DESCRIPTOR.message_types_by_name['Error']
_DECIMAL64 = DESCRIPTOR.message_types_by_name['Decimal64']
_SCALARARRAY = DESCRIPTOR.message_types_by_name['ScalarArray']
_SUBSCRIBEREQUEST = DESCRIPTOR.message_types_by_name['SubscribeRequest']
_POLL = DESCRIPTOR.message_types_by_name['Poll']
_SUBSCRIBERESPONSE = DESCRIPTOR.message_types_by_name['SubscribeResponse']
_SUBSCRIPTIONLIST = DESCRIPTOR.message_types_by_name['SubscriptionList']
_SUBSCRIPTION = DESCRIPTOR.message_types_by_name['Subscription']
_QOSMARKING = DESCRIPTOR.message_types_by_name['QOSMarking']
_ALIAS = DESCRIPTOR.message_types_by_name['Alias']
_ALIASLIST = DESCRIPTOR.message_types_by_name['AliasList']
_SETREQUEST = DESCRIPTOR.message_types_by_name['SetRequest']
_SETRESPONSE = DESCRIPTOR.message_types_by_name['SetResponse']
_UPDATERESULT = DESCRIPTOR.message_types_by_name['UpdateResult']
_GETREQUEST = DESCRIPTOR.message_types_by_name['GetRequest']
_GETRESPONSE = DESCRIPTOR.message_types_by_name['GetResponse']
_CAPABILITYREQUEST = DESCRIPTOR.message_types_by_name['CapabilityRequest']
_CAPABILITYRESPONSE = DESCRIPTOR.message_types_by_name['CapabilityResponse']
_MODELDATA = DESCRIPTOR.message_types_by_name['ModelData']
_SUBSCRIPTIONLIST_MODE = _SUBSCRIPTIONLIST.enum_types_by_name['Mode']
_UPDATERESULT_OPERATION = _UPDATERESULT.enum_types_by_name['Operation']
_GETREQUEST_DATATYPE = _GETREQUEST.enum_types_by_name['DataType']
Notification = _reflection.GeneratedProtocolMessageType('Notification', (_message.Message,), {
  'DESCRIPTOR' : _NOTIFICATION,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Notification)
  })
_sym_db.RegisterMessage(Notification)

Update = _reflection.GeneratedProtocolMessageType('Update', (_message.Message,), {
  'DESCRIPTOR' : _UPDATE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Update)
  })
_sym_db.RegisterMessage(Update)

TypedValue = _reflection.GeneratedProtocolMessageType('TypedValue', (_message.Message,), {
  'DESCRIPTOR' : _TYPEDVALUE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.TypedValue)
  })
_sym_db.RegisterMessage(TypedValue)

Path = _reflection.GeneratedProtocolMessageType('Path', (_message.Message,), {
  'DESCRIPTOR' : _PATH,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Path)
  })
_sym_db.RegisterMessage(Path)

PathElem = _reflection.GeneratedProtocolMessageType('PathElem', (_message.Message,), {

  'KeyEntry' : _reflection.GeneratedProtocolMessageType('KeyEntry', (_message.Message,), {
    'DESCRIPTOR' : _PATHELEM_KEYENTRY,
    '__module__' : 'gnmi_pb2'
    # @@protoc_insertion_point(class_scope:gnmi.PathElem.KeyEntry)
    })
  ,
  'DESCRIPTOR' : _PATHELEM,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.PathElem)
  })
_sym_db.RegisterMessage(PathElem)
_sym_db.RegisterMessage(PathElem.KeyEntry)

Value = _reflection.GeneratedProtocolMessageType('Value', (_message.Message,), {
  'DESCRIPTOR' : _VALUE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Value)
  })
_sym_db.RegisterMessage(Value)

Error = _reflection.GeneratedProtocolMessageType('Error', (_message.Message,), {
  'DESCRIPTOR' : _ERROR,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Error)
  })
_sym_db.RegisterMessage(Error)

Decimal64 = _reflection.GeneratedProtocolMessageType('Decimal64', (_message.Message,), {
  'DESCRIPTOR' : _DECIMAL64,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Decimal64)
  })
_sym_db.RegisterMessage(Decimal64)

ScalarArray = _reflection.GeneratedProtocolMessageType('ScalarArray', (_message.Message,), {
  'DESCRIPTOR' : _SCALARARRAY,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.ScalarArray)
  })
_sym_db.RegisterMessage(ScalarArray)

SubscribeRequest = _reflection.GeneratedProtocolMessageType('SubscribeRequest', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBEREQUEST,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.SubscribeRequest)
  })
_sym_db.RegisterMessage(SubscribeRequest)

Poll = _reflection.GeneratedProtocolMessageType('Poll', (_message.Message,), {
  'DESCRIPTOR' : _POLL,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Poll)
  })
_sym_db.RegisterMessage(Poll)

SubscribeResponse = _reflection.GeneratedProtocolMessageType('SubscribeResponse', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIBERESPONSE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.SubscribeResponse)
  })
_sym_db.RegisterMessage(SubscribeResponse)

SubscriptionList = _reflection.GeneratedProtocolMessageType('SubscriptionList', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIPTIONLIST,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.SubscriptionList)
  })
_sym_db.RegisterMessage(SubscriptionList)

Subscription = _reflection.GeneratedProtocolMessageType('Subscription', (_message.Message,), {
  'DESCRIPTOR' : _SUBSCRIPTION,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Subscription)
  })
_sym_db.RegisterMessage(Subscription)

QOSMarking = _reflection.GeneratedProtocolMessageType('QOSMarking', (_message.Message,), {
  'DESCRIPTOR' : _QOSMARKING,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.QOSMarking)
  })
_sym_db.RegisterMessage(QOSMarking)

Alias = _reflection.GeneratedProtocolMessageType('Alias', (_message.Message,), {
  'DESCRIPTOR' : _ALIAS,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.Alias)
  })
_sym_db.RegisterMessage(Alias)

AliasList = _reflection.GeneratedProtocolMessageType('AliasList', (_message.Message,), {
  'DESCRIPTOR' : _ALIASLIST,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.AliasList)
  })
_sym_db.RegisterMessage(AliasList)

SetRequest = _reflection.GeneratedProtocolMessageType('SetRequest', (_message.Message,), {
  'DESCRIPTOR' : _SETREQUEST,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.SetRequest)
  })
_sym_db.RegisterMessage(SetRequest)

SetResponse = _reflection.GeneratedProtocolMessageType('SetResponse', (_message.Message,), {
  'DESCRIPTOR' : _SETRESPONSE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.SetResponse)
  })
_sym_db.RegisterMessage(SetResponse)

UpdateResult = _reflection.GeneratedProtocolMessageType('UpdateResult', (_message.Message,), {
  'DESCRIPTOR' : _UPDATERESULT,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.UpdateResult)
  })
_sym_db.RegisterMessage(UpdateResult)

GetRequest = _reflection.GeneratedProtocolMessageType('GetRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETREQUEST,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.GetRequest)
  })
_sym_db.RegisterMessage(GetRequest)

GetResponse = _reflection.GeneratedProtocolMessageType('GetResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETRESPONSE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.GetResponse)
  })
_sym_db.RegisterMessage(GetResponse)

CapabilityRequest = _reflection.GeneratedProtocolMessageType('CapabilityRequest', (_message.Message,), {
  'DESCRIPTOR' : _CAPABILITYREQUEST,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.CapabilityRequest)
  })
_sym_db.RegisterMessage(CapabilityRequest)

CapabilityResponse = _reflection.GeneratedProtocolMessageType('CapabilityResponse', (_message.Message,), {
  'DESCRIPTOR' : _CAPABILITYRESPONSE,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.CapabilityResponse)
  })
_sym_db.RegisterMessage(CapabilityResponse)

ModelData = _reflection.GeneratedProtocolMessageType('ModelData', (_message.Message,), {
  'DESCRIPTOR' : _MODELDATA,
  '__module__' : 'gnmi_pb2'
  # @@protoc_insertion_point(class_scope:gnmi.ModelData)
  })
_sym_db.RegisterMessage(ModelData)

_GNMI = DESCRIPTOR.services_by_name['gNMI']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _UPDATE.fields_by_name['value']._options = None
  _UPDATE.fields_by_name['value']._serialized_options = b'\030\001'
  _TYPEDVALUE.fields_by_name['float_val']._options = None
  _TYPEDVALUE.fields_by_name['float_val']._serialized_options = b'\030\001'
  _TYPEDVALUE.fields_by_name['decimal_val']._options = None
  _TYPEDVALUE.fields_by_name['decimal_val']._serialized_options = b'\030\001'
  _PATH.fields_by_name['element']._options = None
  _PATH.fields_by_name['element']._serialized_options = b'\030\001'
  _PATHELEM_KEYENTRY._options = None
  _PATHELEM_KEYENTRY._serialized_options = b'8\001'
  _VALUE._options = None
  _VALUE._serialized_options = b'\030\001'
  _ERROR._options = None
  _ERROR._serialized_options = b'\030\001'
  _SUBSCRIBERESPONSE.fields_by_name['error']._options = None
  _SUBSCRIBERESPONSE.fields_by_name['error']._serialized_options = b'\030\001'
  _SETRESPONSE.fields_by_name['message']._options = None
  _SETRESPONSE.fields_by_name['message']._serialized_options = b'\030\001'
  _UPDATERESULT.fields_by_name['timestamp']._options = None
  _UPDATERESULT.fields_by_name['timestamp']._serialized_options = b'\030\001'
  _UPDATERESULT.fields_by_name['message']._options = None
  _UPDATERESULT.fields_by_name['message']._serialized_options = b'\030\001'
  _GETRESPONSE.fields_by_name['error']._options = None
  _GETRESPONSE.fields_by_name['error']._serialized_options = b'\030\001'
  _ENCODING._serialized_start=3447
  _ENCODING._serialized_end=3515
  _SUBSCRIPTIONMODE._serialized_start=3517
  _SUBSCRIPTIONMODE._serialized_end=3582
  _NOTIFICATION._serialized_start=98
  _NOTIFICATION._serialized_end=248
  _UPDATE._serialized_start=250
  _UPDATE._serialized_end=367
  _TYPEDVALUE._serialized_start=370
  _TYPEDVALUE._serialized_end=757
  _PATH._serialized_start=759
  _PATH._serialized_end=848
  _PATHELEM._serialized_start=850
  _PATHELEM._serialized_end=956
  _PATHELEM_KEYENTRY._serialized_start=914
  _PATHELEM_KEYENTRY._serialized_end=956
  _VALUE._serialized_start=958
  _VALUE._serialized_end=1014
  _ERROR._serialized_start=1016
  _ERROR._serialized_end=1094
  _DECIMAL64._serialized_start=1096
  _DECIMAL64._serialized_end=1142
  _SCALARARRAY._serialized_start=1144
  _SCALARARRAY._serialized_end=1192
  _SUBSCRIBEREQUEST._serialized_start=1195
  _SUBSCRIBEREQUEST._serialized_end=1373
  _POLL._serialized_start=1375
  _POLL._serialized_end=1381
  _SUBSCRIBERESPONSE._serialized_start=1384
  _SUBSCRIBERESPONSE._serialized_end=1552
  _SUBSCRIPTIONLIST._serialized_start=1555
  _SUBSCRIPTIONLIST._serialized_end=1898
  _SUBSCRIPTIONLIST_MODE._serialized_start=1860
  _SUBSCRIPTIONLIST_MODE._serialized_end=1898
  _SUBSCRIPTION._serialized_start=1901
  _SUBSCRIPTION._serialized_end=2060
  _QOSMARKING._serialized_start=2062
  _QOSMARKING._serialized_end=2091
  _ALIAS._serialized_start=2093
  _ALIAS._serialized_end=2141
  _ALIASLIST._serialized_start=2143
  _ALIASLIST._serialized_end=2182
  _SETREQUEST._serialized_start=2185
  _SETREQUEST._serialized_end=2354
  _SETRESPONSE._serialized_start=2357
  _SETRESPONSE._serialized_end=2529
  _UPDATERESULT._serialized_start=2532
  _UPDATERESULT._serialized_end=2734
  _UPDATERESULT_OPERATION._serialized_start=2673
  _UPDATERESULT_OPERATION._serialized_end=2734
  _GETREQUEST._serialized_start=2737
  _GETREQUEST._serialized_end=3016
  _GETREQUEST_DATATYPE._serialized_start=2957
  _GETREQUEST_DATATYPE._serialized_end=3016
  _GETRESPONSE._serialized_start=3018
  _GETRESPONSE._serialized_end=3145
  _CAPABILITYREQUEST._serialized_start=3147
  _CAPABILITYREQUEST._serialized_end=3206
  _CAPABILITYRESPONSE._serialized_start=3209
  _CAPABILITYRESPONSE._serialized_end=3379
  _MODELDATA._serialized_start=3381
  _MODELDATA._serialized_end=3445
  _GNMI._serialized_start=3585
  _GNMI._serialized_end=3812
# @@protoc_insertion_point(module_scope)