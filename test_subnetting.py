import pytest
from subnetting import Subnetting, CIDR, VLSM


def test_calculate_network_address():
    subnet = Subnetting("192.168.1.10", 24)
    assert subnet.network_address == "192.168.1.0"


def test_calculate_broadcast_address():
    subnet = Subnetting("192.168.1.10", 24)
    assert subnet.broadcast_address == "192.168.1.255"


def test_ip_to_binary():
    subnet = Subnetting("192.168.1.10", 24)
    binary = subnet.ip_to_binary("192.168.1.10")
    assert binary == "11000000101010000000000100001010"


def test_binary_to_ip():
    subnet = Subnetting("192.168.1.10", 24)
    ip = subnet.binary_to_ip("11000000101010000000000100001010")
    assert ip == "192.168.1.10"


def test_floor_log2():
    subnet = Subnetting("192.168.1.10", 24)
    assert subnet.floor_log2(8) == 3


def test_ceil_log2():
    subnet = Subnetting("192.168.1.10", 24)
    assert subnet.ceil_log2(9) == 4


def test_cidr_calculate_subnets():
    cidr = CIDR("192.168.1.0", 24)
    subnets = cidr.calculate_subnets(4)
    expected_subnets = [
        {"Địa chỉ mạng": "192.168.1.0/26", "Dải địa chỉ": "192.168.1.1 - 192.168.1.62", "Địa chỉ broadcast": "192.168.1.63", "Số lượng host": 62},
        {"Địa chỉ mạng": "192.168.1.64/26", "Dải địa chỉ": "192.168.1.65 - 192.168.1.126", "Địa chỉ broadcast": "192.168.1.127", "Số lượng host": 62},
        {"Địa chỉ mạng": "192.168.1.128/26", "Dải địa chỉ": "192.168.1.129 - 192.168.1.190", "Địa chỉ broadcast": "192.168.1.191", "Số lượng host": 62},
        {"Địa chỉ mạng": "192.168.1.192/26", "Dải địa chỉ": "192.168.1.193 - 192.168.1.254", "Địa chỉ broadcast": "192.168.1.255", "Số lượng host": 62},
    ]
    assert subnets == expected_subnets


def test_vlsm_calculate_subnets():
    vlsm = VLSM("192.168.1.0", 24)
    host_requirements = [60, 30, 10]
    subnets = vlsm.calculate_subnets(host_requirements)
    expected_subnets = [
        {"Địa chỉ mạng": "192.168.1.0/26", "Dải địa chỉ": "192.168.1.1 - 192.168.1.62", "Địa chỉ broadcast": "192.168.1.63", "Số lượng host": 62},
        {"Địa chỉ mạng": "192.168.1.64/26", "Dải địa chỉ": "192.168.1.65 - 192.168.1.126", "Địa chỉ broadcast": "192.168.1.127", "Số lượng host": 62},
        {"Địa chỉ mạng": "192.168.1.128/28", "Dải địa chỉ": "192.168.1.129 - 192.168.1.142", "Địa chỉ broadcast": "192.168.1.143", "Số lượng host": 14},
    ]
    assert subnets == expected_subnets
