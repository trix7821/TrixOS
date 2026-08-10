# TrixOS

**Ultimate Windows 10/11 Optimization Tool**

TrixOS is a complete suite of utilities for tuning a clean Windows installation. It provides three versions – **Standalone GUI**, **Cloud GUI** (loads tweaks from the internet), and **CLI** – all powered by the same 15 safe and balanced tweaks for privacy, performance, interface, and cleanup.

## Features

- ✅ **15 system tweaks** – grouped by Privacy, Performance, Interface & Network, and Cleanup.
- ✅ **Modern BIOS/UEFI guide** – up‑to‑date recommendations for today’s hardware.
- ✅ **System monitoring dashboard** – real‑time CPU, RAM, disk, and GPU usage (GUI versions).
- ✅ **Auto‑update** – Standalone and CLI check GitHub for new versions.
- ✅ **Cloud version** – tweak database loaded from the internet, with offline cache as fallback.
- ✅ **Dark theme** – easy on the eyes.

## Screenshots

### Standalone GUI – Dashboard

<img width="2559" height="1526" alt="dashboard" src="https://github.com/user-attachments/assets/a692130a-29ba-49fb-8952-954c60bd280e" />

### Standalone GUI – Tweaks

<img width="2559" height="1529" alt="tweaks" src="https://github.com/user-attachments/assets/b4229cdd-1a96-401f-b59d-8c3398e0e3fc" />

### Standalone GUI – BIOS Guide

<img width="2559" height="1518" alt="bios" src="https://github.com/user-attachments/assets/25a66be8-b466-44f2-8d8d-fd4733aaf81d" />

### CLI – Main Menu

<img width="2557" height="1524" alt="cli" src="https://github.com/user-attachments/assets/50513a2f-632f-4915-aeca-52b4687c7010" />

## Download

The easiest way to get TrixOS is to download the installer from the [Releases](https://github.com/trix7821/TrixOS/releases) page.

- **TrixOS_Installer.exe** – installs all three versions with shortcuts.
- **Standalone .exe files** – if you prefer to run them portably.

## Installation

1. Go to the [Releases](https://github.com/trix7821/TrixOS/releases) page.
2. Download `TrixOS_Installer.exe`.
3. Run it and select the components you want:
   - **TrixOS Standalone** – local GUI (recommended for most users)
   - **TrixOS Cloud** – online GUI (tweaks from the web)
   - **TrixOS CLI** – console version for advanced users
4. Follow the on‑screen instructions.

Alternatively, you can download any `.exe` file directly and run it without installation.

## Usage

### Standalone (Local GUI)

- **Dashboard** – view system stats, apply all tweaks, or run quick cleanup.
- **Tweaks** – pick individual tweaks, apply or revert them.
- **BIOS Guide** – read modern recommendations for BIOS/UEFI setup.

💡 **Always create a restore point** before applying tweaks – use the dedicated button in the app.

### Cloud (Online GUI)

Identical to Standalone, but:
- The tweak list is downloaded from GitHub every time you start the app.
- If the internet is unavailable, it uses a cached copy from `%APPDATA%\TrixOS\`.
- There is no **Check Updates** button – tweaks are always up‑to‑date.

### CLI (Console)

Run `TrixOS_CLI.exe` as administrator.

- **Select tweaks** – enter numbers separated by commas, e.g. `1,2,6`.
- **A** – apply selected tweaks.
- **R** – revert selected tweaks.
- **C** – create a restore point manually.
- **U** – check for new versions.
- **B** – show the BIOS guide.
- **ALL** – select all tweaks.
- **Q** – quit.

## Building from Source

If you prefer to compile the executables yourself:

1. Install Python 3.8+ and the required packages:
   ```bash
   pip install customtkinter psutil pyinstaller
2. Compile each script with PyInstaller:

bash
pyinstaller --onefile --console --icon=TrixOS.ico TrixOS_CLI.py
pyinstaller --onefile --noconsole --icon=TrixOS.ico --hidden-import=customtkinter --hidden-import=psutil TrixOS_Standalone.py
pyinstaller --onefile --noconsole --icon=TrixOS.ico --hidden-import=customtkinter --hidden-import=psutil TrixOS_Cloud.py

3. The .exe files will be in the dist folder.
4. To build the installer, use Inno Setup with the provided TrixOS.iss.

### License
This project is licensed under the MIT License – see the LICENSE file for details.

### Contributing
Issues and pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

### Acknowledgments
Built with customtkinter

System information provided by psutil

Package management via winget

### Enjoy a cleaner, faster Windows! 🚀
