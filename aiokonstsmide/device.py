"""Module for communication with Konstsmide Bluetooth devices."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

from bleak import BleakClient

from . import codec, message
from .exceptions import DeviceNotFoundError
from .scanner import check_address

CHARACTERISTIC = "00001001-0000-1000-8000-00805f9b34fb"


async def connect(
    address: str,
    password: Optional[str] = None,
    on: bool = True,
    function: message.Function = message.Function.Steady,
    brightness: int = 100,
    flash_speed: int = 50,
    timeout: float = 5.0,
) -> "Device":
    """
    Connects to the device with the given address.

    Make sure to call `Device.disconnect` once you're finished,
    otherwise it will not be possible to connect to the device anymore
    unless the power is cut.

    :param address: The address of the device to connect to
    :param password: The password of the device
    :param on: If the device should be turned on or off after connecting
    :param function: The function to set after connecting
    :param brightness: The brightness to set after connecting, in the range 0 (dim) - 100 (bright)
    :param flash_speed: The flash speed to set after connecting, in the range 0 (slow) - 100 (fast)
    :param timeout: Timeout in seconds

    :return: A Device instance connected to the device with the given address
    """
    device = Device(address, password, on, function, brightness, flash_speed)
    await device.connect(timeout)
    return device


@dataclass
class Status:
    """Dataclass to hold the status of the device."""

    on: bool
    function: message.Function
    brightness: int
    flash_speed: int


class Device:
    """
    Represents a Konstsmide Bluetooth device.
    """

    def __init__(
        self,
        address: str,
        password: Optional[str] = None,
        on: bool = True,
        function: message.Function = message.Function.Steady,
        brightness: int = 100,
        flash_speed: int = 50,
    ):
        """
        Initializes a Device instance.

        :param address: The address of the device to connect to
        :param password: The password of the device
        :param on: If the device should be turned on or off after connecting
        :param function: The function to set after connecting
        :param brightness: The brightness to set after connecting, in the range 0 (dim) - 100 (bright)
        :param flash_speed: The flash speed to set after connecting, in the range 0 (slow) - 100 (fast)
        """
        self.__logger = logging.getLogger(f"{__package__}({address})")
        self.__address = address
        self.__password = password or "123456"
        self.__status = Status(on, function, brightness, flash_speed)
        self.__client: BleakClient = None
        self.__reconnect = True

    async def connect(self, timeout: float = 5.0):
        """
        Establishes a connection to the device.

        :param timeout: The timeout in seconds
        """
        if not self.__client:
            if not await check_address(self.__address):
                raise DeviceNotFoundError

            def on_disconnect(client: BleakClient):
                if self.__reconnect:
                    self.__logger.debug("Device disconnected, trying to reconnect")
                    asyncio.create_task(self.connect(timeout))

            self.__client = BleakClient(
                self.__address,
                disconnected_callback=on_disconnect,
                timeout=timeout,
            )

        self.__reconnect = True
        if not self.__client.is_connected:
            await self.__client.connect()
            if self.__client.is_connected:
                self.__logger.debug("Device connected, sending password")
                await self.__write(message.password_input(self.__password))
                self.__logger.debug("Synchronizing status")
                await self.__sync_status()
                self.__logger.debug("Synchronizing time")
                await self.sync_time()
            else:
                self.__logger.error("Failed to connect to device")

    async def __sync_status(self):
        """
        Synchronizes the status of the device.
        Since the status of the device can't be read,
        the device status is set according to the internal status.
        """
        init_state = self.__status.on

        await self.control(
            function=self.__status.function,
            brightness=self.__status.brightness,
            flash_speed=self.__status.flash_speed,
        )

        if init_state:
            await self.on()
        else:
            await self.off()

    async def disconnect(self):
        """Disconnects from the device."""
        self.__reconnect = False
        if self.__client and self.__client.is_connected:
            await self.__client.disconnect()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self.disconnect()

    @property
    def is_on(self) -> bool:
        """`True` if the device is currently on, else `False`."""
        return self.__status.on

    @property
    def brightness(self) -> int:
        """The current brightness of the device."""
        return self.__status.brightness

    @property
    def flash_speed(self) -> int:
        """The current flash speed of the device."""
        return self.__status.flash_speed

    @property
    def function(self) -> message.Function:
        """The current function of the device."""
        return self.__status.function

    async def on(self):
        """Turn on the device."""
        self.__logger.debug("Turning on")
        self.__status.on = True
        await self.__write(message.on_off(self.__status.on))

    async def off(self):
        """Turn off the device."""
        self.__logger.debug("Turning off")
        self.__status.on = False
        await self.__write(message.on_off(self.__status.on))

    async def toggle(self):
        """Toggle between on and off."""
        if self.__status.on:
            await self.off()
        else:
            await self.on()

    async def control(
        self,
        function: Optional[message.Function] = None,
        brightness: Optional[int] = None,
        flash_speed: Optional[int] = None,
    ):
        """
        Control the devices function, brightness and flash speed.
        If a parameter is None, the current value will be kept.

        :param function: The function to set
        :param brightness: The brightness to set, in the range 0 (dim) - 100 (bright)
        :param flash_speed: The flash speed to set, in the range 0 (slow) - 100 (fast)
        """
        if function:
            self.__status.function = function
        if brightness:
            self.__status.brightness = brightness
        if flash_speed:
            self.__status.flash_speed = flash_speed

        # Control turns on the device automatically
        self.__status.on = True

        self.__logger.debug(
            f"Setting function {self.__status.function.name} with brightness {self.__status.brightness} and flash speed {self.__status.flash_speed}"
        )
        await self.__write(
            message.control(
                self.__status.function,
                self.__status.brightness,
                self.__status.flash_speed,
            ),
        )

    async def deactivate_timer(self, num: Optional[int] = None):
        """
        Deactivates one specific or all timers on the device.

        :param num: The timer to deactivate, in the range 0 - 7 or `None` for all timers
        """
        if num is not None:
            await self.timer(
                num,
                False,
                False,
                0,
                0,
                message.Function.Steady,
                [],
            )
        else:
            for i in range(8):
                await self.__write(
                    message.timer(
                        i,
                        False,
                        False,
                        0,
                        0,
                        message.Function.Steady,
                        [],
                        self.__status.brightness,
                    )
                )

    async def timer(
        self,
        num: int,
        active: bool,
        turn_on: bool,
        hour: int,
        minute: int,
        function: message.Function,
        repeat: Union[message.Repeat, List[message.Repeat]],
    ):
        """
        Configures a timer on the device.
        The device has 8 built-in timers which can be set individually as desired.

        :param num: The timer to set, in the range 0 - 7
        :param active: `True` if the timer should be activated or `False` if it should be deactivated
        :param turn_on: `True` if the device should be turned on the timer is triggered, `False` otherwise
        :param hour: The hour (0-23) at which the timer triggers
        :param minute: The minute (0-59) at which the timer triggers
        :param function: The function to set when the timer is triggered
        :param repeat: On which weekdays the timer triggers
        """

        # Make sure time is synchronized
        await self.sync_time()

        # Create timer
        if isinstance(repeat, message.Repeat):
            repeat = [repeat]

        await self.__write(
            message.timer(
                num,
                active,
                turn_on,
                hour,
                minute,
                function,
                repeat,
                self.__status.brightness,
            )
        )

    async def sync_time(self):
        """
        Sends an RTC message to the device to synchronize the time.
        This is needed for timers to work correctly.

        Time is synchronized implicitly when connecting to the device or changing a timer.
        """
        await self.__write(message.rtc(datetime.now()))

    async def __write(self, message: bytes):
        """Writes the given message to the device."""
        if self.__client and self.__client.is_connected:
            self.__logger.debug(f"Sending message to device: {message.hex()}")
            enc_msg = codec.encode(message)
            await self.__client.write_gatt_char(CHARACTERISTIC, enc_msg)
        else:
            self.__logger.error(
                "Tried to send message to device, but it's disconnected!"
            )
