"""
Collection of unit tests to test generation of XPath
"""
import pytest

from pygnmi.path_generator import gnmi_path_generator
from pygnmi.spec.gnmi_pb2 import Path, PathElem


def compare_paths(actual: Path, expected: Path):
    assert expected.origin == actual.origin
    assert len(expected.elem) == len(actual.elem)

    for exp_elem, actual_elem in zip(expected.elem, actual.elem):
        assert exp_elem.name == actual_elem.name
        assert len(exp_elem.key) == len(actual_elem.key)
        for key in exp_elem.key:
            assert key in actual_elem.key
            assert exp_elem.key[key] == actual_elem.key[key]


test_paths = [
    # empty path, with / without an origin
    ("", Path(elem=[])),
    ("/", Path(elem=[])),
    ("rfc7951:", Path(origin="rfc7951", elem=[])),
    ("rfc7951:/", Path(origin="rfc7951", elem=[])),

    # some paths from examples/pure_python
    ("interfaces/interface[name=Management1]/state/counters",
     Path(elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Management1"}),
                PathElem(name="state"),
                PathElem(name="counters")])),

    ("/interfaces/interface[name=Management1]/state/counters",
     Path(elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Management1"}),
                PathElem(name="state"),
                PathElem(name="counters")])),

    ("openconfig-interfaces:interfaces/interface[name=Loopback1]",
     Path(origin="openconfig-interfaces",
          elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback1"})])),

    ("/openconfig-interfaces:interfaces/interface[name=Loopback1]",
     Path(origin="openconfig-interfaces",
          elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback1"})])),

    # Examples taken from https://www.rfc-editor.org/rfc/rfc8349.html
    # note intermediate elements with module names, and value with colons & slash
    ("ietf-interfaces:interfaces/"
     "interface[name=eth0]/"
     "ietf-ipv6-unicast-routing:ipv6-router-advertisements/"
     "send-advertisements/"
     "prefix-list/"
     "prefix[prefix-spec=2001:db8:0:2::/64]",
     Path(origin="ietf-interfaces",
          elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "eth0"}),
                PathElem(name="ietf-ipv6-unicast-routing:ipv6-router-advertisements"),
                PathElem(name="send-advertisements"),
                PathElem(name="prefix-list"),
                PathElem(name="prefix",
                         key={"prefix-spec": "2001:db8:0:2::/64"})])),

    # Mind the container control-plane-protocol has key made of two elements
    ("ietf-routing:routing/"
     "control-plane-protocols/"
     "control-plane-protocol[type=ietf-routing:static][name=st0]/"
     "static-routes/"
     "ietf-ipv6-unicast-routing:ipv6/"
     "route[destination-prefix=::/0]",
     Path(origin="ietf-routing",
          elem=[PathElem(name="routing"),
                PathElem(name="control-plane-protocols"),
                PathElem(name="control-plane-protocol",
                         key={"type": "ietf-routing:static",
                              "name": "st0"}),
                PathElem(name="static-routes"),
                PathElem(name="ietf-ipv6-unicast-routing:ipv6"),
                PathElem(name="route",
                         key={"destination-prefix": "::/0"})])),

    # Taken from https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/prog/configuration/1610/b_1610_programmability_cg/gnmi_protocol.html#id_84819
    ("rfc7951:openconfig-interfaces:interfaces/interface[name=Loopback111]",
     Path(origin="rfc7951",
          elem=[PathElem(name="openconfig-interfaces:interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback111"})])),

    ("legacy:oc-if:interfaces/interface[name=Loopback111]",
     Path(origin="legacy",
          elem=[PathElem(name="oc-if:interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback111"})])),

    # no origin
    ("interfaces/interface[name=Loopback111]",
     Path(elem=[PathElem(name="interfaces"),
                PathElem(name="interface",
                         key={"name": "Loopback111"})])),

]


@pytest.mark.parametrize("xpath, yangpath", test_paths)
def test_xpath(xpath, yangpath):
    compare_paths(gnmi_path_generator(xpath), yangpath)
