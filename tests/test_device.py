"""Tests for the scanner module."""

from unittest import mock

import pytest
from bleak.backends.device import BLEDevice

from aiokonstsmide import DeviceNotFoundError, Function, Repeat, device


@pytest.mark.asyncio
@mock.patch(
    "aiokonstsmide.device.BleakClient.is_connected", new_callable=mock.PropertyMock
)
@mock.patch("aiokonstsmide.device.BleakClient.connect")
@mock.patch("aiokonstsmide.device.BleakClient.write_gatt_char")
@mock.patch("aiokonstsmide.device.BleakClient.disconnect")
@mock.patch("bleak.BleakScanner.find_device_by_address")
async def test_connect(
    mock_fdba, mock_disconnect, mock_write_gatt_char, mock_connect, mock_is_connected
):
    # Device not available
    with pytest.raises(DeviceNotFoundError):
        mock_fdba.return_value = None
        await device.connect("f8:dc:f0:2a:d3:ff")

    # Device available
    def connect():
        mock_is_connected.return_value = True

    mock_fdba.return_value = BLEDevice("f8:dc:f0:2a:d3:ff", "Konstsmide")
    mock_connect.side_effect = connect
    mock_is_connected.return_value = False

    # Device should be connected and initial messages sent
    dev = await device.connect("f8:dc:f0:2a:d3:ff")
    mock_connect.assert_called_once()
    mock_write_gatt_char.assert_has_calls(
        [mock.call(device.CHARACTERISTIC, mock.ANY)] * 4
    )

    # Connect request is ignored if already connected
    await dev.connect()
    mock_connect.assert_called_once()

    # Device should be disconnected
    await dev.disconnect()
    mock_disconnect.assert_called_once()
    mock_connect.assert_called_once()


@pytest.mark.asyncio
@mock.patch(
    "aiokonstsmide.device.BleakClient.is_connected", new_callable=mock.PropertyMock
)
@mock.patch("aiokonstsmide.device.BleakClient.connect")
@mock.patch("aiokonstsmide.device.BleakClient.write_gatt_char")
@mock.patch("aiokonstsmide.device.BleakClient.disconnect")
@mock.patch("bleak.BleakScanner.find_device_by_address")
async def test_device_async_context_manager(
    mock_fdba, mock_disconnect, mock_write_gatt_char, mock_connect, mock_is_connected
):
    def connect():
        mock_is_connected.return_value = True

    mock_fdba.return_value = BLEDevice("f8:dc:f0:2a:d3:ff", "Konstsmide")
    mock_connect.side_effect = connect
    mock_is_connected.return_value = False

    # Device should be connected and initial messages sent
    async with device.Device("f8:dc:f0:2a:d3:ff") as dev:
        mock_connect.assert_called_once()
        mock_write_gatt_char.assert_has_calls(
            [mock.call(device.CHARACTERISTIC, mock.ANY)] * 4
        )

        # Connect request is ignored if already connected
        await dev.connect()
        mock_connect.assert_called_once()

    # Device should be disconnected
    mock_disconnect.assert_called_once()
    mock_connect.assert_called_once()


@pytest.mark.asyncio
@mock.patch(
    "aiokonstsmide.device.BleakClient.is_connected", new_callable=mock.PropertyMock
)
@mock.patch("aiokonstsmide.device.BleakClient.connect")
@mock.patch("aiokonstsmide.device.BleakClient.write_gatt_char")
@mock.patch("aiokonstsmide.device.BleakClient.disconnect")
@mock.patch("bleak.BleakScanner.find_device_by_address")
async def test_device_control_and_properties(
    mock_fdba, mock_disconnect, mock_write_gatt_char, mock_connect, mock_is_connected
):
    def connect():
        mock_is_connected.return_value = True

    mock_fdba.return_value = BLEDevice("f8:dc:f0:2a:d3:ff", "Konstsmide")
    mock_connect.side_effect = connect
    mock_is_connected.return_value = False

    # Default initial values
    async with device.Device("f8:dc:f0:2a:d3:ff") as dev:
        mock_write_gatt_char.reset_mock()

        assert dev.is_on is True
        assert dev.function == Function.Steady
        assert dev.brightness == 100
        assert dev.flash_speed == 50

        # On/off/toogle
        await dev.off()
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()
        assert dev.is_on is False

        await dev.on()
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()
        assert dev.is_on is True

        await dev.toggle()
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()
        assert dev.is_on is False

        await dev.toggle()
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()
        assert dev.is_on is True

        await dev.toggle()
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()
        assert dev.is_on is False

        # Control
        await dev.control(Function.Combination, 73, 36)
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()
        assert dev.is_on is True
        assert dev.function == Function.Combination
        assert dev.brightness == 73
        assert dev.flash_speed == 36

        # Deactivate timer - One timer - two calls due to time sync (RTC)
        await dev.deactivate_timer(1)
        assert mock_write_gatt_char.call_count == 2
        mock_write_gatt_char.reset_mock()

        # Deactivate timer - All timers
        await dev.deactivate_timer()
        assert mock_write_gatt_char.call_count == 8
        mock_write_gatt_char.reset_mock()

        # Timer
        await dev.timer(0, True, True, 10, 10, Function.Chasing, Repeat.Weekend)
        assert mock_write_gatt_char.call_count == 2
        mock_write_gatt_char.reset_mock()

        # Sync time
        await dev.sync_time()
        mock_write_gatt_char.assert_called_once()
        mock_write_gatt_char.reset_mock()

        # No write when disconnected
        mock_is_connected.return_value = False
        await dev.sync_time()
        mock_write_gatt_char.assert_not_called()

    # Different initial values
    async with device.Device(
        "f8:dc:f0:2a:d3:ff",
        on=False,
        function=Function.InWaves,
        brightness=33,
        flash_speed=99,
    ) as dev:
        mock_write_gatt_char.reset_mock()

        assert dev.is_on is False
        assert dev.function == Function.InWaves
        assert dev.brightness == 33
        assert dev.flash_speed == 99
