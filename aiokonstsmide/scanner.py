"""
Module for finding available Konstsmide Bluetooth devices.
"""

from typing import AsyncGenerator

from bleak import BleakScanner

DEVICE_NAME = "konstsmide"


async def find_devices(timeout: float = 5.0) -> AsyncGenerator[str, None]:
    """
    Scans for available Konstsmide Bluetooth devices.

    This function is an [asynchronous generator](https://peps.python.org/pep-0525/) and can be used with `async for`.

    :param timeout: Time in seconds to scan for devices

    :return: An asynchronous generator with addresses of found Konstsmide devices
    """
    for device in await BleakScanner.discover(timeout=timeout, return_adv=False):
        if device.name and device.name.strip().lower() == DEVICE_NAME:
            yield device.address


async def check_address(address: str, timeout: float = 5.0) -> bool:
    """
    Checks if the given address is a valid reachable Konstsmide device.

    :param address: The address of the device to check
    :param timeout: Timeout in seconds

    :return: True if the address is a valid device, False otherwise
    """
    device = await BleakScanner.find_device_by_address(address, timeout=timeout)
    if device and device.name and device.name.strip().lower() == DEVICE_NAME:
        return True
    return False
