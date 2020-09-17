
Getting Started
===============

Command Line Tool
-----------------

Do ``$ bleico -h`` to see mode options and optional args.

.. code-block:: console

    $ bleico -h
    usage: bleico [Mode] [options]

    Bluetooth Low Energy System Tray Utility

    positional arguments:
      Mode          Mode:
                    - config
                    - run

    optional arguments:
      -h, --help    show this help message and exit
      -v            show program's version number and exit
      -t T          device target uuid
      -s            show scanner with available devices
      -r R          read timeout in seconds, default: 1
      -dflev DFLEV  debug file mode level, options [debug, info, warning, error, critical]
      -dslev DSLEV  debug sys out mode level, options [debug, info, warning, error, critical]




Config mode
^^^^^^^^^^^
To configure a default device to connect to, use ``-t`` to indicate the device's
uuid and ``-r`` to indicate the read timeout in seconds (defaults to 1 second)
The device configuration will be saved in ``bleico_.config``  under ``~/.bleico``
directory.

Run mode
^^^^^^^^

- **Case 1: Configured device**
      The device is configured already, no any option needed, just do
      ``$ bleico run``, to start bleico, a splash will appear while trying to
      connect to the device, and once it is connected the bleico icon will appear
      in the system tray / task bar

      .. code-block:: console

          $ bleico run
          ************************************************************

          $$$$$$$\  $$\       $$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\
          $$  __$$\ $$ |      $$  _____|\_$$  _|$$  __$$\ $$  __$$\
          $$ |  $$ |$$ |      $$ |        $$ |  $$ /  \__|$$ /  $$ |
          $$$$$$$\ |$$ |      $$$$$\      $$ |  $$ |      $$ |  $$ |
          $$  __$$\ $$ |      $$  __|     $$ |  $$ |      $$ |  $$ |
          $$ |  $$ |$$ |      $$ |        $$ |  $$ |  $$\ $$ |  $$ |
          $$$$$$$  |$$$$$$$$\ $$$$$$$$\ $$$$$$\ \$$$$$$  | $$$$$$  |
          \_______/ \________|\________|\______| \______/  \______/

          ************************************************************
          2020-09-10 22:27:20,153 [bleico] [MainThread] [INFO] Running bleico 0.0.1
          2020-09-10 22:27:23,544 [bleico] [MainThread] [INFO] Connected to: 9998175F-9A91-4CA2-B5EA-482AFC3453B9
          2020-09-10 22:27:24,540 [bleico] [MainThread] [INFO] Device esp32-batt-temp found
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO] Services:
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (S) Device Information
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Appearance
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Manufacturer Name String
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Model Number String
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Serial Number String
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Firmware Revision String
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Hardware Revision String
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (C)  - Software Revision String
          2020-09-10 22:27:24,541 [bleico] [MainThread] [INFO]  (S) Battery Service
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]  (C)  - Battery Level
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]  (C)  - Battery Power State
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]  (S) Environmental Sensing
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]  (C)  - Temperature
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]  (C)  - Temperature Range
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO] Device: esp32-batt-temp, UUID: 9998175F-9A91-4CA2-B5EA-482AFC3453B9
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO] Device Information:
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]     - Appearance: Generic Thermometer
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]     - Manufacturer Name : Espressif Incorporated
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]     - Model Number : ESP32 module with ESP32
          2020-09-10 22:27:24,542 [bleico] [MainThread] [INFO]     - Serial Number : 30:AE:A4:23:35:64
          2020-09-10 22:27:24,543 [bleico] [MainThread] [INFO]     - Firmware Revision : micropython-1.13.0
          2020-09-10 22:27:24,543 [bleico] [MainThread] [INFO]     - Hardware Revision : esp32
          2020-09-10 22:27:24,543 [bleico] [MainThread] [INFO]     - Software Revision : 3.4.0
          2020-09-10 22:27:24,552 [bleico] [MainThread] [INFO] Multithreading with maximum 4 threads
          2020-09-10 22:27:24,687 [bleico] [MainThread] [INFO] [Battery Service] Battery Level: 96 %
          2020-09-10 22:27:24,687 [bleico] [MainThread] [INFO] [Environmental Sensing] Temperature: 25.03 °C
          2020-09-10 22:27:24,688 [bleico] [MainThread] [INFO] [Environmental Sensing] Temperature Range Minimum Temperature: 15.0 °C
          2020-09-10 22:27:24,688 [bleico] [MainThread] [INFO] [Environmental Sensing] Temperature Range Maximum Temperature: 28.0 °C

