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


Supported requests
------------------
- Capabilities
- Get

Supported operation modes
-------------------------
- insecure gRPC channel (without encryption)

Tested Network Operating Systems (NOS)
--------------------------------------
- Arista EOS
- Nokia SR OS

Network Operating Systems (NOS) in test
---------------------------------------
- Nokia SRLinux

=======
License
=======
By using the pyGNMI tool you agree with `the license <LICENSE.txt>`_.

=======
Dev Log
=======
Release **0.1.8**:

- Adding conversion of the collected information over the gNMI into a Python dictionary

Release **0.1.7**:

- Changing packages modules

Release **0.1.6**:

- Restructuring internal context

Release **0.1.5**:

- Minor bugfixing

Release **0.1.4**:

- Minor bugfixing

Release **0.1.3**:

- Minor bugfixing

Release **0.1.2**:

- The gNMIClient is recreated as context manger.
- Tests with Nokia SR OS done, the module is working nice for insecure channel.

Release **0.1.1**:

- Added the ``Get`` operation out of gNMI specification.

Release **0.1.0**:

- The first release.

.. |version| image:: https://img.shields.io/static/v1?label=latest&message=v0.1.8&color=success
.. _version: https://pypi.org/project/pygnmi/
.. |tag| image:: https://img.shields.io/static/v1?label=status&message=in%20development&color=yellow
.. _tag: https://pypi.org/project/pygnmi/
.. |license| image:: https://img.shields.io/static/v1?label=license&message=BSD-3-clause&color=success
.. _license: https://github.com/akarneliuk/pygnmi/blob/master/LICENSE.txt
.. |project| image:: https://img.shields.io/badge/akarneliuk%2Fpygnmi-blueviolet.svg?logo=github&color=success
.. _project: https://github.com/akarneliuk/pygnmi/blob/master/LICENSE.txt