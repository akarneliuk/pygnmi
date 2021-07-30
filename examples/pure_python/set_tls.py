#!/usr/bin/env python

# Modules
from pygnmi.client import gNMIclient
import json

host = ('10.127.60.177', '57400')
set_config = [
(
    "openconfig-system:system",
    {
            "config": {
                "hostname": "BH1_P2A5"
            }
            
    }

)   

]
del_config = ["openconfig-interfaces:interfaces/interface[name=\"Optics0/0/0/0\"]"]


if __name__ == '__main__':

    with gNMIclient(target=host, username='test2', password='cisco123', path_cert='/ws/avpathak-bgl/BossHogg/openconfig/ems_BH_P2A4.pem', override='ems.cisco.com',debug=True) as gc:
        # result = gc.set(update=set_config)
        result = gc.set(delete=del_config)
        print(result)


        

