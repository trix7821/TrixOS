# -*- coding: utf-8 -*-
# TrixOS_CLI.py

import os
import sys
import subprocess
import ctypes
import re
import ssl
import urllib.request
import urllib.error
import shutil
import tempfile
import time
from pathlib import Path

VERSION = "1.0"
APP_NAME = "TrixOS"
GITHUB_REPO = "https://raw.githubusercontent.com/trix7821/TrixOS/main/"

TWEAKS = [
    # Privacy
    {
        "id": "Telemetry",
        "category": "Privacy",
        "desc": "Disable telemetry (AllowTelemetry=0)",
        "cmd": ['reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f'],
        "revert": ['reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /f 2>nul']
    },
    {
        "id": "TelemetryServices",
        "category": "Privacy",
        "desc": "Disable tracking services (DiagTrack, dmwappushservice)",
        "cmd": [
            'sc stop DiagTrack',
            'sc config DiagTrack start= disabled',
            'sc stop dmwappushservice',
            'sc config dmwappushservice start= disabled'
        ],
        "revert": [
            'sc config DiagTrack start= demand',
            'sc start DiagTrack',
            'sc config dmwappushservice start= demand',
            'sc start dmwappushservice'
        ]
    },
    {
        "id": "Cortana",
        "category": "Privacy",
        "desc": "Disable Cortana and web search in Start menu",
        "cmd": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Search" /v DisableWebSearch /t REG_DWORD /d 1 /f'],
        "revert": ['reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Search" /v DisableWebSearch /f 2>nul']
    },
    {
        "id": "Ads",
        "category": "Privacy",
        "desc": "Disable ads and suggestions in File Explorer",
        "cmd": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowSyncProviderNotifications /t REG_DWORD /d 0 /f'],
        "revert": ['reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowSyncProviderNotifications /f 2>nul']
    },
    {
        "id": "UpdateTelemetry",
        "category": "Privacy",
        "desc": "Disable update feedback notifications",
        "cmd": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\UserProfileEngagement" /v DoNotShowFeedbackNotifications /t REG_DWORD /d 1 /f'],
        "revert": ['reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\UserProfileEngagement" /v DoNotShowFeedbackNotifications /f 2>nul']
    },
    # Performance
    {
        "id": "PowerPlan",
        "category": "Performance",
        "desc": "Activate 'High Performance' power plan",
        "cmd": ['powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'],
        "revert": ['powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e']
    },
    {
        "id": "Animations",
        "category": "Performance",
        "desc": "Optimize visual effects (disable window animations)",
        "cmd": ['reg add "HKCU\\Control Panel\\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012038010000000 /f'],
        "revert": ['reg add "HKCU\\Control Panel\\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9E12038010000000 /f']
    },
    {
        "id": "BackgroundApps",
        "category": "Performance",
        "desc": "Prevent apps from running in background",
        "cmd": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f'],
        "revert": ['reg delete "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /f 2>nul']
    },
    {
        "id": "DisableTransparency",
        "category": "Performance",
        "desc": "Disable transparency effects (reduces GPU load)",
        "cmd": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 0 /f'],
        "revert": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v EnableTransparency /t REG_DWORD /d 1 /f']
    },
    # Interface & Network
    {
        "id": "ContextMenu",
        "category": "Interface & Network",
        "desc": "Classic context menu (Windows 11 only)",
        "cmd": [
            'reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /ve /f',
            'taskkill /f /im explorer.exe',
            'start explorer.exe'
        ],
        "revert": [
            'reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f',
            'taskkill /f /im explorer.exe',
            'start explorer.exe'
        ]
    },
    {
        "id": "Notifications",
        "category": "Interface & Network",
        "desc": "Disable intrusive system notifications",
        "cmd": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 0 /f'],
        "revert": ['reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\PushNotifications" /v ToastEnabled /t REG_DWORD /d 1 /f']
    },
    {
        "id": "SetDNSCloudflare",
        "category": "Interface & Network",
        "desc": "Set Cloudflare DNS (1.1.1.1, 1.0.0.1)",
        "cmd": [
            'powershell -Command "$adapters = Get-NetAdapter -Physical | Where-Object {$_.Status -eq \'Up\'}; foreach ($adapter in $adapters) { Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses (\'1.1.1.1\',\'1.0.0.1\') }"'
        ],
        "revert": [
            'powershell -Command "$adapters = Get-NetAdapter -Physical | Where-Object {$_.Status -eq \'Up\'}; foreach ($adapter in $adapters) { Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ResetServerAddresses }"'
        ]
    },
    {
        "id": "DisableFastStartup",
        "category": "Interface & Network",
        "desc": "Disable Fast Startup",
        "cmd": ['reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f'],
        "revert": ['reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 1 /f']
    },
    # Cleanup
    {
        "id": "CleanTemp",
        "category": "Cleanup",
        "desc": "Clean user and system Temp folders",
        "cmd": [
            'del /f /s /q "%TEMP%\\*" 2>nul',
            'del /f /s /q "%SystemRoot%\\Temp\\*" 2>nul',
            'rd /s /q "%TEMP%" 2>nul',
            'rd /s /q "%SystemRoot%\\Temp" 2>nul',
            'mkdir "%TEMP%" 2>nul',
            'mkdir "%SystemRoot%\\Temp" 2>nul'
        ],
        "revert": []
    },
    {
        "id": "CleanPrefetch",
        "category": "Cleanup",
        "desc": "Clean Prefetch folder (old startup logs)",
        "cmd": ['del /f /s /q "%SystemRoot%\\Prefetch\\*" 2>nul'],
        "revert": []
    }
]

