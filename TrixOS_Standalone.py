# -*- coding: utf-8 -*-
# TrixOS_Standalone.py

import os
import sys
import ctypes
import threading
import subprocess
import re
import ssl
import urllib.request
import urllib.error
import shutil
import tempfile
import time
from pathlib import Path

import psutil
import customtkinter as ctk
from tkinter import scrolledtext

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
        env = os.environ.copy()
        env["WINGET_DISABLE_ADMIN_WARNING"] = "1"
        proc = subprocess.run(cmd, shell=True, capture_output=capture, text=True, encoding='utf-8', errors='replace', env=env)
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

def get_cpu_percent():
    return psutil.cpu_percent(interval=0.5)

def get_ram_percent():
    return psutil.virtual_memory().percent

def get_disk_percent():
    return psutil.disk_usage('C:').percent

def get_gpu_model():
    try:
        cmd = 'powershell -Command "Get-WmiObject -Class Win32_VideoController | Select-Object -ExpandProperty Name"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        lines = result.stdout.splitlines()
        for line in lines:
            line = line.strip()
            if line and not line.lower().startswith('name'):
                return line
        return "Unknown"
    except:
        return "Unknown"

def check_update_standalone(log_callback=None):
    def _update():
        for attempt in range(3):
            try:
                context = ssl._create_unverified_context()
                url_ver = GITHUB_REPO + "version.txt"
                req = urllib.request.Request(
                    url_ver,
                    headers={
                        'Cache-Control': 'no-cache',
                        'User-Agent': 'TrixOS-Updater/1.0'
                    }
                )
                with urllib.request.urlopen(req, timeout=20, context=context) as resp:
                    latest = resp.read().decode('utf-8').strip()
                if log_callback:
                    log_callback(f"Server version: {latest}, local version: {VERSION}\n")
                if latest > VERSION:
                    if log_callback:
                        log_callback(f"New version available: {latest}. Downloading...\n")
                    current_exe = sys.argv[0]
                    if not current_exe.lower().endswith('.exe'):
                        if log_callback:
                            log_callback("Update only works for compiled .exe.\n")
                        return
                    url_exe = GITHUB_REPO + "TrixOS_Standalone.exe"
                    req_exe = urllib.request.Request(url_exe, headers={'User-Agent': 'TrixOS-Updater/1.0'})
                    temp_file = current_exe + ".new"
                    with urllib.request.urlopen(req_exe, timeout=20, context=context) as response:
                        with open(temp_file, 'wb') as f:
                            shutil.copyfileobj(response, f)
                    bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
move /Y "{temp_file}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
                    bat_path = os.path.join(tempfile.gettempdir(), "update_trixos.bat")
                    with open(bat_path, 'w') as f:
                        f.write(bat_content)
                    subprocess.Popen([bat_path], creationflags=subprocess.CREATE_NO_WINDOW)
                    if log_callback:
                        log_callback("Update installed. Program will restart.\n")
                    sys.exit(0)
                else:
                    if log_callback:
                        log_callback("You have the latest version.\n")
                return
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                else:
                    if log_callback:
                        log_callback(f"Update check error after 3 attempts: {e}\n")
                        log_callback("Please check your internet connection and try again.\n")
                    return
    threading.Thread(target=_update, daemon=True).start()

class TrixOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TrixOS v" + VERSION)
        self.geometry("1100x700")
        self.minsize(1000, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Set window icon
        try:
            self.iconbitmap("TrixOS.ico")
        except:
            pass

        self.tweak_vars = {}

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)

        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(side="right", fill="both", expand=True)

        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_frame("dashboard"))
        self.btn_dashboard.pack(pady=10, padx=10, fill="x")
        self.btn_tweaks = ctk.CTkButton(self.sidebar, text="Tweaks", command=lambda: self.show_frame("tweaks"))
        self.btn_tweaks.pack(pady=10, padx=10, fill="x")
        self.btn_bios = ctk.CTkButton(self.sidebar, text="BIOS Guide", command=lambda: self.show_frame("bios"))
        self.btn_bios.pack(pady=10, padx=10, fill="x")
        self.btn_update = ctk.CTkButton(self.sidebar, text="Check Updates", command=self.check_updates)
        self.btn_update.pack(pady=10, padx=10, fill="x")

        self.frames = {}
        for name in ["dashboard", "tweaks", "bios"]:
            frame = ctk.CTkFrame(self.main_frame)
            frame.pack(fill="both", expand=True)
            self.frames[name] = frame

        # Log and progress
        self.log_frame = ctk.CTkFrame(self.main_frame, height=150)
        self.log_frame.pack(side="bottom", fill="x", padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap="word", height=6, bg="#1e1e1e", fg="white", font=("Consolas", 9))
        self.log_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.progress = ctk.CTkProgressBar(self.log_frame, width=200)
        self.progress.pack(side="right", padx=10, pady=5)
        self.progress.set(0)

        self.build_dashboard()
        self.build_tweaks()
        self.build_bios()

        self.show_frame("dashboard")

    def show_frame(self, name):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    def log(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.update_idletasks()

    def build_dashboard(self):
        frame = self.frames["dashboard"]
        card_frame = ctk.CTkFrame(frame)
        card_frame.pack(pady=20, padx=20, fill="x")
        self.lbl_cpu = ctk.CTkLabel(card_frame, text="CPU: 0%", font=("Arial", 16))
        self.lbl_cpu.pack(side="left", padx=20)
        self.lbl_ram = ctk.CTkLabel(card_frame, text="RAM: 0%", font=("Arial", 16))
        self.lbl_ram.pack(side="left", padx=20)
        self.lbl_disk = ctk.CTkLabel(card_frame, text="Drive C: 0%", font=("Arial", 16))
        self.lbl_disk.pack(side="left", padx=20)
        gpu = get_gpu_model()
        self.lbl_gpu = ctk.CTkLabel(card_frame, text=f"GPU: {gpu}", font=("Arial", 16))
        self.lbl_gpu.pack(side="left", padx=20)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Apply All Tweaks", command=self.apply_all_tweaks).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Quick Cleanup", command=self.fast_cleanup).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Create Restore Point", command=self.manual_restore_point).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Check Updates", command=self.check_updates).pack(side="left", padx=10)

        self.update_system_info()

    def update_system_info(self):
        try:
            self.lbl_cpu.configure(text=f"CPU: {get_cpu_percent():.1f}%")
            self.lbl_ram.configure(text=f"RAM: {get_ram_percent():.1f}%")
            self.lbl_disk.configure(text=f"Drive C: {get_disk_percent():.1f}%")
        except:
            pass
        self.after(3000, self.update_system_info)

    def manual_restore_point(self):
        self.log("Creating restore point...")
        if create_restore_point():
            self.log("Restore point created successfully.")
        else:
            self.log("Failed to create restore point.")

    def apply_all_tweaks(self):
        def _apply():
            self.progress.set(0)
            self.log("Applying all tweaks (no restore point created).")
            total = len(TWEAKS)
            for i, tweak in enumerate(TWEAKS):
                self.log(f"Applying: {tweak['desc']}")
                apply_tweak(tweak, revert=False, log_callback=self.log)
                self.progress.set((i+1)/total)
            self.log("All tweaks applied.")
        threading.Thread(target=_apply, daemon=True).start()

    def fast_cleanup(self):
        def _clean():
            self.progress.set(0)
            self.log("Cleaning Temp and Prefetch...")
            for tweak in TWEAKS:
                if tweak["id"] in ["CleanTemp", "CleanPrefetch"]:
                    apply_tweak(tweak, revert=False, log_callback=self.log)
            self.progress.set(1)
            self.log("Cleanup completed.")
        threading.Thread(target=_clean, daemon=True).start()

    def check_updates(self):
        self.log("Checking for updates...")
        check_update_standalone(self.log)

    def build_tweaks(self):
        frame = self.frames["tweaks"]
        categories = {}
        for t in TWEAKS:
            categories.setdefault(t["category"], []).append(t)

        scroll = ctk.CTkScrollableFrame(frame)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        for cat, tweaks in categories.items():
            cat_frame = ctk.CTkFrame(scroll)
            cat_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(cat_frame, text=cat, font=("Arial", 14, "bold")).pack(anchor="w")
            for tweak in tweaks:
                var = ctk.BooleanVar(value=False)
                self.tweak_vars[tweak["id"]] = var
                cb = ctk.CTkCheckBox(cat_frame, text=tweak["desc"], variable=var, onvalue=True, offvalue=False)
                cb.pack(anchor="w", padx=20)

        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Apply Selected", command=self.apply_selected_tweaks).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Revert Selected", command=self.revert_selected_tweaks).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Create Restore Point", command=self.manual_restore_point).pack(side="left", padx=10)

    def apply_selected_tweaks(self):
        selected = [tid for tid, var in self.tweak_vars.items() if var.get()]
        if not selected:
            self.log("No tweaks selected.")
            return
        def _apply():
            self.progress.set(0)
            self.log("Applying selected tweaks (no restore point created).")
            total = len(selected)
            for i, tid in enumerate(selected):
                tweak = get_tweak_by_id(tid)
                if tweak:
                    self.log(f"Applying: {tweak['desc']}")
                    apply_tweak(tweak, revert=False, log_callback=self.log)
                self.progress.set((i+1)/total)
            self.log("Application completed.")
        threading.Thread(target=_apply, daemon=True).start()

    def revert_selected_tweaks(self):
        selected = [tid for tid, var in self.tweak_vars.items() if var.get()]
        if not selected:
            self.log("No tweaks selected.")
            return
        def _revert():
            self.progress.set(0)
            self.log("Reverting selected tweaks (no restore point created).")
            total = len(selected)
            for i, tid in enumerate(selected):
                tweak = get_tweak_by_id(tid)
                if tweak:
                    self.log(f"Reverting: {tweak['desc']}")
                    apply_tweak(tweak, revert=True, log_callback=self.log)
                self.progress.set((i+1)/total)
            self.log("Revert completed.")
        threading.Thread(target=_revert, daemon=True).start()

    def build_bios(self):
        frame = self.frames["bios"]
        text_widget = ctk.CTkTextbox(frame, wrap="word", font=("Consolas", 12))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", BIOS_TEXT)
        text_widget.configure(state="disabled")

if __name__ == "__main__":
    if not is_admin():
        print("Requesting administrator privileges...")
        run_as_admin()
    else:
        app = TrixOSApp()
        app.mainloop()