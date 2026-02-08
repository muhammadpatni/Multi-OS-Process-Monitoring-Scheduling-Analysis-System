import psutil
import ctypes
from ctypes import wintypes
import datetime
import time
import platform
import  os
import wmi

processes = []

if platform.system().lower() != "windows":
    raise SystemExit("This script is intended to run on Windows.")

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
version = ctypes.WinDLL('version', use_last_error=True)
wmi_obj = wmi.WMI()

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
OpenProcess.restype = wintypes.HANDLE

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = (wintypes.HANDLE,)
CloseHandle.restype = wintypes.BOOL

GetProcessHandleCount = kernel32.GetProcessHandleCount
GetProcessHandleCount.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
GetProcessHandleCount.restype = wintypes.BOOL

GetPriorityClass = kernel32.GetPriorityClass
GetPriorityClass.argtypes = (wintypes.HANDLE,)
GetPriorityClass.restype = wintypes.DWORD

QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD))
QueryFullProcessImageNameW.restype = wintypes.BOOL

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong)
    ]

GetProcessIoCounters = kernel32.GetProcessIoCounters
GetProcessIoCounters.argtypes = (wintypes.HANDLE, ctypes.POINTER(IO_COUNTERS))
GetProcessIoCounters.restype = wintypes.BOOL

def filetime_to_seconds(ft):
    val = (ft.dwHighDateTime << 32) + ft.dwLowDateTime
    return val / 10_000_000.0

PRIORITY_CLASS_MAP = {
    0x00000010: "IDLE",
    0x00000040: "BELOW_NORMAL",
    0x00000020: "NORMAL",
    0x00008000: "ABOVE_NORMAL",
    0x00000080: "HIGH",
    0x00000100: "REALTIME",
}

def priority_class_text(val):
    return PRIORITY_CLASS_MAP.get(val, f"UNKNOWN(0x{val:x})")

def predict_schedulers_for_process(info):
    candidates = []
    candidates.append("Priority-based (preemptive) with time-slicing (Windows default)")
    if info.get('priority_class') in (0x00000100,):
        candidates.insert(0, "Real-time FIFO / Real-time scheduling (highest priority)")
    if info.get('cpu_percent', 0) > 30 or info.get('threads', 0) > 10:
        candidates.append("Round-Robin within same priority (interactive/high CPU)")
    if info.get('ctx_switches_total', 0) > 1000:
        candidates.append("Round-Robin-like with small quantum (high preemption)")
    if info.get('io_bytes', 0) > 10_000_000:
        candidates.append("I/O-aware dynamic priority scheduling (boosts for I/O)")
    candidates.append("Hybrid / Multilevel Feedback Queue (MLFQ)-like behavior (adaptive)")
    seen = set()
    out = []
    for c in candidates:
        if c not in seen:
            out.append(c)
            seen.add(c)
    return out

