"""
Exceptions specific to this library.
"""


class AioKonstmideError(Exception):
    """Base error."""


class EncodeError(AioKonstmideError):
    """Tried to encode an invalid message."""


class DecodeError(AioKonstmideError):
    """Tried to decode an invalid message."""


class DeviceNotFoundError(AioKonstmideError):
    """The device couldn't be found or is not a valid Konstsmide Bluetooth device."""
