#(c)2019-2021, karneliuk.com

# Modules
from dictdiffer import diff
from copy import deepcopy
import re


# User-defined functions
def _dict_to_xpath(input_dict: dict, parent_type_class: type, pre_parent_type_class: type = dict) -> list:
    result = []
    unique_id = ""

    if isinstance(input_dict, dict):
        for k1, v1 in input_dict.items():
            if isinstance(v1, dict):
                next_level_list = _dict_to_xpath(input_dict=v1, parent_type_class=type(v1), pre_parent_type_class=type(input_dict))

                for nested_list in next_level_list:
                    result.append(["/" + k1 + nested_list[0], nested_list[1]])

            elif isinstance(v1, list):
                for v2 in v1:
                    if isinstance(v2, dict):
                        next_level_list = _dict_to_xpath(input_dict=v2, parent_type_class=type(v2), pre_parent_type_class=type(v1))
                        
                        for nested_list in next_level_list:
                            result.append(["/" + k1 + nested_list[0], nested_list[1]])

            else:
                if pre_parent_type_class == list and parent_type_class == dict:
                    unique_id = f"[{k1}={v1}]"

                result.append(["/" + k1, v1])        

    if unique_id:
        result = [[unique_id + nl[0], nl[1]] for nl in result]

    return result


def _get_unique_id(path_list: list, temp_elem: dict) -> str:
    result = ""
    
    for path_item in path_list:
        temp_elem = temp_elem[path_item]

    for k1, v1 in temp_elem.items():
        if not isinstance(v1, dict):
            result = f"[{k1}={v1}]"

    return result


def diff_openconfig(pre_dict: dict, post_dict: dict, is_printable: bool = True) -> list:
    result = []
    diff_list = list(diff(pre_dict, post_dict))

    for entry_tuple in diff_list:
        xpath_str = ""
        pre_path_list = []

        if entry_tuple[1] and isinstance(entry_tuple[1], list):
            ## Looking for prefix attribuate
            if "notification" in entry_tuple[1]:
                while entry_tuple[1][0] != "notification":
                    pre_path_list.append(entry_tuple[1].pop(0))

                for i in range(2):
                    pre_path_list.append(entry_tuple[1].pop(0))

                temp_dict = deepcopy(post_dict)
                for elem in pre_path_list:
                    temp_dict = temp_dict[elem]

                if "prefix" in temp_dict and temp_dict["prefix"]:
                    xpath_str += "/" + temp_dict["prefix"]

            ## Looking for path attribute
            if "update" in entry_tuple[1]:
                while entry_tuple[1][0] != "update":
                    pre_path_list.append(entry_tuple[1].pop(0))

                for i in range(2):
                    pre_path_list.append(entry_tuple[1].pop(0))

                temp_dict = deepcopy(post_dict)
                for elem in pre_path_list:
                    temp_dict = temp_dict[elem]

                if "path" in temp_dict and temp_dict["path"]:
                    xpath_str += "/" + temp_dict["path"]

                ## Looking for the rest path
                if "val" in entry_tuple[1]:
                    while entry_tuple[1][0] != "val":
                        pre_path_list.append(entry_tuple[1].pop(0))

                    pre_path_list.append(entry_tuple[1].pop(0))
                    
                    for elem in entry_tuple[1]:
                        pre_path_list.append(elem)

                        if isinstance(elem, int):
                            xpath_str += _get_unique_id(path_list=pre_path_list, temp_elem=post_dict)

                        else:
                            xpath_str += "/" + elem

                if entry_tuple[0] in {"remove", "add"}:
                    ## Looking for the rest path and value
                    if entry_tuple[2] and isinstance(entry_tuple[2], list):
                        for elem_list in entry_tuple[2]:
                            pre_path_list.append(elem_list[0])

                            if entry_tuple[0] == "remove":
                                result_list = _dict_to_xpath(input_dict=elem_list[-1], parent_type_class=type(elem_list[-1]))
                                result_list = [["-", xpath_str + _get_unique_id(path_list=pre_path_list, temp_elem=pre_dict) + nl[0], nl[1]] for nl in result_list]

                            elif entry_tuple[0] == "add":
                                result_list = _dict_to_xpath(input_dict=elem_list[-1], parent_type_class=type(elem_list[-1]))
                                result_list = [["+", xpath_str + _get_unique_id(path_list=pre_path_list, temp_elem=post_dict) + nl[0], nl[1]] for nl in result_list]

                else:
                    result_list = []
                    result_list.append(["-", xpath_str, entry_tuple[2][0]])
                    result_list.append(["+", xpath_str, entry_tuple[2][1]])

            ## Adding significant config part (e.g., creating new interface entirely) -> new element in ordered list
            else:
                if entry_tuple[2] and isinstance(entry_tuple[2], list):
                    for update_msg_list in entry_tuple[2]:
                        if update_msg_list[0] == "update":
                            if len(update_msg_list) > 1 and isinstance(update_msg_list[1], list):
                                for update_content_dict in update_msg_list[1]:
                                    if "path" in update_content_dict: 
                                        xpath_str += "/" + update_content_dict["path"]

                                    if "val" in update_content_dict:
                                        result_list = _dict_to_xpath(input_dict=update_content_dict["val"], parent_type_class=type(update_content_dict["val"]))
                                        result_list = [["+", xpath_str + nl[0], nl[1]] for nl in result_list]

        if result_list:
                result.extend(result_list)

    if is_printable:
        for result_nested_list in result:
            print_str = " ".join([str(tr) for tr in result_nested_list])

            if re.match(r'^\+', print_str):
                print("\33[92m" + print_str + "\33[0m")

            else:
                print("\33[91m" + print_str + "\33[0m")

    return result