- **Case 2: No configured device, known uuid**
      To connect to a different device with a known uuid, do ``$ bleico run -t [uuid]``
      e.g.

      .. code-block:: console

            $ bleico run -t F6291A68-6086-4538-A2C7-A7ABE485305C
            ************************************************************

            $$$$$$$\  $$\       $$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\
            $$  __$$\ $$ |      $$  _____|\_$$  _|$$  __$$\ $$  __$$\
            $$ |  $$ |$$ |      $$ |        $$ |  $$ /  \__|$$ /  $$ |
            $$$$$$$\ |$$ |      $$$$$\      $$ |  $$ |      $$ |  $$ |
            $$  __$$\ $$ |      $$  __|     $$ |  $$ |      $$ |  $$ |
            $$ |  $$ |$$ |      $$ |        $$ |  $$ |  $$\ $$ |  $$ |
            $$$$$$$  |$$$$$$$$\ $$$$$$$$\ $$$$$$\ \$$$$$$  | $$$$$$  |
            \_______/ \________|\________|\______| \______/  \______/

            ************************************************************
            2020-09-13 21:33:48,783 [bleico] [MainThread] [INFO] Running bleico 0.0.1
            2020-09-13 21:33:52,640 [bleico] [MainThread] [ERROR] Device with address F6291A68-6086-4538-A2C7-A7ABE485305C was not found
            2020-09-13 21:33:52,641 [bleico] [MainThread] [INFO] Trying again...
            2020-09-13 21:34:00,612 [bleico] [MainThread] [INFO] Connected to: F6291A68-6086-4538-A2C7-A7ABE485305C
            2020-09-13 21:34:02,310 [bleico] [MainThread] [INFO] Device LG6 found
            2020-09-13 21:34:02,310 [bleico] [MainThread] [INFO] Services:
            2020-09-13 21:34:02,310 [bleico] [MainThread] [INFO]  (S) Battery Service
            2020-09-13 21:34:02,310 [bleico] [MainThread] [INFO]  (C)  - Battery Level
            2020-09-13 21:34:02,310 [bleico] [MainThread] [INFO]  (C)  - Battery Power State
            2020-09-13 21:34:02,310 [bleico] [MainThread] [INFO]  (S) Device Information
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (C)  - Manufacturer Name String
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (C)  - Appearance
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (C)  - Model Number String
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (C)  - Firmware Revision String
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (S) Environmental Sensing
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (C)  - Temperature
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (C)  - Sensor Location
            2020-09-13 21:34:02,311 [bleico] [MainThread] [INFO]  (S) Tx Power
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO]  (C)  - Tx Power Level
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO] Device: LG6, UUID: F6291A68-6086-4538-A2C7-A7ABE485305C
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO] Device Information:
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO]     - Manufacturer Name : LG Electronics
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO]     - Appearance: Fingertip
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO]     - Model Number : LG-H870
            2020-09-13 21:34:02,312 [bleico] [MainThread] [INFO]     - Firmware Revision : Android 9
            2020-09-13 21:34:02,324 [bleico] [MainThread] [INFO] Multithreading with maximum 4 threads
            2020-09-13 21:34:02,848 [bleico] [MainThread] [INFO] [Battery Service] Battery Level: 96 %
            2020-09-13 21:34:02,848 [bleico] [MainThread] [INFO] [Environmental Sensing] Temperature: 25.0 °C
            2020-09-13 21:34:02,849 [bleico] [MainThread] [INFO] [Environmental Sensing] Sensor Location: Other
            2020-09-13 21:34:02,849 [bleico] [MainThread] [INFO] [Tx Power] Tx Power Level: 0 dBm


