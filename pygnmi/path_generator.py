#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
from pygnmi.spec.gnmi_pb2 import *
import re

# User-defined functions
def gnmi_path_generator(path_in_question: list):
    gnmi_path = Path()
    keys = []
    temp_path = ''
    temp_non_modified = ''

    # Subtracting all the keys from the elements and storing them separately
    if re.match('.*?\[.+?=.+?\].*?', path_in_question):
        split_list = re.findall('.*?\[.+?=.+?\].*?', path_in_question)

        for sle in split_list:
            temp_non_modified += sle
            temp_key, temp_value = re.sub('.*?\[(.+?)\].*?', '\g<1>', sle).split('=')
            keys.append({temp_key: temp_value})
            sle = re.sub('(.*?\[).+?(\].*?)', f'\g<1>{len(keys) - 1}\g<2>', sle)
            temp_path += sle

        if len(temp_non_modified) < len (path_in_question):
            temp_path += path_in_question.replace(temp_non_modified, '')

        path_in_question = temp_path

    path_elements = path_in_question.split('/')

    for pe_entry in path_elements:
        if not re.match('.+?:.+?', pe_entry) and len(path_elements) == 1:
            sys.exit(f'You haven\'t specified either YANG module or the top-level container in \'{pe_entry}\'.')

        elif re.match('.+?:.+?', pe_entry):
            gnmi_path.origin = pe_entry.split(':')[0]
            gnmi_path.elem.add(name=pe_entry.split(':')[1])

        elif re.match('.+?\[\d+?\].*?', pe_entry):
            key_id = int(re.sub('.+?\[(\d+?)\].*?', '\g<1>', pe_entry))
            gnmi_path.elem.add(name=pe_entry.split('[')[0], key=keys[key_id])

        else:
            gnmi_path.elem.add(name=pe_entry)

    return gnmi_path