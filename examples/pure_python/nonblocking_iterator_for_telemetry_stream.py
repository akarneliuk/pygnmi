#!/usr/bin/env python
# -*- coding: utf-8 -*-
# example for integrating pygnmi client in an umbrella testtool

import sys
import logging
import time
import datetime
import traceback
import copy
import shlex
import json
import queue
import kthread

from pygnmi.client import gNMIclient, telemetryParser

class gnmiConnect:

    def __init__(self, stepDict, method="gnmi", port=50051):

        self.logger = logging.getLogger()
        logging.basicConfig(
            format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self.hostname = stepDict.get("device")
        self.port = stepDict.get("port", port)
        self.initConnectTs = datetime.datetime.now()
        self.username = stepDict.get("username")
        self.timeout = stepDict.get("timeout", 10)
        self.insecure = stepDict.get("insecure", True)
        self.override = stepDict.get("override", False)
        self.password = stepDict.get("password")
        self.connected = False
        self.connectTries = 1
        try:
            host = (self.hostname, self.port)
            self.logger.info("connect host %s", host)
            self.gc = gNMIclient(
                target=host,
                debug=True,
                username=self.username,
                password=self.password,
                insecure=self.insecure)
            self.gc.__enter__()
        except Exception as exc:
            self.logger.error("error: %s\n %s",
                exc, traceback.format_exc())
            self.logger.error(
                'Error on line %s', sys.exc_info()[-1].tb_lineno)
            self.logger.warning("connect to %s port %s failed: %s",
                                self.hostname, self.port, exc)
            raise Exception ("cannot connect")
        else:
            self.logger.info("connect succeeded to {} port {}".format(
                self.hostname, self.port))
            self.connected = True
            self.ts = []   #telemetry stream
            self.nb_ts = None

    def sendGnmiRequest(self, origCommandDataStructure, timeout=-1):

        if not self.connected:
            raise Exception ("not connected ... cannot send commands")
        self.logger.debug('sendGnmiRequest {}'.format(
            origCommandDataStructure))
        command = copy.deepcopy(origCommandDataStructure)

        if isinstance(command, str):
            self.logger.info("gnmi command string: %s", command)
            splitList = shlex.split(command)

            if len(splitList) == 1:
                if command == "capabilities":
                    response = self.gc.capabilities()
                    return json.dumps(response, indent=2)

            elif len(splitList) == 2:
                command = splitList[0]
                if command == "get":
                    path = splitList[1]
                    paths = [path]
                    response = self.gc.get(path=paths, encoding='json')
                    return json.dumps(response, indent=2)

        elif isinstance(command, dict):

            if list(command.keys())[0] == "get":
                get_dict = command["get"]
                paths = get_dict.get("paths") 
                _encoding = get_dict.get("encoding", "json_ietf") 
                try:
                    response = self.gc.get(path=paths, encoding=_encoding)
                except Exception as exc:
                    self.logger.error("error: %s\n %s",
                        exc, traceback.format_exc())
                    self.logger.error(
                        'Error on line %s', sys.exc_info()[-1].tb_lineno)
                    raise Exception (exc)
                self.logger.info('gnmi response %s', response)
                try:
                    return json.dumps(response, indent=2)
                except Exception as exc:
                    self.logger.error("error: %s\n %s",
                        exc, traceback.format_exc())
                    self.logger.error(
                        'Error on line %s', sys.exc_info()[-1].tb_lineno)
                    raise Exception ("cannot convert %s to json: %s", response, exc)

            if list(command.keys())[0] == "set":
                set_dict = command["set"]
                _json = set_dict.get("json") # fixme Yaml
                _update = [(set_dict["path"],_json)]
                response = self.gc.set(update=_update, encoding='json')
                self.logger.info('gnmi response %s', response)
                try:
                    return json.dumps(response, indent=2)
                except Exception:
                    return str(response)

            if list(command.keys())[0] == "subscribe":
                subscribe_dict = command["subscribe"]
                self.ts = self.gc.subscribe(subscribe=subscribe_dict)
                self.logger.info('gnmi telemetry_stream  type %s',
                    type(self.ts))
                self.nb_ts = Nonblocking_iterator(self.ts, self.timeout, self.logger, stop_if_timeout = True)
                self.logger.info('noneblocking  type %s timeout %s',
                   type(self.nb_ts),self.nb_ts.timeout)
                return json.dumps("telemetry data receiver intialized")

            if list(command.keys())[0] == "display_received_telemetry_data":
                _dict = command["display_received_telemetry_data"]
                timeout = int(_dict.get("timeout", 60)) * 1000
                end_ts = int(round(time.time() * 1000)) + timeout
                t_data = []
                while int(round(time.time() * 1000)) < end_ts:
                    try:
                        telemetry_entry = next(self.nb_ts)
                    except Exception as exc:
                        self.logger.warning('next exception: %s', exc)
                        break
                    if telemetry_entry:
                        t_data.append(telemetryParser(telemetry_entry))
                try:
                    return json.dumps(t_data, indent=2)
                except Exception as exc:
                    self.logger.error("error: %s\n %s",
                        exc, traceback.format_exc())
                    self.logger.error(
                        'Error on line %s', sys.exc_info()[-1].tb_lineno)
                    return json.dumps(aggr_t_data, indent=2)
        return "unknown gnmiConnect command"

    def disconnect(self):
        try:
            try:
                if self.nb_ts:
                    self.nb_ts.terminate()
            except Exception as exc:
                self.logger.warning('nonblocking ts: %s', exc)
            self.gc.close()
            self.logger.info('del %s', self.gc)
            del self.g
            self.logger.info('disconnect succeeded')
        except Exception as exc:
            self.logger.error('disconnect error: %s', exc)

class Nonblocking_iterator:
    def __init__(self, blocking_generator, timeout, logger, stop_if_timeout = False):
        self.logger = logger
        self.timeout = timeout
        self.logger.info("Nonblocking_iterator timeout %s", timeout)
        self.stop_if_timeout = stop_if_timeout
        self.msg_queue = queue.Queue()
        self.blocking_generator = blocking_generator
        self._thread = kthread.KThread(
            target=self._put_messages_from_blocking_generator_to_queue)
        self._thread.start()

    def _put_messages_from_blocking_generator_to_queue(self):
        while True:
            try:
                next_msg = next(self.blocking_generator)
                self.msg_queue.put(next_msg)
            except Exception as exc:
                self.logger.error(
                    'error reading from telemetry generator: %s', exc)
                break

    def terminate(self):
        self._thread.terminate()
        while self._thread.is_alive():
            self._thread.join()
        time.sleep(1)

    def is_alive(self):
        return self._thread.is_alive()

    def join(self):
        self._thread.join()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            _next_from_queue = self.msg_queue.get(timeout=self.timeout)
            return _next_from_queue
        except queue.Empty:
            try:
                self._thread.terminate()
                while self._thread.is_alive():
                    self._thread.join()
                time.sleep(1)
                raise Exception("timeout error")
            except Exception as exc:
                self.logger.error("__next__ %s", exc)
                pass

    def next(self):
        return self.__next__()

if __name__ == "__main__":

    stepDict = {}
    stepDict["device"] = '192.168.56.31'
    stepDict["port"] = 50051
    stepDict["vendor"] = 'gnmi'
    stepDict["method"] = 'gnmi'
    stepDict["name"] = 'gnmiConnect test'
    stepDict["timeout"] = 5
    stepDict["username"] = 'admin'
    stepDict["password"] = 'admin1'
    stepDict["insecure"] = False
    stepDict["override"] = True
    stepDict["commands"] = ['capabilities',
                             {
                                "subscribe": {
                                "subscription": [
                                    {
                                    "path": "/interfaces/interface[name=Management1]/state/counters",
                                    "mode": "target_defined"
                                    }
                                ],
                                "use_aliases": False,
                                "mode": "once",
                                "encoding": "json"
                                }
                             },
                             {
                                "display_received_telemetry_data": {
                                    "timeout": 5
                                }
                             } 
                            ]
    myClient = gnmiConnect(stepDict)
    for command in stepDict["commands"]:
        print(command)
        result = myClient.sendGnmiRequest(command)
        print(result)