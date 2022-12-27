from datetime import datetime

import pytest

from aiokonstsmide import message


def test_on_off():
    assert message.on_off(True) == b"\xBC\x01\x01\x00\x00\x00\x00\x00\x00"
    assert message.on_off(False) == b"\xBC\x01\x00\x00\x00\x00\x00\x00\x00"


def test_control():
    # Valid values
    tests = [
        (
            message.Function.Combination,
            0x23,
            0x44,
            b"\xBC\x02\x01\x23\x20\x00\x00\x00\x00",
        ),
        (message.Function.InWaves, 0x01, 0x00, b"\xBC\x02\x02\x01\x60\x00\x00\x00\x00"),
        (
            message.Function.Sequential,
            0x00,
            0x08,
            b"\xBC\x02\x03\x00\x5C\x00\x00\x00\x00",
        ),
        (message.Function.SloGlo, 0x64, 0x12, b"\xBC\x02\x04\x64\x52\x00\x00\x00\x00"),
        (message.Function.Chasing, 0x63, 0x64, b"\xBC\x02\x05\x63\x00\x00\x00\x00\x00"),
        (
            message.Function.SlowFade,
            0x19,
            0x55,
            b"\xBC\x02\x06\x19\x0F\x00\x00\x00\x00",
        ),
        (message.Function.Twinkle, 0x37, 0x01, b"\xBC\x02\x07\x37\x60\x00\x00\x00\x00"),
        (message.Function.Steady, 0x45, 0x63, b"\xBC\x02\x08\x45\x01\x00\x00\x00\x00"),
        (
            message.Function.FlashAlternating,
            0x57,
            0x50,
            b"\xBC\x02\x09\x57\x14\x00\x00\x00\x00",
        ),
        (
            message.Function.FlashSynchronous,
            0x0F,
            0x28,
            b"\xBC\x02\x0A\x0F\x3C\x00\x00\x00\x00",
        ),
    ]
    for fun, bri, spd, res in tests:
        assert message.control(fun, bri, spd) == res

    # Invalid values
    with pytest.raises(ValueError):
        message.control(message.Function.Combination, -1, 20)
    with pytest.raises(ValueError):
        message.control(message.Function.InWaves, 101, 33)

    with pytest.raises(ValueError):
        message.control(message.Function.FlashSynchronous, 79, -1)
    with pytest.raises(ValueError):
        message.control(message.Function.Sequential, 56, 101)

    with pytest.raises(ValueError):
        message.control(None, 79, 12)
    with pytest.raises(ValueError):
        message.control(message.Function.Keep, 79, 12)
    with pytest.raises(ValueError):
        message.control(message.Function.Chasing, None, 12)
    with pytest.raises(ValueError):
        message.control(message.Function.SloGlo, 79, None)


def test_password_input():
    # Valid values
    assert message.password_input("123456") == b"\xBC\x04\x00\x01\xE2\x40\x00\x00\x00"
    assert message.password_input("000000") == b"\xBC\x04\x00\x00\x00\x00\x00\x00\x00"
    assert message.password_input("999999") == b"\xBC\x04\x00\x0F\x42\x3F\x00\x00\x00"
    assert message.password_input("650238") == b"\xBC\x04\x00\x09\xEB\xFE\x00\x00\x00"

    # Invalid values
    with pytest.raises(ValueError):
        message.password_input("1234567")
    with pytest.raises(ValueError):
        message.password_input(None)
    with pytest.raises(ValueError):
        message.password_input("")
    with pytest.raises(ValueError):
        message.password_input("-123")


def test_set_password():
    assert message.set_password("123456") == b"\xBC\x03\x00\x01\xE2\x40\x00\x00\x00"
    assert message.set_password("000000") == b"\xBC\x03\x00\x00\x00\x00\x00\x00\x00"
    assert message.set_password("999999") == b"\xBC\x03\x00\x0F\x42\x3F\x00\x00\x00"
    assert message.set_password("650238") == b"\xBC\x03\x00\x09\xEB\xFE\x00\x00\x00"

    # Invalid password
    with pytest.raises(ValueError):
        message.set_password("1234567")
    with pytest.raises(ValueError):
        message.set_password(None)
    with pytest.raises(ValueError):
        message.set_password("")
    with pytest.raises(ValueError):
        message.set_password("-123")


