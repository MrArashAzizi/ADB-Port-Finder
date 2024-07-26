# ADB Port Finder

This script automates the process of finding available ADB (Android Debug Bridge) ports and connecting to an ADB-enabled device. It helps you locate an open port, connect to the device, install APK files, and disconnect when done.

## Features

- Find open ADB ports within a specified range
- Connect to an ADB-enabled device
- Install APK files
- Disconnect from the device

## Prerequisites

- **Python 3.x**: Ensure you have Python 3.x installed.
- **ADB**: Android Debug Bridge (ADB) must be installed and available in your system PATH. Alternatively, make sure the ADB executable files (`adb.exe` on Windows or `adb` on Unix-like systems) are in the same directory as this script.
- **colorama**: Install the `colorama` library using `pip install colorama`.

## Usage

1. **Clone the repository** or download the script.
2. **Modify the configuration variables** at the top of the script if necessary. These include IP address, timeout duration, and port range.
3. **Run the script** using Python. For example: `python adb_port_finder.py`.