- **Case 3: No configured device and unknown uuid**
      To connect to a device with unknown uuid do ``$ bleico run -s``
      This will perform a scan and show available devices in a dialog box, where
      the device can be selected and save it as a default. e.g.

      .. image:: img/bleico_scan.png
          :target: https://github.com/Carglglz/bleico
          :alt: Bleico App
          :align: center
          :width: 90%

      .. image:: img/bleico_scan_selected.png
          :target: https://github.com/Carglglz/bleico
          :alt: Bleico App
          :align: center
          :width: 90%

      .. code-block:: console

          $ bleico run -s
          ************************************************************

          $$$$$$$\  $$\       $$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\
          $$  __$$\ $$ |      $$  _____|\_$$  _|$$  __$$\ $$  __$$\
          $$ |  $$ |$$ |      $$ |        $$ |  $$ /  \__|$$ /  $$ |
          $$$$$$$\ |$$ |      $$$$$\      $$ |  $$ |      $$ |  $$ |
          $$  __$$\ $$ |      $$  __|     $$ |  $$ |      $$ |  $$ |
          $$ |  $$ |$$ |      $$ |        $$ |  $$ |  $$\ $$ |  $$ |
          $$$$$$$  |$$$$$$$$\ $$$$$$$$\ $$$$$$\ \$$$$$$  | $$$$$$  |
          \_______/ \________|\________|\______| \______/  \______/

          ************************************************************
          2020-09-13 21:40:58,393 [bleico] [MainThread] [INFO] Running bleico 0.0.1
          2020-09-13 21:40:58,586 [bleico] [MainThread] [INFO] SCANNING AVAILABLE DEVICES...
          2020-09-13 21:40:58,987 [bleico] [MainThread] [INFO] Scanning...
          2020-09-13 21:41:03,992 [bleico] [MainThread] [INFO] BLE device/s found: 2
          2020-09-13 21:41:03,992 [bleico] [MainThread] [INFO] NAME: LG6, UUID: F6291A68-6086-4538-A2C7-A7ABE485305C, RSSI: -46.0 dBm
          2020-09-13 21:41:03,992 [bleico] [MainThread] [INFO] NAME: Unknown, UUID: 214AD23B-6C5E-4F3D-8132-20E6A22B8EFF, RSSI: -85.0 dBm
          2020-09-13 21:41:06,610 [bleico] [MainThread] [INFO] Device selected: F6291A68-6086-4538-A2C7-A7ABE485305C
          2020-09-13 21:41:25,860 [bleico] [MainThread] [INFO] Connecting to: F6291A68-6086-4538-A2C7-A7ABE485305C
          2020-09-13 21:41:29,185 [bleico] [MainThread] [ERROR] Device with address F6291A68-6086-4538-A2C7-A7ABE485305C was not found
          2020-09-13 21:41:29,186 [bleico] [MainThread] [INFO] Trying again...
          2020-09-13 21:41:33,192 [bleico] [MainThread] [ERROR] Device with address F6291A68-6086-4538-A2C7-A7ABE485305C was not found
          2020-09-13 21:41:33,192 [bleico] [MainThread] [INFO] Trying again...
          2020-09-13 21:41:37,196 [bleico] [MainThread] [ERROR] Device with address F6291A68-6086-4538-A2C7-A7ABE485305C was not found
          2020-09-13 21:41:37,196 [bleico] [MainThread] [INFO] Trying again...
          2020-09-13 21:41:45,534 [bleico] [MainThread] [INFO] Connected to: F6291A68-6086-4538-A2C7-A7ABE485305C
          2020-09-13 21:41:47,280 [bleico] [MainThread] [INFO] Device LG6 found
          2020-09-13 21:41:47,280 [bleico] [MainThread] [INFO] Services:
          2020-09-13 21:41:47,280 [bleico] [MainThread] [INFO]  (S) Battery Service
          2020-09-13 21:41:47,280 [bleico] [MainThread] [INFO]  (C)  - Battery Level
          2020-09-13 21:41:47,280 [bleico] [MainThread] [INFO]  (C)  - Battery Power State
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (S) Device Information
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (C)  - Manufacturer Name String
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (C)  - Appearance
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (C)  - Model Number String
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (C)  - Firmware Revision String
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (S) Environmental Sensing
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (C)  - Temperature
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (C)  - Sensor Location
          2020-09-13 21:41:47,281 [bleico] [MainThread] [INFO]  (S) Tx Power
          2020-09-13 21:41:47,282 [bleico] [MainThread] [INFO]  (C)  - Tx Power Level
          2020-09-13 21:41:47,282 [bleico] [MainThread] [INFO] Device: LG6, UUID: F6291A68-6086-4538-A2C7-A7ABE485305C
          2020-09-13 21:41:47,282 [bleico] [MainThread] [INFO] Device Information:
          2020-09-13 21:41:47,282 [bleico] [MainThread] [INFO]     - Manufacturer Name : LG Electronics
          2020-09-13 21:41:47,282 [bleico] [MainThread] [INFO]     - Appearance: Fingertip
          2020-09-13 21:41:47,282 [bleico] [MainThread] [INFO]     - Model Number : LG-H870
          2020-09-13 21:41:47,283 [bleico] [MainThread] [INFO]     - Firmware Revision : Android 9
          2020-09-13 21:41:47,289 [bleico] [MainThread] [INFO] Multithreading with maximum 4 threads
          2020-09-13 21:41:47,915 [bleico] [MainThread] [INFO] [Battery Service] Battery Level: 96 %
          2020-09-13 21:41:47,915 [bleico] [MainThread] [INFO] [Environmental Sensing] Temperature: 25.0 °C
          2020-09-13 21:41:47,916 [bleico] [MainThread] [INFO] [Environmental Sensing] Sensor Location: Other
          2020-09-13 21:41:47,916 [bleico] [MainThread] [INFO] [Tx Power] Tx Power Level: 0 dBm


Standalone Application
----------------------

If there is no configured device, the scan dialog will appear.
If there is a configured device, it will try to connect to it, and if this is not
possible, the scan dialog will appear again.
