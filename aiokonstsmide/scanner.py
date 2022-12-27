"""
Module for finding available Konstsmide Bluetooth devices.
"""

from typing import List

from bleak import BleakScanner

DEVICE_NAME = "konstsmide"


async def find_devices(timeout: float = 5.0) -> List[str]:
    """
    Scans for available Konstsmide Bluetooth devices.
    """
    async for device in BleakScanner.discover(timeout=timeout, return_adv=False):
        if device.name.strip().lower() == DEVICE_NAME:
            yield device.address


async def check_address(address: str, timeout: float = 5.0) -> bool:
    """
    Checks if the given address is a valid reachable Konstsmide device.
    """
    device = await BleakScanner.find_device_by_address(address, timeout=timeout)
    if device and device.name.strip().lower() == DEVICE_NAME:
        return True
    return False
