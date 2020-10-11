#!/usr/bin/env python
#(c)2020, Anton Karneliuk

# Modules
from pygnmi.spec.gnmi_pb2 import *
import re

# User-defined functions
def gnmi_path_generator(path_in_question):
    gnmi_path = Path()
    keys = []

    # Subtracting all the keys from the elements and storing them separately
    while re.match('.*?\[.+?=.+?\].*?', path_in_question):
        temp_key, temp_value = re.sub('.*?\[(.+?)\].*?', '\g<1>', path_in_question).split('=')
        keys.append({temp_key: temp_value})
        path_in_question = re.sub('(.*?\[).+?(\].*?)', f'\g<1>{len(keys) - 1}\g<2>', path_in_question)

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