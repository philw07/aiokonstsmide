"""
Connects to the device with the given address and creates two timers which
turn on the device every day at 16:00 and off again at 16:30.
"""

import asyncio
import sys

import aiokonstsmide


async def main():
    if len(sys.argv) < 2:
        print("Please pass a device address as argument")
        return

    address = sys.argv[1]
    async with aiokonstsmide.Device(address) as dev:
        await dev.timer(
            0,
            True,
            True,
            16,
            0,
            aiokonstsmide.Function.Steady,
            aiokonstsmide.Repeat.Everyday,
        )
        await dev.timer(
            1,
            True,
            False,
            16,
            30,
            aiokonstsmide.Function.Steady,
            aiokonstsmide.Repeat.Everyday,
        )


if __name__ == "__main__":
    asyncio.run(main())