def test_timer():
    # Valid values
    assert (
        message.timer(
            0,
            True,
            False,
            12,
            12,
            message.Function.InWaves,
            [message.Repeat.Saturday, message.Repeat.Sunday],
            100,
        )
        == b"\xBC\x05\x00\x00\x01\x0C\x0C\x41\x02\x64"
    )
    assert (
        message.timer(
            1,
            False,
            True,
            16,
            57,
            message.Function.Sequential,
            [
                message.Repeat.Monday,
                message.Repeat.Tuesday,
                message.Repeat.Wednesday,
                message.Repeat.Thursday,
                message.Repeat.Friday,
            ],
            53,
        )
        == b"\xBC\x05\x01\x01\x00\x10\x39\x3E\x03\x35"
    )
    assert (
        message.timer(
            6,
            True,
            True,
            14,
            3,
            message.Function.Keep,
            [message.Repeat.Monday, message.Repeat.Tuesday, message.Repeat.Sunday],
            10,
        )
        == b"\xBC\x05\x06\x01\x01\x0E\x03\x07\x00\x0A"
    )
    assert (
        message.timer(
            6,
            True,
            True,
            14,
            3,
            message.Function.Keep,
            [],
            10,
        )
        == b"\xBC\x05\x06\x01\x01\x0E\x03\x00\x00\x0A"
    )
    assert (
        message.timer(
            6,
            True,
            True,
            14,
            3,
            message.Function.Keep,
            None,
            10,
        )
        == b"\xBC\x05\x06\x01\x01\x0E\x03\x00\x00\x0A"
    )

    # Invalid values
    with pytest.raises(ValueError):
        message.timer(-1, True, True, 1, 1, message.Function.Chasing, [], 100)
    with pytest.raises(ValueError):
        message.timer(9, True, True, 1, 1, message.Function.Chasing, [], 100)

    with pytest.raises(ValueError):
        message.timer(0, True, True, -1, 1, message.Function.Chasing, [], 100)
    with pytest.raises(ValueError):
        message.timer(0, True, True, 24, 1, message.Function.Chasing, [], 100)
    with pytest.raises(ValueError):
        message.timer(0, True, True, 1, -1, message.Function.Chasing, [], 100)
    with pytest.raises(ValueError):
        message.timer(0, True, True, 1, 60, message.Function.Chasing, [], 100)

    with pytest.raises(ValueError):
        message.timer(0, True, True, 1, 1, message.Function.FlashAlternating, [], 100)
    with pytest.raises(ValueError):
        message.timer(0, True, True, 1, 1, message.Function.FlashSynchronous, [], 100)

    with pytest.raises(ValueError):
        message.timer(0, True, True, 1, 1, message.Function.Chasing, [], -1)
    with pytest.raises(ValueError):
        message.timer(0, True, True, 1, 1, message.Function.Chasing, [], 101)


def test_rtc():
    assert (
        message.rtc(datetime(2022, 11, 4, 9, 19, 27))
        == b"\xBC\x06\x1B\x13\x09\x04\x0B\xE6\x07"
    )
    assert (
        message.rtc(datetime(2013, 1, 1, 1, 7, 6))
        == b"\xBC\x06\x06\x07\x01\x01\x01\xDD\x07"
    )
    assert (
        message.rtc(datetime(2023, 12, 31, 23, 59, 58))
        == b"\xBC\x06\x3A\x3B\x17\x1F\x0C\xE7\x07"
    )
    assert (
        message.rtc(datetime(2048, 5, 24, 16, 43, 0))
        == b"\xBC\x06\x00\x2B\x10\x18\x05\x00\x08"
    )
