"""This module contains the converter of str() to GNMI Path class.
#(c)2019-2022, karneliuk.com
"""
# Modules
import re
from pygnmi.spec.gnmi_pb2 import Path


# User-defined functions
def gnmi_path_generator(path_in_question: str,
                        target: str = None):
    """Parses an XPath expression into a gNMI Path

    Accepted syntaxes:

    - "" or "/" for the empty path;

    - "origin://" or "/origin://" for the empty path with origin set to `origin` (e.g., `rfc7951`)

    - "yang-module:container/container[key=value]/other-module:leaf";
      the origin set to yang-module, and specify a key-value selector

    - "/yang-module:container/container[key=value]/other-module:leaf";
       identical to the previous

    - "/container/container[key=value]"; the origin left empty
    """
    gnmi_path = Path()
    keys = []
    temp_path = ''
    temp_non_modified = ''

    if target:
        gnmi_path.target = target

    # Subtracting all the keys from the elements and storing them separately
    if path_in_question:
        if re.match(r'.*?\[.+?=.+?\].*?', path_in_question):
            split_list = re.findall(r'.*?\[.+?=.+?\].*?', path_in_question)

            for sle in split_list:
                temp_non_modified += sle
                temp_key, temp_value = re.sub(r'.*?\[(.+?)\].*?', r'\g<1>', sle).split('=')
                keys.append({temp_key: temp_value})
                sle = re.sub(r'(.*?\[).+?(\].*?)', fr'\g<1>{len(keys) - 1}\g<2>', sle)
                temp_path += sle

            if len(temp_non_modified) < len(path_in_question):
                temp_path += path_in_question.replace(temp_non_modified, '')

            path_in_question = temp_path

        path_elements = path_in_question.split('/')
        path_elements = list(filter(None, path_elements))

        # Check if first path element contains a colon, and use that to set origin
        if path_elements and re.match('.+?:.*?', path_elements[0]):
            pe_entry = path_elements[0]
            parts = pe_entry.split(':', 1)
            gnmi_path.origin = parts[0]

            if len(parts) > 1 and parts[1]:
                path_elements[0] = parts[1]
            else:
                del path_elements[0]

        for pe_entry in path_elements:
            if re.match(r'.+?\[\d+?\]', pe_entry):
                element_keys = {}
                path_info = [re.sub(']', '', en) for en in pe_entry.split('[')]
                element = path_info.pop(0)

                for elem_key in path_info:
                    element_keys.update(keys[int(elem_key)])

                gnmi_path.elem.add(name=element, key=element_keys)

            else:
                gnmi_path.elem.add(name=pe_entry)

    return gnmi_path


def gnmi_path_degenerator(gnmi_path) -> str:
    """Parses a gNMI Path into an XPath expression
    """
    result = None
    if gnmi_path and gnmi_path.elem:
        resource_path = []
        for path_elem in gnmi_path.elem:
            temp_path = ''
            if path_elem.name:
                temp_path += path_elem.name

            if path_elem.key:
                for pk_name, pk_value in sorted(path_elem.key.items()):
                    temp_path += f'[{pk_name}={pk_value}]'

            resource_path.append(temp_path)

        result = '/'.join(resource_path)

    return result