BIOS_TEXT = """
===========================================================
   MODERN BIOS/UEFI SETUP RECOMMENDATIONS
===========================================================

1. ENTERING BIOS/UEFI:
   • Press Delete, F2, F10 or Esc during boot.
   • Refer to your motherboard manual if these keys don't work.

2. RESET TO OPTIMIZED DEFAULTS:
   • First, load optimized defaults (Load Optimized Defaults) to start from a clean slate.

3. RAM (Memory):
   • Enable XMP / DOCP / EXPO profile to run RAM at its rated speed.
   • If unstable, try a lower profile or manually adjust voltage (carefully).

4. GPU (Graphics Card):
   • Enable Above 4G Decoding and Resizable BAR (Re-Size BAR Support) for 5-15% performance boost in games.
   • Set Primary Graphics Adapter to PCIe if you have a discrete GPU.

5. SYSTEM SECURITY (for Windows 11):
   • Enable Secure Boot and TPM 2.0 (fTPM/PTT) – required for Windows 11 installation.

6. STORAGE:
   • Set SATA mode to AHCI (not IDE) – improves SSD performance (usually default).

7. CPU & POWER MANAGEMENT (modern approach):
   • Leave C-States (including C6/C7) on Auto – they save power and do not affect gaming performance.
   • Leave Intel SpeedStep / AMD Cool'n'Quiet on Auto – modern CPUs manage frequencies efficiently.
   • Do not lock all cores to a fixed frequency (Sync All Cores) – it increases heat and power draw without benefit.
   • Keep virtualization (Intel VT-x / AMD-V, VT-d/AMD-Vi) enabled – WSL2, Docker, and anti-cheat systems rely on it.
   • Do not disable Spread Spectrum – it has no impact on modern system stability.

8. BOOT OPTIONS:
   • Enable Fast Boot only if you use an SSD – it may reduce BIOS access time.

9. FIRMWARE UPDATES:
   • Check for BIOS updates on your motherboard vendor's website – they often improve stability and performance.

⚠️ IMPORTANT:
   • Make changes gradually. If system fails to boot, clear CMOS (remove battery for 2 minutes or use Clear CMOS jumper).
   • Always note original settings before changing.
   • Modern systems are highly optimized; leaving most settings on Auto is usually the best choice.
"""

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    except Exception:
        input("Failed to get administrator privileges. Press Enter to exit.")
        sys.exit(1)
    sys.exit()

def create_restore_point():
    try:
        cmd = 'powershell -Command "Checkpoint-Computer -Description \'TrixOS\' -RestorePointType MODIFY_SETTINGS"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return result.returncode == 0
    except:
        return False

def run_command(cmd, capture=False, log_callback=None):
    if log_callback:
        log_callback(f"Executing: {cmd}\n")
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=capture, text=True, encoding='utf-8', errors='replace')
        if log_callback:
            if proc.stdout:
                log_callback(proc.stdout)
            if proc.stderr:
                log_callback(f"STDERR: {proc.stderr}")
        if proc.returncode != 0:
            if log_callback:
                log_callback(f"Command returned error code: {proc.returncode}\n")
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as e:
        if log_callback:
            log_callback(f"Exception: {str(e)}\n")
        return -1, "", str(e)

def apply_tweak(tweak, revert=False, log_callback=None):
    commands = tweak["revert"] if revert else tweak["cmd"]
    if not commands:
        msg = "No commands to execute (maybe cleanup)." if not revert else "Revert not possible."
        if log_callback:
            log_callback(msg + "\n")
        return False
    success = True
    for cmd in commands:
        code, _, _ = run_command(cmd, capture=True, log_callback=log_callback)
        if code != 0:
            success = False
            if log_callback:
                log_callback(f"Command failed: {cmd}\n")
    return success

def get_tweak_by_id(tweak_id):
    for t in TWEAKS:
        if t["id"] == tweak_id:
            return t
    return None

