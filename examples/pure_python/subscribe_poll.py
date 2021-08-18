#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient, telemetryParser

# Variables
from inventory import hosts

# Body
for host_entry in hosts:
    if host_entry["nos"] == "graphnos":
        paths = ["graphnos-frib:frib", "graphnos-interfaces:interfaces"]

        subscribes = [{
            'subscription': [{
                'path': path
            }],
            'mode': 'poll',
            'encoding': 'json_ietf'
        } for path in paths]

        prompt_msg = "\n".join([f"{i} - {path}" for i, path in enumerate(paths)] + \
                               ["Type path # to poll, or STOP: "])

        with gNMIclient(target=(host_entry["ip_address"], host_entry["port"]),
                        path_root=host_entry["path_root"], path_cert=host_entry["path_cert"],
                        path_key=host_entry["path_key"], override=host_entry["ssl_name"]) as gc:

            polls = [gc.subscribe_poll(subscribe=s) for s in subscribes]

            while True:
                cmd = input(prompt_msg)
                if cmd.isnumeric():
                    pathid = int(cmd)
                    notification = polls[pathid].get_update(timeout=5)
                    print(notification)
                elif cmd == "STOP":
                    [poll.close() for poll in polls]
                    break
