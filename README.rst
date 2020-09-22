==========================
pyGNMI: Python gNMI client
==========================
This repository contains pure Python implementation of the gNMI client to interact with the network functions.

=====
Usage
=====
The explanation of the demo:

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

Network Operating Systems (NOS) in test
---------------------------------------
- Nokia SRLinux
- Nokia SR OS

=======
License
=======
By using the pyGNMI tool you agree with `the license <LICENSE.txt>`_.

=======
Dev Log
=======
Release **0.1.1**:

- Added the ``Get`` operation out of gNMI specification.

Release **0.1.0**:

- The first release.