==========================
pyGNMI: Python gNMI client
==========================

|project|_ |version|_ |tag|_ |license|_

This repository contains pure Python implementation of the gNMI client to interact with the network functions.

=====
Usage
=====
Sample code example:

.. code-block:: python3

  # Modules
  from pygnmi.client import gNMIclient

  # Variables
  host = ('169.254.255.64', '57400')

  # Body
  if __name__ == '__main__':
      with gNMIclient(target=host, username='admin', password='admin', insecure=True) as gc:
           result = gc.get(path=['openconfig-interfaces:interfaces', 'openconfig-acl:acl'])
         
      print(result)

Also integration with Nornir is supported (`refer to examples <examples/nornir>`_).

Video tutorial
--------------
Watch the detailed explanation how to use pyGNMI `in our YouTube channel <https://www.youtube.com/watch?v=NooE_uHIgys&list=PLsTgo2tBPnTwmeP9zsd8B_tZR-kbguvla>`_.


All gNMI RPCs supported
-----------------------
- Capabilities
- Get
- Set
- Subscribe

Supported operation modes
-------------------------
- insecure gRPC channel (without encryption)
- secure gRPC channel (with encryption and authentication based on certificate)

Tested Network Operating Systems (NOS)
--------------------------------------
- Arista EOS
- Nokia SR OS
- Cisco IOS XR

Network Operating Systems (NOS) in test
---------------------------------------
- Nokia SRLinux
- Cisco Nexus
- Juniper JUNOS

=======
License
=======
By using the pyGNMI tool you agree with `the license <LICENSE.txt>`_.

=======
Dev Log
=======

Release **0.3.12**:

- Minor bug fix.

Release **0.3.11**:

- Minor bug fix.

Release **0.3.10**:

- Renamed the debug mode. Add argument ``debug=True`` upon object creation to see the Protobuf messages.

Release **0.3.9**:

- Added functionality to list the full the device configuration in case the path is empty: ``get(path[])``.

Release **0.3.8**:

- Merged the proposal how to implement TLS with override for Cisco IOS XR (tested for Cisco IOS XR, to be tested for other vendors yet)
- Merged examples with TLS

Release **0.3.7**:

- Added the argument ``encoding`` as an extra key to ``Set`` operation

Release **0.3.6**:

- Added the argument ``encoding`` to ``Get`` operation

Release **0.3.5**:

- Added the example for Nornir Integration
- Added the topology diagram
- Added links to the video tutorial

Release **0.3.4**:

- Added the ``close`` method to ``gNMIClient`` class for those, who doesn't use ``with ... as ...`` context manager.

Release **0.3.3**:

- Added the functionality to pass gRPC messages to the code execution

Release **0.3.2**:

- Minor bugs fixed.

Release **0.3.1**:

- Minor bugs fixed.
- Added examples of gNMI operations.

Release **0.3.0**:

- Added new function ``telemetryParser``, which converts Protobuf messages in Python dictionary.
- Fixed the errors with the telemetry parsing.

Release **0.2.7**:

- Modified core so that telemetry is working in ``once`` and ``stream`` mode.

Release **0.2.6**:

- Added alpha version of the ``Subscribe`` operation.

Release **0.2.5**:

- Added typing hints.

Release **0.2.4**:

- Minor bugfixing.

Release **0.2.3**:

- Added support for IPv6 transport (now you can connect to the network function over IPv6).

Release **0.2.2**:

- Added conversion of the collected information over the gNMI into a Python dictionary for Set operation.

Release **0.2.1**:

- Fixing the bugs with improper Protobuf paths generation.
- Now all ``Set`` operations (``delete``, ``replace``, and ``update``) are working properly.

Releast **0.2.0**:

- Added the ``Set`` operation from gNMI specification.

Releast **0.1.9**:

- Added the property ``datatype='all'`` to the get() request. The values are per the gNMI specification: all, config, state, operatonal.

Release **0.1.8**:

- Added conversion of the collected information over the gNMI into a Python dictionary for Get operation.

Release **0.1.7**:

- Changing packages modules.

Release **0.1.6**:

- Restructuring internal context.

Release **0.1.5**:

- Minor bugfixing.

Release **0.1.4**:

- Minor bugfixing.

Release **0.1.3**:

- Minor bugfixing.

Release **0.1.2**:

- The gNMIClient is recreated as context manger.
- Tests with Nokia SR OS done, the module is working nice for insecure channel.

Release **0.1.1**:

- Added the ``Get`` operation out of gNMI specification.

Release **0.1.0**:

- The first release.

(c)2020-2021, karneliuk.com

.. |version| image:: https://img.shields.io/static/v1?label=latest&message=v0.3.12&color=success
.. _version: https://pypi.org/project/pygnmi/
.. |tag| image:: https://img.shields.io/static/v1?label=status&message=in%20development&color=yellow
.. _tag: https://pypi.org/project/pygnmi/
.. |license| image:: https://img.shields.io/static/v1?label=license&message=BSD-3-clause&color=success
.. _license: https://github.com/akarneliuk/pygnmi/blob/master/LICENSE.txt
.. |project| image:: https://img.shields.io/badge/akarneliuk%2Fpygnmi-blueviolet.svg?logo=github&color=success
.. _project: https://github.com/akarneliuk/pygnmi/