"""
Module to process arguments used in pygnmi cli
"""


# Modules
import argparse
import re
from getpass import getpass


# Functions
def parse_args(msg):
    """
    Function to collect user arguments when using pygnmi cli
    """
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
        required=False,
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
        "--token",
        type=str,
        required=False,
        help="Specify the token for token-based authentication",
    )
    parser.add_argument(
        "-c", "--path-cert",
        type=str,
        required=False,
        help="Path to certificate chain file",
    )
    parser.add_argument(
        "-k", "--path-key",
        type=str,
        required=False,
        help="Path to private key file"
    )
    parser.add_argument(
        "-r", "--path-root",
        type=str,
        required=False,
        help="Path to root CA file"
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
        "--skip-verify",
        action="store_true",
        default=False,
        help="Set to disable SSL certificate valication on the encrypted gRPC channel",
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
        "-x", "--gnmi-path",
        type=str,
        required=False,
        default="", nargs="+",
        help="gNMI paths of interest in XPath format, space separated"
    )
    parser.add_argument(
        "--gnmi-path-target",
        type=str,
        required=False,
        help="Set target for GNMI path if it is different to the endpoint itself."
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
        help="Compare the states of the devices before and after change to show difference",
    )
    parser.add_argument(
        "--ext-history-range-start",
        type=str,
        required=False,
        help="Specify the start timestamp for the GNMI history range",
    )
    parser.add_argument(
        "--ext-history-range-end",
        type=str,
        required=False,
        help="Specify the end timestamp for the GNMI history range",
    )
    parser.add_argument(
        "--ext-history-snapshot-time",
        type=str,
        required=False,
        help="Specify the snapshit time for the GNMI history",
    )

    args = parser.parse_args()

    targets = args.target
    try:
        if re.match(r'\[.*\]', targets):
            parsed_args = re.sub(r'^\[([0-9a-fA-F:]+?)\]:(\d+?)$', r'\g<1> \g<2>', targets)
            args.target = parsed_args.split(' ')
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

    if not args.password and not args.token:
        args.password = getpass("Device password: ")

    return args