SYSTEM_DESCRIPTIONS = {
    "System": "Kernel & System (NTOSKRNL)",
    "Registry": "System Registry Process",
    "smss.exe": "Session Manager Subsystem",
    "csrss.exe": "Client/Server Runtime Subsystem",
    "wininit.exe": "Windows Initialization Process",
    "winlogon.exe": "Windows Logon Process",
    "services.exe": "Service Control Manager",
    "lsass.exe": "Local Security Authority Subsystem",
    "svchost.exe": "Service Host Process",
    "dwm.exe": "Desktop Window Manager",
    "spoolsv.exe": "Print Spooler Service",
    "System Idle Process": "Indicates unused CPU time; runs when system is idle.",
    "fontdrvhost.exe": "Font Driver Host — handles font rendering inside user mode.",
    "SearchProtocolHost.exe": "Windows Search Protocol Host — handles search indexing protocols.",
    "IntelCpHDCPSvc.exe": "Intel HDCP Service — manages content protection for Intel graphics.",
    "MemCompression": "Windows Memory Manager compression process — compresses memory pages.",
    "igfxCUIService.exe": "Intel Graphics Control Panel service.",
    "unsecapp.exe": "WMI Sink — receives asynchronous WMI callbacks.",
    "HotKeyServiceUWP.exe": "OEM Hotkey Handler service (HP/Dell hotkeys).",
    "WUDFHost.exe": "Windows User-Mode Driver Framework Host — runs user-mode drivers.",
    "AggregatorHost.exe": "Windows host for background aggregator services.",
    "PresentationFontCache.exe": "WPF font caching service for .NET applications.",
    "CxAudioSvc.exe": "Conexant Audio Service — manages audio enhancements.",
    "SynTPEnhService.exe": "Synaptics TouchPad Enhancement Service.",
    "ibtsiva.exe": "Intel Bluetooth Authentication Service.",
    "armsvc.exe": "Adobe Acrobat Update Service.",
    "CxUtilSvc.exe": "Conexant Audio Utility Service.",
    "valWBFPolicyService.exe": "Windows Biometric Framework policy service (fingerprint).",
    "XtuService.exe": "Intel Extreme Tuning Utility Service.",
    "fpCSEvtSvc.exe": "HP Fingerprint sensor event service.",
    "OneApp.IGCC.WinService.exe": "Intel Graphics Command Center background service.",
    "MsMpEng.exe": "Windows Defender Antivirus engine.",
    "sqlwriter.exe": "SQL Server VSS Writer — enables backup for SQL databases.",
    "servicehost.exe": "Generic Windows service hosting container.",
    "MpDefenderCoreService.exe": "Microsoft Defender core antivirus service.",
    "OfficeClickToRun.exe": "Office Update Service (Click-to-Run).",
    "LanWlanWwanSwitchingServiceUWP.exe": "OEM service for switching Network modes (HP/Dell).",
    "dllhost.exe": "COM Surrogate — runs COM/OLE objects safely.",
    "HPAudioAnalytics.exe": "HP audio analytics background service.",
    "MicTray64.exe": "Microphone tray utility (HP audio).",
    "HPHotkeyNotification.exe": "HP Hotkey Notification service.",
    "WmiPrvSE.exe": "WMI Provider Host — handles WMI operations.",
    "NisSrv.exe": "Windows Defender Network Inspection Service.",
    "SearchFilterHost.exe": "Search filter host (indexing PDFs, documents).",
    "SearchIndexer.exe": "Windows Search Indexing service.",
    "ctfmon.exe": "CTF Loader — manages keyboard input, language bar & IMEs.",
    "SynTPHelper.exe": "Synaptics touchpad helper module.",
    "igfxTray.exe": "Intel Graphics Tray module.",
    "StartMenuExperienceHost.exe": "Windows Start Menu experience host.",
    "TextInputHost.exe": "Windows Text Input framework (emoji panel, touch keyboard).",
    "sqlceip.exe": "SQL Customer Experience Improvement Program service.",
    "WmiPrvSE.exe": "WMI Provider Host — background data provider.",
    "SecurityHealthService.exe": "Windows Security Health Host service.",
    "sqlservr.exe": "SQL Server Database Engine.",
    "WhatsApp.exe": "WhatsApp Desktop App.",
    "audiodg.exe": "Windows Audio Device Graph — handles audio processing.",
    "pet.exe": "Unknown — Probably a custom or third-party application (need path)."
}

def get_description_wmi(path):
    try:
        for file in wmi_obj.CIM_DataFile(Name=path):
            return file.FileDescription
    except:
        return None

def get_file_description(path):
    try:
        size = version.GetFileVersionInfoSizeW(path, None)
        if size == 0:
            return None
        res = ctypes.create_string_buffer(size)
        if not version.GetFileVersionInfoW(path, 0, size, res):
            return None
        lptr = ctypes.c_void_p()
        lsize = wintypes.UINT()
        if not version.VerQueryValueW(res, r"\VarFileInfo\Translation", ctypes.byref(lptr), ctypes.byref(lsize)):
            return None
        if lsize.value < 4:
            return None
        lang, codepage = ctypes.cast(lptr, ctypes.POINTER(ctypes.c_ushort))[0:2]
        sub_block = f"\\StringFileInfo\\{lang:04x}{codepage:04x}\\FileDescription"
        sptr = ctypes.c_void_p()
        ssize = wintypes.UINT()
        if version.VerQueryValueW(res, sub_block, ctypes.byref(sptr), ctypes.byref(ssize)):
            return ctypes.wstring_at(sptr)
    except:
        return None
    return None

