"""
Communication with the device is encoded using a simple XOR algorithm.
"""

from random import randint
from typing import List, Union

from .exceptions import DecodeError, EncodeError


def encode(data: Union[List[int], bytes]) -> bytes:
    """Encodes a plaintext message to be sent to the device."""
    if not data or len(data) == 0:
        raise EncodeError(
            "Invalid length, message to encode must be at least 1 byte long"
        )

    magic_byte = 0x54
    length = (len(data) + 1) ^ magic_byte
    key = randint(0, 255)
    enc = [magic_byte, length, key ^ magic_byte]

    for x in data:
        enc.append(x ^ key)

    return bytes(enc)


def decode(data: Union[List[int], bytes]) -> bytes:
    """Decodes an encoded message from the device."""
    if not data or len(data) < 4:
        raise DecodeError(
            "Invalid length, message to decode must be at least 4 bytes long."
        )

    if data[0] != 0x54:
        raise DecodeError("Invalid magic byte in encoded message.")

    dec_len = data[1] ^ data[0]
    if len(data) != dec_len + 2:
        raise DecodeError(
            f"Invalid length of encoded message, expected {dec_len + 3} bytes, but found {len(data)} bytes."
        )

    dec = []
    key = data[2] ^ data[0]

    for x in data[3:]:
        dec.append(x ^ key)

    return bytes(dec)
