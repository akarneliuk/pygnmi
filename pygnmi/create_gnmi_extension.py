"""This module contains the converter of dict() to Extension() GRPC class
(c)2019-2022, karneliuk.com"""
# Modules
import datetime
from pygnmi.spec.v080.gnmi_ext_pb2 import Extension


# Functions
def get_gnmi_extension(ext: dict = None) -> list:
    """This helper function allows conversion of dictinary to Extension class"""
    result = Extension()

    # Don't build empty extension
    if not ext:
        return result

    # Create history extension
    if "history" in ext:

        if "snapshot_time" in ext["history"] and "range" in ext["history"]:
            raise Exception("Both 'snapshot_time' and 'range' are provided. Choose one")

        # Set snapshot_time key
        if "snapshot_time" in ext["history"]:
            result.history.snapshot_time = _get_time_ns_epoch(ext["history"]["snapshot_time"])

        # Set time range
        if "range" in ext["history"]:
            if not ("start" in ext["history"]["range"] and "end" in ext["history"]["range"]):
                raise Exception("'/extension/history/range' requires both 'start' and 'end'.")

            else:
                result.history.range.start = _get_time_ns_epoch(ext["history"]["range"]["start"])
                result.history.range.end = _get_time_ns_epoch(ext["history"]["range"]["end"])

    return result


def _get_time_ns_epoch(time_in_question) -> int:
    """This helper function takes input as int() or str() and returns int() with time in ns
    since the beginning of the epoch."""
    if isinstance(time_in_question, int):
        result = time_in_question

    else:
        try:
            time_stamp = datetime.datetime.strptime(time_in_question, "%Y-%m-%dT%H:%M:%SZ")
            result = int(time_stamp.timestamp() * pow(10, 9))

        except Exception as err:
            err.args += (f"Time conversion error: cannot convert {time_in_question}, use 'yyyy-mm-ddTHH:MM:SSZ' format. Details: {err}")
            raise

    return result
