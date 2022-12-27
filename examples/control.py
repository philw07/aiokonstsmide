import asyncio
import sys

import aiokonstsmide


async def main():
    if len(sys.argv) < 2:
        print("Please pass a device address as argument")
        return

    address = sys.argv[1]
    async with aiokonstsmide.Device(address) as dev:
        for func in aiokonstsmide.Function:
            if func != aiokonstsmide.Function.Keep:
                await asyncio.sleep(3)
                await dev.control(func, 80, 80)


if __name__ == "__main__":
    asyncio.run(main())
