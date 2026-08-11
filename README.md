```markdown
# TrixOS

**Windows Optimization Tool for Windows 10/11**

TrixOS is a free, open‑source utility suite for tuning Windows systems. It includes three versions:

- **GUI** – full‑featured graphical interface with tweaks, BIOS guide, history, and tooltips.
- **CLI** – lightweight console version for quick tweaking.
- **Cloud** – online GUI that loads tweaks from the internet (with offline cache).

All versions use the same 15 safe and balanced tweaks (Privacy, Performance, Interface, Cleanup) and automatically create system restore points before applying changes.

---


## Features

- ✅ **15 system tweaks** – grouped by Privacy, Performance, Interface & Network, Cleanup.
- ✅ **Modern BIOS/UEFI guide** – up‑to‑date recommendations.
- ✅ **System monitoring dashboard** – real‑time CPU, RAM, disk, GPU usage (GUI versions).
- ✅ **Auto‑update** – GUI and CLI check GitHub for new versions.
- ✅ **Cloud version** – dynamic tweak database with offline cache.
- ✅ **Dark theme** – comfortable for night use.
- ✅ **Tooltips** – hover over any tweak to see a detailed description.
- ✅ **Tweak status detection** – already applied tweaks are checked on startup.
- ✅ **History tab** – logs all applied/reverted tweaks with timestamps.
- ✅ **Show Commands** – view the exact registry/PowerShell commands for each tweak.
- ✅ **Component selection** – installer lets you choose which versions to install.

---

## Download & Installation

### Option 1: Installer (recommended)

1. Go to the [Releases](https://github.com/trix7821/TrixOS/releases) page.
2. Download **`TrixOS_Installer.exe`**.
3. Run the installer and choose which components you want:
   - **TrixOS GUI** (local graphical interface)
   - **TrixOS CLI** (console version)
   - **TrixOS Cloud** (online GUI)
4. Follow the on‑screen instructions.
5. Launch TrixOS from the Start Menu or desktop shortcut.

### Option 2: Standalone executables

If you prefer not to use the installer, download any `.exe` file from the Releases page and run it as administrator.

---

## Usage

### GUI (Graphical Interface)

- **Dashboard** – view system load (CPU, RAM, disk, GPU) and apply all tweaks or quick cleanup.
- **Tweaks** – select individual tweaks, apply or revert them. Hover for tooltips, click 👁️ to see commands.
- **BIOS Guide** – modern recommendations for BIOS/UEFI setup.
- **History** – log of all applied/reverted tweaks with timestamps and status.
- **About** – author info and support links (DonationAlerts, Telegram, YouTube, Twitch).

### CLI (Console)

Run `TrixOS_CLI.exe` as administrator.

- Enter numbers (e.g., `1,2,6`) to select/deselect tweaks.
- `A` – apply selected.
- `R` – revert selected.
- `C` – create a restore point manually.
- `U` – check for updates.
- `B` – show BIOS guide.
- `O` – about / support.
- `Q` – quit.

### Cloud (Online GUI)

Identical to the GUI version, but tweaks are loaded from GitHub (with local cache as fallback). There is no **Check Updates** button – tweaks are always up‑to‑date.

---

## Building from Source

If you want to compile the executables yourself:

1. Install Python 3.8+ and dependencies:
   ```bash
   pip install customtkinter psutil pyinstaller
   ```
2. Run `build.bat` (Windows) to compile all three versions at once.
   - The script will automatically find PyInstaller and use `TrixOS.ico` if available.
3. Use Inno Setup with `TrixOS.iss` to build the installer.
   - The installer supports component selection (GUI, CLI, Cloud).

---

## Support the Project

If you find TrixOS useful, consider supporting its development:

- 💳 [DonationAlerts](https://www.donationalerts.com/r/21trix)
- 📱 [Telegram](https://t.me/thetrix21)
- 📺 [YouTube](https://www.youtube.com/@trixos7821)
- 📧 Email: trixos7821@gmail.com

---

## License

MIT License – see the [LICENSE](LICENSE) file for details.

---

**Enjoy a cleaner, faster Windows!** 🚀
```
