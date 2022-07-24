"""Collection of unit tests to test the generation of Extensions"""
# Modules
from pygnmi.create_gnmi_extension import get_gnmi_extension


# Statics
EXT1 = {
        'history': {
            'snapshot_time': 1626166020000000000
        }
       }

EXT2 = {
        'history': {
            'snapshot_time': '2021-07-13T09:47:00Z'
        }
       }

EXT3 = {
        'history': {
            'range': {
                'start': '2021-07-13T09:47:00Z',
                'end': '2021-07-13T09:51:00Z'
            }
        }
       }

EXT4 = {
        'history': {
            'range': {
                'start': 1626166020000000000,
                'end': 1626166260000000000
            }
        }
       }

EXT5 = {}

EXT6 = None


# Tests
def test_extension_history_snapshot_time_ns(ext=EXT1):
    """Unit test to verify time provied in ns is properly set
    for /extension/history/snapshot_time key"""
    gnmi_ext = get_gnmi_extension(ext)
    assert isinstance(gnmi_ext.history.snapshot_time, int)


def test_extension_history_snapshot_time_str(ext=EXT2):
    """Unit test to verify time provied as a string is properly set
    for /extension/history/snapshot_time key"""
    gnmi_ext = get_gnmi_extension(ext)
    assert isinstance(gnmi_ext.history.snapshot_time, int)


def test_extension_history_range_ns(ext=EXT3):
    """Unit test to verify time provied in ns is properly set
    for /extension/history/range/{start,end} keys"""
    gnmi_ext = get_gnmi_extension(ext)
    assert isinstance(gnmi_ext.history.range.start, int)
    assert isinstance(gnmi_ext.history.range.end, int)


def test_extension_history_range_str(ext=EXT4):
    """Unit test to verify time provied as a sting is properly set
    for /extension/history/range/{start,end} keys"""
    gnmi_ext = get_gnmi_extension(ext)
    assert isinstance(gnmi_ext.history.range.start, int)
    assert isinstance(gnmi_ext.history.range.end, int)


def test_extension_empty_dict(ext=EXT5):
    """Unit test to verify /extension is not created
    for empty dict"""
    gnmi_ext = get_gnmi_extension(ext)
    assert not gnmi_ext


def test_extension_empty_none(ext=EXT6):
    """Unit test to verify /extension is not created
    for None"""
    gnmi_ext = get_gnmi_extension(ext)
    assert not gnmi_ext
