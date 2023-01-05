"""Tests for the scanner module."""

from unittest import mock

import pytest
from bleak.backends.device import BLEDevice

from aiokonstsmide import scanner


@pytest.mark.asyncio
async def test_find_devices():
    # No device
    with mock.patch("bleak.BleakScanner.discover") as mock_discover:
        mock_discover.return_value = []
        assert [d async for d in scanner.find_devices()] == []
        mock_discover.assert_called_once_with(timeout=5.0, return_adv=mock.ANY)

    # No Konstsmide device
    with mock.patch("bleak.BleakScanner.discover") as mock_discover:
        mock_discover.return_value = [
            BLEDevice("b3:c8:57:7d:fb:54", None),
            BLEDevice("72:0c:23:be:79:0c", "Test"),
        ]
        assert [d async for d in scanner.find_devices(10.0)] == []
        mock_discover.assert_called_once_with(timeout=10.0, return_adv=mock.ANY)

    # Only Konstsmide device
    with mock.patch("bleak.BleakScanner.discover") as mock_discover:
        mock_discover.return_value = [BLEDevice("5a:1d:e8:e1:44:d5", "Konstsmide")]
        assert [d async for d in scanner.find_devices(3.5)] == ["5a:1d:e8:e1:44:d5"]
        mock_discover.assert_called_once_with(timeout=3.5, return_adv=mock.ANY)

    # Mixed devices
    with mock.patch("bleak.BleakScanner.discover") as mock_discover:
        mock_discover.return_value = [
            BLEDevice("95:f9:2a:d0:e8:0c", "Konstsmide"),
            BLEDevice("ed:65:02:9e:38:3c", "Test"),
            BLEDevice("9a:f4:68:79:7b:98", None),
            BLEDevice("ef:34:51:6a:06:9f", "Konstsmide"),
        ]
        assert [d async for d in scanner.find_devices(timeout=24.36)] == [
            "95:f9:2a:d0:e8:0c",
            "ef:34:51:6a:06:9f",
        ]
        mock_discover.assert_called_once_with(timeout=24.36, return_adv=mock.ANY)


@pytest.mark.asyncio
async def test_check_address():
    # No device for address
    with mock.patch("bleak.BleakScanner.find_device_by_address") as mock_fdba:
        mock_fdba.return_value = None
        assert await scanner.check_address("e7:72:70:06:8f:50") is False
        mock_fdba.assert_called_once_with("e7:72:70:06:8f:50", timeout=5.0)

    # Other device - w/o name
    with mock.patch("bleak.BleakScanner.find_device_by_address") as mock_fdba:
        mock_fdba.return_value = BLEDevice("5e:f9:3a:e9:be:32", None)
        assert await scanner.check_address("5e:f9:3a:e9:be:32", 12.71) is False
        mock_fdba.assert_called_once_with("5e:f9:3a:e9:be:32", timeout=12.71)

    # Other device - w/ name
    with mock.patch("bleak.BleakScanner.find_device_by_address") as mock_fdba:
        mock_fdba.return_value = BLEDevice("64:aa:39:ee:5e:d3", "Test device")
        assert await scanner.check_address("64:aa:39:ee:5e:d3", timeout=1.0) is False
        mock_fdba.assert_called_once_with("64:aa:39:ee:5e:d3", timeout=1.0)

    # Konstsmide device
    with mock.patch("bleak.BleakScanner.find_device_by_address") as mock_fdba:
        mock_fdba.return_value = BLEDevice("77:89:90:c4:78:ef", "Konstsmide")
        assert await scanner.check_address("77:89:90:c4:78:ef", 5.0) is True
        mock_fdba.assert_called_once_with("77:89:90:c4:78:ef", timeout=5.0)
