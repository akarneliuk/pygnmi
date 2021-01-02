#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient
from nornir import InitNornir
from nornir.core.task import Task, Result
import logging

# User-defined tasks
def gnmi_capabilites(task: Task) -> Result:
    with gNMIclient(target=(task.host.hostname, task.host.port), username=task.host.username,
                    password=task.host.password, insecure=True) as gc:

        r = gc.capabilities()

    return Result(host=task.host, result=r)

def gnmi_get(task: Task, path) -> Result:
    with gNMIclient(target=(task.host.hostname, task.host.port), username=task.host.username,
                    password=task.host.password, insecure=True) as gc:

        r = gc.get(path=path)

    return Result(host=task.host, result=r)

# Main
if __name__ == "__main__":
    nr = InitNornir(config_file='config.yaml')
    result = nr.run(task=gnmi_capabilites)
    result2 = nr.run(task=gnmi_get, path=['openconfig-interfaces:interfaces'])

    print(result2['gNMI-EOS1'][0])