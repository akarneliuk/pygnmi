#(c)2020, Anton Karneliuk

msg = {
    'unknown_arg': 'There is no such argument. Run \'--help\' for details.',
    'help': 'The following keys are availble:\n\n  -u (--user):      Provide the username to connect to the network element\n  -p (--pass):      Provide the password to connect to the network element\n  -h (--help):      Provide the help on the available keys\n  -t (--target):    Provide the list of endpoint in \'host:port\' format\n  -o (--operation): Prvoide the type of gNMI request\n  -c (--cert):      Provide the path towards the certificate\n  --insecure:       Define whether gRPC channel is encrypted or not\n  --gnmi-path:      Provide path to the resource at the network function\n  --print:          Define whether Protobuf messages shall be printed in the STDOUT',
    'bad_host': 'The host address is malformed. It shall be provided in a format \'ip_address:grpc_port\'.',
    'not_defined_user': 'The username is not defined. The execution is terminated.',
    'not_defined_pass': 'The password is not defined.',
    'not_defined_target': 'There are no hosts provided. The execution is terminated.',
    'not_enough_arg': 'There are not enough arguments.',
    'wrong_data': 'The argument is provided in thw wrong type (e.g. string instead of integer).',
    'not_allowed_op': 'The request gNMI operation type is now allowed.',
    'not_defined_op': 'The gNMI operation type is not defined.',
    'not_defined_path': 'The gNMI path is ot defined with Get or Set operation.'
}