def inspect_processes():
    global Countprocesses
    os.system('cls')

    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except:
            pass
    time.sleep(1)

    all_processes = []

    for p in psutil.process_iter(['pid','name','username']):
        try:
            pid = p.info['pid']
            name = p.info.get('name') or "<unknown>"
            user = p.info.get('username') or "<unknown>"

            h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            opened = True if h else False

            cpu_pct = round(p.cpu_percent(interval=None), 2)
            cpu_times = p.cpu_times()
            user_time = round(cpu_times.user, 2)
            system_time = round(cpu_times.system, 2)
            total_cpu_time = round(user_time + system_time, 2)
            mem = p.memory_info()
            rss_mb = round(mem.rss / (1024*1024), 2)
            vms_mb = round(mem.vms / (1024*1024), 2)
            threads = p.num_threads()
            try:
                ctx = p.num_ctx_switches()
                ctx_vol = ctx.voluntary
                ctx_invol = ctx.involuntary
                ctx_total = ctx_vol + ctx_invol
            except:
                ctx_vol = ctx_invol = ctx_total = 0
            try:
                io = p.io_counters()
                io_read = io.read_bytes
                io_write = io.write_bytes
                io_bytes = io_read + io_write
            except:
                io_read = io_write = io_bytes = 0
            try:
                start_time = datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
            except:
                start_time = "N/A"

            priority_class = None
            proc_image = None
            handles_count = None
            io_counters_native = None
            kernel_time = None
            user_time_native = None

            if opened:
                try:
                    size = wintypes.DWORD(260)
                    buf = ctypes.create_unicode_buffer(260)
                    if QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                        proc_image = buf.value
                except:
                    proc_image = None
                try:
                    pc = GetPriorityClass(h)
                    priority_class = pc
                except:
                    priority_class = None
                try:
                    hc = wintypes.DWORD()
                    if GetProcessHandleCount(h, ctypes.byref(hc)):
                        handles_count = hc.value
                except:
                    handles_count = None
                try:
                    ioc = IO_COUNTERS()
                    if GetProcessIoCounters(h, ctypes.byref(ioc)):
                        io_counters_native = {
                            'read_bytes': ioc.ReadTransferCount,
                            'write_bytes': ioc.WriteTransferCount,
                        }
                except:
                    io_counters_native = None
                try:
                    creation = wintypes.FILETIME()
                    exit_time = wintypes.FILETIME()
                    kernel_ft = wintypes.FILETIME()
                    user_ft = wintypes.FILETIME()
                    if kernel32.GetProcessTimes(h, ctypes.byref(creation), ctypes.byref(exit_time),
                                               ctypes.byref(kernel_ft), ctypes.byref(user_ft)):
                        kernel_time = round(filetime_to_seconds(kernel_ft), 2)
                        user_time_native = round(filetime_to_seconds(user_ft), 2)
                except:
                    kernel_time = user_time_native = None
                CloseHandle(h)

            description = None
            if proc_image:
                description = get_description_wmi(proc_image)
                if not description:
                    description = get_file_description(proc_image)
            if not description and name in SYSTEM_DESCRIPTIONS:
                description = SYSTEM_DESCRIPTIONS[name]
            if not description:
                description = "N/A"

            scheduling_algorithms = predict_schedulers_for_process({
                'priority_class': priority_class,
                'cpu_percent': cpu_pct,
                'threads': threads,
                'ctx_switches_total': ctx_total,
                'io_bytes': io_bytes
            })

            process_info = {
                'pid': pid,
                'name': name,
                'description': description,
                'user': user,
                'proc_image': proc_image,
                'cpu_percent': cpu_pct,
                'user_time': user_time,
                'total_cpu_time': total_cpu_time,
                'kernel_time_native': kernel_time,
                'user_time_native': user_time_native,
                'rss_mb': rss_mb,
                'vms_mb': vms_mb,
                'threads': threads,
                'ctx_vol': ctx_vol,
                'ctx_invol': ctx_invol,
                'ctx_total': ctx_total,
                'io_read': io_read,
                'io_write': io_write,
                'io_bytes': io_bytes,
                'io_native': io_counters_native,
                'priority_class': priority_class,
                'handles': handles_count,
                'start_time': start_time,
                'scheduling_algorithms': scheduling_algorithms
            }

            all_processes.append(process_info)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return all_processes


if __name__ == "__main__":
    processes = inspect_processes()
    print("program done,,")
