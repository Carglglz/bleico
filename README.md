# Bleico

<p align="center">
  <img src="https://github.com/Carglglz/bleico/blob/master/docs/bleico_logo.png?raw=true" width="360"/>
</p>

### Bluetooth Low Energy System Tray Utility

Bleico is a system tray application/tool to scan, connect, explore and debug
Bluetooth low energy devices which are compliant with [Bluetooth SIG GATT Characteristics](https://www.bluetooth.com/specifications/gatt/characteristics/).

* Lincense: GPL-3.0
* Documentation: https://bleico.readthedocs.io.


It is based on [bleak](https://bleak.readthedocs.io/en/latest/), [bleak-sigspec](https://bleak-sigspec.readthedocs.io/en/latest/) and [PyQt5](https://pypi.org/project/PyQt5/)

### Features
* Bluetooth Low Energy Scanner
* __System Tray Menu__ with:
  * Icon according to Appearance characteristic (if present)
  * Device Name
  * Device UUID
  * Services and Characteristics menu tree
  * Characteristic Metadata view
  * Device information (if present)
  * Readable and writeable Characteristics organised in sections by services
  * Read periodically from Characteristics
  * Write to Characteristics (from menu or dialog box)
  * Enable desktop notifications on notifiable Characteristics
  * Configurable tool tip
  * Last update, Connection status and RSSI
  * Desktop Notification on Connection status changes (can be disabled).
  * Automatic Reconnection on disconnect, in 30 seconds cycles until reconnected.



### Installation

#### Command Line Tool

Install ``bleico`` by running:

```bash
$ pip install bleico
```

Or get latest development version:  

```bash
$ pip install https://github.com/Carglglz/bleico/tree/develop.zip
```

#### Standalone Application

Download from [Releases](https://github.com/Carglglz/bleico/releases)

