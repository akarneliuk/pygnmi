#!/usr/bin/env python
#(c)2019-2021, karneliuk.com

# Modules
import argparse
import re
from getpass import getpass


# Functions
def parse_args(msg):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t", "--target",
        type=str,
        required=True,
        help="Target device connection details in 'host:port' format",
    )
    parser.add_argument(
        "-u", "--user",
        type=str,
        required=True,
        help="Username to use when connecting",
        dest="username"
    )
    parser.add_argument(
        "-p", "--pass",
        type=str,
        required=False,
        help="Password to use when connecting",
        dest="password"
    )
    parser.add_argument(
        "-c", "--path_cert", type=str, required=False, help="Path to certificate chain file",
    )
    parser.add_argument(
        "-k", "--path_key", type=str, required=False, help="Path to private key file"
    )
    parser.add_argument(
        "-r", "--path_root", type=str, required=False, help="Path to root CA file"
    )
    parser.add_argument(
        "-O", "--override",
        type=str,
        required=False,
        help="Override the expected server hostname to match certificate name",
    )
    parser.add_argument(
        "-i", "--insecure",
        action="store_true",
        default=False,
        help="Set to disable TLS encryption on the gRPC channel",
    )
    parser.add_argument(
        "-o", "--operation",
        type=str,
        required=False,
        choices=[
            "capabilities", "get", "set-update", "set-replace", "set-delete",
            "subscribe-stream", "subscribe-poll", "subscribe-once", "subscribe2"
        ],
        default="capabilities",
        help="gNMI Request type",
    )
    parser.add_argument(
        "-x", "--gnmi_path",
        type=str,
        required=False,
        default="", nargs="+",
        help="gNMI paths of interest in XPath format, space separated"
    )
    parser.add_argument(
        "-d", "--datastore",
        type=str,
        required=False,
        choices=["all", "config", "operational", "state"],
        default="all", const="all", nargs="?",
        help="Which datastore to operate on",
    )
    parser.add_argument(
        "-f", "--file",
        type=str,
        required=False,
        help="Path to file containing JSON data to use in a set request",
    )
    parser.add_argument(
        "-D", "--debug",
        action="store_true",
        default=False,
        help="Set to enable printing of Protobuf messages to STDOUT",
    )
    parser.add_argument(
        "-C", "--compare",
        type=str,
        required=False,
        choices=[
            "get", "print", ""
        ],
        default="",
        help="Compare the states of the devices before and after change to show difference in XPaths' values",
    )

    args = parser.parse_args()

    targets = args.target
    try:
        if re.match(r'\[.*\]', targets):
            args.target = re.sub(r'^\[([0-9a-fA-F:]+?)\]:(\d+?)$', r'\g<1> \g<2>', targets).split(' ')
            args.target = (str(args.target[0]), int(args.target[1]))
        else:
            args.target = (str(targets.split(':')[0]), int(targets.split(':')[1]))
    except IndexError:
        parser.error(msg['bad_host'])
    except ValueError:
        parser.error(msg['wrong_data'])

    if args.operation in ("set-update", "set-replace"):
        if args.file is None:
            parser.error(f"--file is required when doing a {args.operation} operation")
        if len(args.gnmi_path) > 1:
            parser.error(f"Only one path supported when doing a {args.operation} operation")

    if not args.password:
        args.password = getpass("Device password: ")

    return args
