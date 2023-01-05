# aiokonstsmide

An asynchronous library to communicate with Konstsmide Bluetooth string lights.

- [Documentation](https://philw07.github.io/aiokonstsmide/aiokonstsmide.html)

## Supported features

- Connect with a device and send the password as pairing mechanism
- Turn the device on/off
- Control the devices function, brightness and flash speed
- Create timers on the device to turn on/off the device or specific functions at specific times and weekdays

## Installation

```console
$ pip install aiokonstsmide
```

## Usage

```python
async with aiokonstsmide.Device("11:22:33:44:55:66") as dev:
    await dev.on()
```

Also check the [examples](https://github.com/philw07/aiokonstsmide/tree/master/examples) folder.
