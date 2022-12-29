"""Defines messages to be sent to a device."""

from datetime import datetime
from enum import Enum
from functools import reduce
from typing import List

MAGIC_BYTE = 0xBC


class Command(Enum):
    """Commands which can be sent to the device."""

    OnOff = 1
    Control = 2
    SetPassword = 3
    PasswordInput = 4
    Timer = 5
    Rtc = 6


class Function(Enum):
    """Functions which the device supports."""

    Keep = 0
    Combination = 1
    InWaves = 2
    Sequential = 3
    SloGlo = 4
    Chasing = 5
    SlowFade = 6
    Twinkle = 7
    Steady = 8
    FlashAlternating = 9
    FlashSynchronous = 10


class Repeat(Enum):
    """Weekdays which can be used for repeating timers."""

    Sunday = 1
    Monday = 2
    Tuesday = 4
    Wednesday = 8
    Thursday = 16
    Friday = 32
    Saturday = 64


def on_off(on: bool) -> bytes:
    """Constructs a message to turn the device on or off."""
    return bytes(
        [
            MAGIC_BYTE,
            Command.OnOff.value,
            int(on),
            0,
            0,
            0,
            0,
            0,
            0,
        ]
    )


def control(function: Function, brightness: int, flash_speed: int) -> bytes:
    """
    Constructs a message to control the function, brightness and flash speed of the device.
    The flash speed only affects the alternating and synchronous flash functions.

    NOTE: The Keep function can't be used.
    """
    if not function:
        raise ValueError("A valid function must be given")
    if function == Function.Keep:
        raise ValueError("Keep function can only be used with timers")
    if brightness is None or not (0 <= brightness <= 100):
        raise ValueError(f"Brightness must be between 0 and 100, got {brightness}")
    if flash_speed is None or not (0 <= flash_speed <= 100):
        raise ValueError(f"Flash speed must be between 0 and 100, got {flash_speed}")

    return bytes(
        [
            MAGIC_BYTE,
            Command.Control.value,
            function.value,
            brightness,
            100 - max(flash_speed, 4),
            0,
            0,
            0,
            0,
        ]
    )


def password_input(password: str) -> bytes:
    """
    Constructs a password input message.
    The password must consist of exactly six digits.

    This message has to be sent to the device first with the correct password to be able to control it.
    """
    if not password or len(password) != 6 or not password.isdigit():
        raise ValueError("The password must consist of exactly six digits")

    num = int(password)
    return bytes(
        [
            MAGIC_BYTE,
            Command.PasswordInput.value,
            (num >> 24) & 0xFF,
            (num >> 16) & 0xFF,
            (num >> 8) & 0xFF,
            num & 0xFF,
            0,
            0,
            0,
        ]
    )


def set_password(password: str) -> bytes:
    """
    Constructs a set password message.
    The password must consist of exactly six digits.
    """
    if not password or len(password) != 6 or not password.isdigit():
        raise ValueError("The password must consist of exactly six digits")

    num = int(password)
    return bytes(
        [
            MAGIC_BYTE,
            Command.SetPassword.value,
            (num >> 24) & 0xFF,
            (num >> 16) & 0xFF,
            (num >> 8) & 0xFF,
            num & 0xFF,
            0,
            0,
            0,
        ]
    )


def timer(
    num: int,
    active: bool,
    turn_on: bool,
    hour: int,
    minute: int,
    function: Function,
    repeat: List[Repeat],
    brightness: int,
) -> bytes:
    """
    Constructs a timer message.

    NOTE: The FlashAlternating and FlashSynchronous functions can't be used.
    """
    if not (0 <= num <= 7):
        raise ValueError(f"Timer number must be between 0 and 7, got {num}")
    if not (0 <= hour <= 23):
        raise ValueError(f"Hour must be between 0 and 23, got {hour}")
    if not (0 <= minute <= 59):
        raise ValueError(f"Minute must be between 0 and 59, got {minute}")
    if not function:
        raise ValueError("A valid function must be given")
    if function in [Function.FlashAlternating, Function.FlashSynchronous]:
        raise ValueError("Flash functions can't be used with timers")
    if brightness is None or not (0 <= brightness <= 100):
        raise ValueError(f"Brightness must be between 0 and 100, got {brightness}")

    if repeat is None or len(repeat) == 0:
        repeat = [0]
    else:
        repeat = [rep.value for rep in repeat]

    return bytes(
        [
            MAGIC_BYTE,
            Command.Timer.value,
            num,
            int(turn_on),
            int(active),
            hour,
            minute,
            reduce(lambda a, b: a ^ b, repeat),
            function.value,
            brightness,
        ]
    )


def rtc(date: datetime) -> bytes:
    """
    Constructs an RTC message to synchronize the date and time of the device.
    This is necessary for the timers to work correctly.
    """
    return bytes(
        [
            MAGIC_BYTE,
            Command.Rtc.value,
            date.second,
            date.minute,
            date.hour,
            date.day,
            date.month,
            date.year & 0xFF,
            (date.year >> 8) & 0xFF,
        ]
    )