def get_latest_version():
    for attempt in range(3):
        try:
            context = ssl._create_unverified_context()
            url = GITHUB_REPO + "version.txt"
            req = urllib.request.Request(
                url,
                headers={
                    'Cache-Control': 'no-cache',
                    'User-Agent': 'TrixOS-Updater/1.0'
                }
            )
            with urllib.request.urlopen(req, timeout=20, context=context) as resp:
                return resp.read().decode('utf-8').strip()
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2)
                continue
            else:
                print(f"[Update] Connection error after 3 attempts: {e.reason}")
                return None
        except Exception as e:
            print(f"[Update] Unexpected error: {e}")
            return None
    return None

def download_new_exe():
    current_exe = sys.argv[0]
    if not current_exe.lower().endswith('.exe'):
        print("Update only works for compiled .exe.")
        return False
    for attempt in range(3):
        try:
            context = ssl._create_unverified_context()
            url = GITHUB_REPO + "TrixOS_CLI.exe"
            req = urllib.request.Request(url, headers={'User-Agent': 'TrixOS-Updater/1.0'})
            temp_file = current_exe + ".new"
            with urllib.request.urlopen(req, timeout=20, context=context) as response:
                with open(temp_file, 'wb') as f:
                    shutil.copyfileobj(response, f)
            os.remove(current_exe)
            os.rename(temp_file, current_exe)
            print("Update installed. Please restart the program.")
            return True
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            else:
                print(f"Download error after 3 attempts: {e}")
                return False
    return False

def print_biostext():
    print(BIOS_TEXT)

def main():
    if not is_admin():
        print("Requesting administrator privileges...")
        run_as_admin()
        return

    print("TrixOS CLI v" + VERSION)
    print("=" * 50)

    selected = set()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n=== TrixOS CLI ===")
        print(f"Version: {VERSION}\n")
        print("Select tweaks (enter numbers separated by commas, e.g. 1,2,6)")
        print("  [ALL] - select all")
        print("  [A] - apply selected")
        print("  [R] - revert selected")
        print("  [C] - create system restore point (manual)")
        print("  [U] - check for updates")
        print("  [B] - show BIOS guide")
        print("  [Q] - quit\n")

        for idx, tweak in enumerate(TWEAKS, 1):
            status = "[X]" if tweak["id"] in selected else "[ ]"
            print(f"{idx:2}. {status} {tweak['category']} -> {tweak['desc']}")

        print("\nEnter command or numbers: ", end="")
        user_input = input().strip().lower()

        if user_input == 'q':
            break
        elif user_input == 'a':
            if not selected:
                print("No tweaks selected.")
                input("Press Enter...")
                continue
            print("Applying tweaks... (no restore point created automatically)")
            for tid in list(selected):
                tweak = get_tweak_by_id(tid)
                if tweak:
                    print(f"Applying: {tweak['desc']}")
                    apply_tweak(tweak, revert=False, log_callback=lambda msg: print(msg, end=""))
            print("Done.")
            input("Press Enter...")
        elif user_input == 'r':
            if not selected:
                print("No tweaks selected.")
                input("Press Enter...")
                continue
            print("Reverting tweaks... (no restore point created automatically)")
            for tid in list(selected):
                tweak = get_tweak_by_id(tid)
                if tweak:
                    print(f"Reverting: {tweak['desc']}")
                    apply_tweak(tweak, revert=True, log_callback=lambda msg: print(msg, end=""))
            print("Done.")
            input("Press Enter...")
        elif user_input == 'c':
            print("Creating system restore point...")
            if create_restore_point():
                print("Restore point created successfully.")
            else:
                print("Failed to create restore point.")
            input("Press Enter...")
        elif user_input == 'u':
            print("Checking for updates...")
            latest = get_latest_version()
            if latest is None:
                print("Could not reach GitHub server. Please check your internet connection.")
                print("If you are behind a proxy or firewall, make sure raw.githubusercontent.com is accessible.")
            elif latest > VERSION:
                print(f"New version available: {latest}. Downloading...")
                if download_new_exe():
                    print("Update successful. Please restart the program.")
                    input("Press Enter to exit.")
                    sys.exit(0)
                else:
                    print("Update error.")
            else:
                print("You have the latest version.")
            input("Press Enter...")
        elif user_input == 'b':
            print_biostext()
            input("Press Enter...")
        elif user_input == 'all':
            selected = {t["id"] for t in TWEAKS}
        else:
            try:
                parts = re.split(r'[,\s]+', user_input)
                new_selected = set()
                for p in parts:
                    if p.isdigit():
                        idx = int(p)
                        if 1 <= idx <= len(TWEAKS):
                            new_selected.add(TWEAKS[idx-1]["id"])
                if new_selected:
                    for tid in new_selected:
                        if tid in selected:
                            selected.remove(tid)
                        else:
                            selected.add(tid)
                else:
                    print("Invalid input.")
                    input("Press Enter...")
            except:
                print("Invalid input.")
                input("Press Enter...")

if __name__ == "__main__":
    main()