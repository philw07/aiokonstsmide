import pytest

from aiokonstsmide import codec
from aiokonstsmide.exceptions import DecodeError


def test_decode():
    # Valid messages
    msgs = [
        (
            b"\x54\x5E\x68\x80\x38\x3C\x3D\xDE\x7C\x3C\x3C\x3C",
            b"\xBC\x04\x00\x01\xE2\x40\x00\x00\x00",
        ),
        (
            b"\x54\x5E\x76\x9E\x24\x39\x31\x2B\x26\x29\xC4\x25",
            b"\xBC\x06\x1B\x13\x09\x04\x0B\xE6\x07",
        ),
        (
            b"\x54\x5F\x07\xEF\x56\x55\x53\x53\x5A\x53\x2C\x52\x37",
            b"\xBC\x05\x06\x00\x00\x09\x00\x7F\x01\x64",
        ),
        (
            b"\x54\x5E\x88\x60\xDD\xDD\xDC\xDC\xDC\xDC\xDC\xDC",
            b"\xBC\x01\x01\x00\x00\x00\x00\x00\x00",
        ),
        (
            b"\x54\x5E\x57\xBF\x02\x03\x03\x03\x03\x03\x03\x03",
            b"\xBC\x01\x00\x00\x00\x00\x00\x00\x00",
        ),
    ]
    for enc, dec in msgs:
        assert codec.decode(enc) == dec

    # Invalid empty message
    with pytest.raises(DecodeError):
        codec.decode(b"")

    # Invalid magic byte
    with pytest.raises(DecodeError):
        codec.decode(b"\x53\x5E\x68\x80\x38\x3C\x3D\xDE\x7C\x3C\x3C\x3C")

    # Invalid length
    with pytest.raises(DecodeError):
        codec.decode(b"\x54\x5F\x68\x80\x38\x3C\x3D\xDE\x7C\x3C\x3C\x3C")


def test_encode():
    # Valid messages
    msgs = [
        b"\xBC\x04\x00\x01\xE2\x40\x00\x00\x00",
        b"\xBC\x06\x1B\x13\x09\x04\x0B\xE6\x07",
        b"\xBC\x05\x06\x00\x00\x09\x00\x7F\x01\x64",
        b"\xBC\x01\x01\x00\x00\x00\x00\x00\x00",
        b"\xBC\x01\x00\x00\x00\x00\x00\x00\x00",
    ]
    for msg in msgs:
        enc = codec.encode(msg)
        assert enc[0] == 0x54
        assert enc[1] == (len(msg) + 1) ^ 0x54
        # Relying on a working decode function
        assert codec.decode(enc) == msg
