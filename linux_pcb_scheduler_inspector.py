import psutil
import datetime
import subprocess
import re
import os
import shutil

processes = []

def format_bytes(b):
    if b is None or b == 0:
        return "0.00 MB"
    try:
        return f"{b / (1024*1024):.2f} MB"
    except Exception:
        return str(b)

LINUX_PROCESS_PURPOSE = {
   "mtk_wmtd": "MediaTek NAND/EMMC Flash Translation Layer manager",
    "mtk_wmtd_worker": "Worker thread for MediaTek flash mapping operations",
    "kworker/0:1": "Kernel worker thread handling deferred tasks",
    "jbd2/mmcblk0p22": "Journaling thread for ext4 filesystem on partition mmcblk0p22",
   "systemd": "Core init system that manages services and system startup",
    "init": "Parent of all processes, responsible for boot initialization",
    "udevd": "Handles device events and manages /dev entries",
    "dbus-daemon": "Message bus for inter-process communication",
    "NetworkManager": "Manages network connections and WiFi",
    "wpa_supplicant": "Handles WiFi authentication and WPA encryption",
    "cron": "Runs scheduled background tasks",
    "irqbalance": "Distributes hardware interrupts across CPU cores",
    "sshd": "Secure Shell Daemon for remote access",
    "rsyslogd": "System log message handler",
    "cupsd": "Printer service manager",
    "bluetoothd": "Bluetooth device manager",
    "ModemManager": "Controls cellular modem hardware",
    "avahi-daemon": "Service discovery on local network",
    "pipewire": "Audio/video routing and processing server",
    "pipewire-pulse": "PulseAudio compatibility layer for PipeWire",
    "wireplumber": "PipeWire session manager",
    "gnome-shell": "Main GNOME desktop interface",
    "mutter": "GNOME window manager and compositor",
    "tracker-miner-fs": "Search indexer for files",
    "tracker-store": "Database service for GNOME Tracker",
    "gdm-session-worker": "Manages GNOME login sessions",
    "ibus-daemon": "Input method engine for multilingual typing",
    "ibus-engine-simple": "Simple input engine for IBus",
    "ibus-x11": "X11 backend for IBus input system",
    "gjs": "GNOME JavaScript runtime for extensions",
    "xdg-desktop-portal": "Flatpak sandbox permission broker",
    "xdg-document-portal": "Provides file access to sandboxed apps",
    "xdg-permission-store": "Stores app permission settings",
    "gvfsd": "Virtual filesystem service",
    "gvfsd-trash": "Manages Trash/Recycle Bin",
    "pool_workqueue_release": "Kernel worker process responsible for releasing work items from workqueues",
"Kworker/R-rcu_gp": "Kernel worker for RCU (Read-Copy-Update) grace-period tasks",
"kworker/R-sync_wq": "Kernel worker for synchronous workqueue tasks",
"kworker/R-kvfree_rcu_reclaim": "Kernel worker reclaiming memory via RCU",
"kworker/R-slub_flushwq": "Kernel worker for flushing SLUB caches",
"kworker/R-netns": "Kernel worker for network namespace related tasks",
"kworker/u8:0-ipv6_addrconf": "Kernel worker for IPv6 address configuration",
"kworker/R-mm_percpu_wq": "Kernel worker for per-CPU memory management tasks",
"rcu_tasks_kthread": "RCU kernel thread for normal task updates",
"rcu_tasks_rude_kthread": "RCU kernel thread for urgent task updates",
"rcu_tasks_trace_kthread": "RCU kernel thread for tracing task updates",
"rcu_preempt": "RCU kernel thread handling preemption",
"rcu_exp_par_gp_kthread_worker/0": "RCU kernel worker handling expedited grace-period work on CPU 0",
"rcu_exp_gp_kthread_worker": "RCU kernel worker for expedited grace-period tasks",
"idle_inject/0": "Kernel worker injecting idle tasks on CPU 0",
"cpuhp/0": "CPU hotplug thread managing CPU 0 online/offline state",
"cpuhp/1": "CPU hotplug thread managing CPU 1 online/offline state",
"idle_inject/1": "Kernel worker injecting idle tasks on CPU 1",
"migration/1": "Kernel thread for task migration on CPU 1",
"ksoftirqd/1": "Kernel thread handling soft interrupts on CPU 1",
"kworker/1:0H-events_highpri": "High-priority kernel worker for events on CPU 1",
"kdevtmpfs": "Kernel device filesystem manager",
"kworker/R-inet_frag_wq": "Kernel worker for IP fragmentation tasks",
"khungtaskd": "Kernel watchdog thread detecting hung tasks",
"oom_reaper": "Out-of-memory reaper, frees memory when system is low",
"kworker/R-writeback": "Kernel worker handling writeback of dirty pages",
"ksmd": "Kernel thread for kernel samepage merging (KSM)",
    "gvfsd-metadata": "Handles file metadata",
    "gvfs-gphoto2-volume-monitor": "Monitors camera devices",
    "gvfs-mtp-volume-monitor": "Detects Android phones (MTP)",
    "jbd2/mmcblk0p22": "Journaling thread for ext4 filesystem",
    "ext4lazyinit": "Lazy initializer for ext4 filesystem structures",
    "kworker/0:1-events": "Kernel worker thread for async events",
    "kworker/1:2-mm": "Kernel worker handling memory management tasks",
    "kworker/u8:3": "Unbound worker thread for general kernel jobs",
    "rcu_sched": "Read-Copy-Update scheduler thread",
    "rcu_bh": "RCU thread for bottom-half processing",
    "ksoftirqd/0": "Handles software interrupts on CPU0",
    "migration/0": "Moves processes between CPU cores",
    "watchdog/0": "Monitors CPU stall conditions",
    "kswapd0": "Swaps memory pages when RAM is low",
    "khugepaged": "Manages huge page memory optimization",
    "mdadm": "Manages RAID arrays",
    "dhclient": "Gets IP address via DHCP",
    "polkitd": "Authorization service for privileged actions",
    "cups-browsed": "Detects network printers",
"journald": "Collects and stores logs for systemd",
    "systemd-logind": "Manages user logins and seats",
    "systemd-udevd": "Handles hardware device initialization",
    "systemd-resolved": "DNS resolver and caching service",
    "systemd-hostnamed": "Provides hostname information",
    "systemd-localed": "Keyboard and locale settings manager",
    "systemd-timesyncd": "Syncs system time using NTP",
    "colord": "Manages color profiles for displays/printers",
    "packagekitd": "Backend for installing/updating software",
    "snapd": "Manages Snap applications and updates",
    "snap": "Helper process for Snap packages",
    "flatpak": "Runs sandboxed Flatpak apps",
    "xdg-desktop-portal-gtk": "GTK backend for portal permissions",
    "xdg-desktop-portal-gnome": "GNOME-specific portal service",
    "rtkit-daemon": "Gives real-time priority to audio/video apps",
    "gnome-keyring-daemon": "Stores passwords, certificates, SSH keys",
    "seahorse": "GUI for managing keyrings and passwords",
    "gdm-wayland-session": "Starts GNOME session on Wayland",
    "gdm-x-session": "Starts GNOME session on Xorg",
    "gsd-power": "Power management and battery policies",
    "gsd-media-keys": "Handles volume/brightness hotkeys",
    "gsd-color": "Color calibration for GNOME",
    "gsd-datetime": "Time/date settings management",
    "gsd-printer": "Manages printers in GNOME",
    "gsd-wacom": "Wacom tablet configuration",
    "gsd-mouse": "Mouse/touchpad settings handler",
    "gsd-xsettings": "Manages UI theme and fonts",
    "evolution-calendar-factory": "Calendar backend for GNOME",
    "evolution-source-registry": "Stores online account sources",
    "evolution-data-server": "Calendar, contacts, mail backend",
    "update-notifier": "Checks for system updates",
    "mission-control-5": "Handles chat messaging accounts",
    "goa-daemon": "GNOME Online Accounts",
    "goa-identity-service": "Handles account authentication",
    "ibus-dconf": "Loads IBus configuration from dconf",
    "ibus-portal": "IBus flatpak portal interface",
    "ibus-extension-gtk3": "GTK3 input extension",
    "ibus-extension-gtk4": "GTK4 input extension",
    "bash": "Command-line shell",
    "zsh": "Z-shell command processor",
    "fish": "Friendly interactive shell",
    "python3": "Python interpreter",
    "node": "Node.js JavaScript runtime",
    "code": "Visual Studio Code editor",
    "chrome": "Google Chrome browser",
    "chrome_crashpad_handler": "Crash reporting for Chrome",
    "firefox": "Firefox browser",
    "Web Content": "Firefox tab rendering process",
    "WebExtensions": "Runs Firefox browser extensions",
    "Utility Process": "Firefox background utility worker",
    "RDD Process": "Firefox remote data decoder",
    "Isolated Web Co": "Firefox site-isolated content",
    "Socket Process": "Network/socket operations for browser",
"privileged-utility": "Browser privileged task handler",
    "gpu-process": "Handles GPU acceleration tasks",
    "browser-extensions": "Manages browser extensions",
    "media-playback": "Media playback process for browser",
    "network-service": "Handles network requests for browser",
    "crash-reporter": "Collects crash reports for applications",
    "forkserver": "Python multiprocessing fork server",
    "tracker-miner-fs-3": "File indexing for GNOME search",
    "tracker-store": "Database store for GNOME Tracker",
    "tracker-extract": "Extracts metadata from files",
    "tracker-miner-apps": "Indexes application metadata",
    "tracker-miner-user-guides": "Indexes user guide files",
    "tracker-miner-fs": "File system metadata extractor",
    "Xwayland": "X11 applications run on Wayland",
    "mutter": "GNOME window compositor",
    "mutter-x11": "X11-specific compositor tasks",
    "gnome-shell-extension": "GNOME extension process",
    "evolution-alarm-notify": "Calendar alarm notifications",
    "evolution-addressbook-factory": "Contacts backend service",
    "gvfsd-metadata": "Manages file metadata",
    "gvfsd-trash": "Handles trash/recycle bin",
    "gvfsd-recent": "Manages recently used files",
    "gvfs-udisks2-volume-monitor": "Monitors USB/disk events",
    "gvfs-gphoto2-volume-monitor": "Monitors cameras via gphoto2",
    "gvfs-afc-volume-monitor": "Monitors iPhone/iPad connections",
    "gvfs-mtp-volume-monitor": "Monitors Android MTP devices",
    "gvfs-goa-volume-monitor": "Monitors online account storage",
    "xdg-document-portal": "Provides controlled file access for sandboxed apps",
    "xdg-permission-store": "Stores Flatpak/portal permissions",
    "xdg-desktop-portal": "Desktop portal broker for sandbox apps",
    "xdg-desktop-portal-gnome": "GNOME-specific portal backend",
    "xdg-desktop-portal-gtk": "GTK portal backend",
    "rtkit-daemon": "Real-time priority manager for apps",
    "at-spi-bus-launcher": "Accessibility bus launcher",
    "at-spi2-registryd": "Accessibility registry daemon",
    "ibus-daemon": "Input method framework daemon",
    "ibus-engine-simple": "Simple IBus input engine",
    "ibus-x11": "X11 backend for IBus",
    "gnome-keyring-daemon": "Manages stored passwords/keys",
    "gcr-ssh-agent": "Manages SSH keys",
    "seahorse": "Keyring manager GUI",
    "gsd-smartcard": "Smart card support",
    "gsd-sound": "Sound configuration",
    "gsd-disk-utility-notify": "Disk notifications",
    "gsd-housekeeping": "Background system tasks",
    "gsd-sharing": "Desktop sharing settings",
    "gsd-rfkill": "Wi-Fi/Bluetooth on/off manager",
    "gsd-screensaver-proxy": "Lock screen integration",
    "packagekitd": "Software installation/updating daemon",
    "colord": "Color profile management",
    "journald": "System log collection",
    "systemd-logind": "Manages user logins and seats",
    "systemd-udevd": "Handles device initialization",
 "systemd-timesyncd": "Synchronizes system clock with network time",
    "systemd-networkd": "Manages network configuration and devices",
    "systemd-resolved": "DNS resolver service",
    "polkitd": "Authorization manager for system actions",
    "dbus-daemon": "Inter-process communication service",
    "modemmanager": "Manages mobile broadband devices",
    "NetworkManager": "Handles network connections and switching",
    "cupsd": "Print server daemon",
    "avahi-daemon": "mDNS/DNS-SD service discovery",
    "cron": "Schedules recurring tasks",
    "atd": "Handles scheduled jobs",
    "ssh-agent": "Manages SSH authentication keys",
    "agetty": "TTY login manager",
    "login": "Handles user login sessions",
    "rsyslogd": "System log daemon",
    "kerneloops": "Collects kernel crash information",
    "kworker": "Kernel worker process for hardware/system tasks",
    "ksoftirqd": "Kernel soft IRQ handler",
    "rcu_sched": "Kernel RCU scheduler task",
    "rcu_bh": "Kernel RCU bottom-half task",
    "migration": "CPU task migration for load balancing",
    "watchdog": "Monitors system health and responsiveness",
    "kthreadd": "Kernel thread daemon",
    "kswapd": "Manages virtual memory and swap",
    "jbd2": "Journaling block device handler",
    "ext4-rsv-conver": "Ext4 filesystem reserved blocks converter",
    "systemd-journald": "Collects and stores system logs",
    "systemd-udevd": "Device manager for kernel events",
    "systemd-coredump": "Handles core dumps",
    "irq/nn-mouse": "Interrupt handler for mouse devices",
    "irq/nn-keyboard": "Interrupt handler for keyboard devices",
    "irq/nn-usb": "Interrupt handler for USB devices",
    "kblockd": "Block device I/O handler",
    "kmpathd": "Multipath device handler",
    "bioset": "Manages block I/O request sets",
    "kauditd": "Kernel audit daemon",
    "kpsmoused": "PS/2 mouse daemon",
    "scsi_eh_0": "SCSI error handler for device 0",
    "scsi_tmf_0": "SCSI task management function handler",
    "scsi_eh_1": "SCSI error handler for device 1",
    "scsi_tmf_1": "SCSI task management function handler for device 1",
    "nvme": "NVMe device kernel driver",
    "nvme0q0": "NVMe queue process",
    "bioset": "Manages block I/O request sets",
    "kmpath_handlerd": "Multipath device management daemon",
    "kdmflush": "Kernel DMA memory flush process",
    "ksuspend_usbd": "USB suspend/resume handler",
    "ipv6_addrconf": "Handles IPv6 address configuration",
    "deferwq": "Kernel deferred work queue",
    "kthrotld": "Kernel I/O throttling daemon",
    "rpciod": "RPC I/O handling daemon",
    "xfsalloc": "XFS filesystem allocation task",
    "xfs_mru_cache": "XFS most recently used cache manager",
    "xfslogd": "XFS filesystem logging daemon",
    "xfs-buf/dm-0": "XFS buffer I/O task for device dm-0","xfs-data/sda1": "XFS filesystem data I/O for device sda1",
    "xfs-conv/sda1": "XFS filesystem conversion task for sda1",
    "xfs-cil/sda1": "XFS commit item list task",
    "xfs-reclaim": "XFS inode reclaim daemon",
    "xfsaild": "XFS allocator daemon",
    "iscsi_tgt": "iSCSI target daemon",
    "iscsid": "iSCSI initiator daemon",
    "bonding": "Network interface bonding driver",
    "teamd": "Network teaming daemon",
    "tunl0": "IP tunnel interface process",
    "gre0": "Generic routing encapsulation interface process",
    "veth0": "Virtual ethernet interface process",
    "docker-proxy": "Docker networking proxy process",
    "containerd": "Container runtime daemon",
    "runc": "Container execution process",
    "kubelet": "Kubernetes node agent",
    "etcd": "Key-value store daemon",
    "flanneld": "Kubernetes overlay networking daemon",
    "calico-node": "Calico networking agent for containers",
    "cilium-agent": "Cilium container networking agent",
    "containerd-shim": "Container runtime shim for user processes",
    "auditd": "User space audit daemon",
    "tcpdump": "Network packet capture tool",
    "nginx": "Web server daemon",
    "apache2": "HTTP server daemon",
    "mysql": "Database server daemon",
    "postgres": "PostgreSQL database server",
    "redis-server": "Redis in-memory database server",
    "memcached": "Memory caching daemon",
    "java": "Java runtime process",
    "node": "Node.js runtime process",
    "npm": "Node.js package manager process",
    "gunicorn": "Python WSGI HTTP server",
    "uwsgi": "Python uWSGI server process",
    "celery": "Python distributed task queue",
    "rabbitmq-server": "Message broker server",
    "mongod": "MongoDB database server",
    "haproxy": "Load balancer daemon",
    "fail2ban": "Security monitoring daemon",
    "logrotate": "Rotates and compresses logs",
    "rsync": "File synchronization daemon",
    "minikube": "Local Kubernetes cluster manager",
    "kvm": "Kernel-based Virtual Machine process",
    "qemu-system-x86": "QEMU virtual machine process",
    "libvirtd": "Virtual machine management daemon",
    "virtlogd": "Virtual machine logging daemon",
    "docker": "Docker container engine",
    "podman": "Podman container engine",
    "lxc-start": "LXC container start process",
    "lxd": "LXD container management daemon",
    "firewalld": "Dynamic firewall manager",
    "ufw": "Uncomplicated firewall daemon",
    "systemd-logind": "Manages user logins and seats",
    "networkd-dispatcher": "Dispatches network events to scripts",
    "chronyd": "NTP client daemon for time sync",
    "ntpd": "Network time protocol daemon","kthreadd": "Kernel thread daemon",
    "pool_workqueue_release": "Kernel worker process responsible for releasing work items from workqueues",
    "kworker/R-rcu_gp": "Kernel worker for RCU grace-period tasks",
    "kworker/R-sync_wq": "Kernel worker for synchronous workqueue tasks",
    "kworker/R-kvfree_rcu_reclaim": "Kernel worker reclaiming memory via RCU",
    "kworker/R-slub_flushwq": "Kernel worker for flushing SLUB caches",
    "kworker/R-netns": "Kernel worker for network namespace related tasks",
    "kworker/u8:0-ipv6_addrconf": "Kernel worker for IPv6 address configuration",
    "kworker/R-mm_percpu_wq": "Kernel worker for per-CPU memory management tasks",
    "rcu_tasks_kthread": "RCU kernel thread for normal task updates",
    "rcu_tasks_rude_kthread": "RCU kernel thread for urgent task updates",
    "rcu_tasks_trace_kthread": "RCU kernel thread for tracing task updates",
    "ksoftirqd/0": "Handles software interrupts on CPU0",
    "rcu_preempt": "RCU kernel thread handling preemption",
    "rcu_exp_par_gp_kthread_worker/0": "RCU kernel worker handling expedited grace-period work on CPU 0",
    "rcu_exp_gp_kthread_worker": "RCU kernel worker for expedited grace-period tasks",
    "migration/0": "Moves processes between CPU cores",
    "idle_inject/0": "Kernel worker injecting idle tasks on CPU 0",
    "cpuhp/0": "CPU hotplug thread managing CPU 0 online/offline state",
    "cpuhp/1": "CPU hotplug thread managing CPU 1 online/offline state",
    "idle_inject/1": "Kernel worker injecting idle tasks on CPU 1",
    "migration/1": "Kernel thread for task migration on CPU 1",
    "ksoftirqd/1": "Kernel thread handling soft interrupts on CPU 1",
    "kworker/1:0H-events_highpri": "High-priority kernel worker for events on CPU 1",
    "kdevtmpfs": "Kernel device filesystem manager",
    "kworker/R-inet_frag_wq": "Kernel worker for IP fragmentation tasks",
    "kauditd": "Kernel audit daemon",
    "khungtaskd": "Kernel watchdog thread detecting hung tasks",
    "oom_reaper": "Out-of-memory reaper, frees memory when system is low",
    "kworker/R-writeback": "Kernel worker handling writeback of dirty pages",
    "kcompactd0": "Kernel thread for memory compaction",
    "ksmd": "Kernel thread for kernel samepage merging (KSM)",
    "khugepaged": "Manages huge page memory optimization",
    "kworker/R-kintegrityd": "Kernel worker for integrity checking",
    "kworker/R-kblockd": "Kernel worker handling block I/O tasks",
    "kworker/R-blkcg_punt_bio": "Kernel worker handling block cgroup punt tasks",
    "irq/9-acpi": "ACPI interrupt handler",
    "kworker/R-tpm_dev_wq": "Kernel worker for TPM device tasks",
    "kworker/R-ata_sff": "Kernel worker for ATA SFF devices",
    "kworker/R-md": "Kernel worker for RAID devices",
    "kworker/R-md_bitmap": "Kernel worker for RAID bitmap tasks",
    "kworker/R-edac-poller": "Kernel worker for EDAC memory error polling",
    "kworker/R-devfreq_wq": "Kernel worker for device frequency scaling",
    "watchdogd": "Kernel watchdog daemon",
    "kswapd0": "Swaps memory pages when RAM is low",
    "ecryptfs-kthread": "Kernel thread for encrypted filesystem",
    "kworker/R-kthrotld": "Kernel worker for I/O throttling",
    "kworker/R-acpi_thermal_pm": "Kernel worker for ACPI thermal management",
    "scsi_eh_0": "SCSI error handler for device 0",
    "kworker/R-scsi_tmf_0": "Kernel worker for SCSI Task Management Functions device 0",
    "scsi_eh_1": "SCSI error handler for device 1",
    "kworker/R-scsi_tmf_1": "Kernel worker for SCSI Task Management Functions device 1",
    "kworker/u10:4-events_power_efficient": "Kernel worker for power-efficient events",
    "kworker/R-mld": "Kernel worker for MLD tasks (IPv6 multicast)",
    "kworker/R-ipv6_addrconf": "Kernel worker for IPv6 address configuration",
    "kworker/u8:1-ipv6_addrconf": "Kernel worker for secondary IPv6 address config",
    "kworker/R-kstrp": "Kernel worker for kernel string tasks",
    "kworker/u11:0": "Kernel worker thread",
    "kworker/u12:0": "Kernel worker thread",
    "kworker/u13:0": "Kernel worker thread",
    "kworker/R-charger_manager": "Kernel worker for charger management",
    "kworker/R-ttm": "Kernel worker for TTM graphics memory manager",
    "kworker/0:2-cgroup_destroy": "Kernel worker for cgroup destruction",
    "scsi_eh_2": "SCSI error handler for device 2",
    "kworker/R-scsi_tmf_2": "Kernel worker for SCSI Task Management Functions device 2",
    "jbd2/sda2-8": "Journaling block device daemon for sda2",
    "kworker/R-ext4-rsv-conversion": "Kernel worker for ext4 reserved block conversion",
    "systemd-journald": "Collects and stores system logs",
    "systemd-udevd": "Device manager for kernel events",
    "systemd-oomd": "Out-of-memory handling daemon",
    "systemd-resolved": "DNS resolver service",
    "systemd-timesyncd": "Synchronizes system clock with network time",
    "psimon": "System performance monitoring daemon",
    "kworker/0:2H-kblockd": "High-priority block device worker on CPU 0",
    "avahi-daemon": "mDNS/DNS-SD service discovery",
    "dbus-daemon": "Inter-process communication service",
    "polkitd": "Authorization manager for system actions",
    "power-profiles-daemon": "Manages power profiles",
    "snapd": "Manages Snap applications and updates",
    "accounts-daemon": "User account management",
    "cron": "Schedules recurring tasks",
    "kworker/R-cryptd": "Kernel crypto worker",
    "switcheroo-control": "GPU switching service",
    "systemd-logind": "Manages user logins and seats",
    "udisksd": "Disk management daemon",
    "NetworkManager": "Handles network connections and switching",
    "wpa_supplicant": "Handles WiFi authentication and WPA encryption",
    "rsyslogd": "System log daemon",
    "ModemManager": "Controls cellular modem hardware",
    "cupsd": "Print server daemon",
    "cups-browsed": "Detects network printers",
    "kerneloops": "Collects kernel crash information",
    "gdm-session-worker": "Manages GNOME login sessions",
    "rtkit-daemon": "Real-time priority manager for apps",
    "colord": "Color profile management",
    "upowerd": "Power management daemon",
    "(sd-pam)": "PAM session handler",
    "pipewire": "Audio/video routing and processing server",
    "snapd-desktop-integration": "Snap app desktop integration helper",
    "wireplumber": "PipeWire session manager",
    "pipewire-pulse": "PulseAudio compatibility layer for PipeWire",
    "gnome-keyring-daemon": "Manages stored passwords/keys",
    "gdm-wayland-session": "Starts GNOME session on Wayland",
    "gnome-session-binary": "GNOME session manager",
    "xdg-document-portal": "Provides controlled file access for sandboxed apps",
    "xdg-permission-store": "Stores Flatpak/portal permissions",
    "fusermount3": "FUSE filesystem mount manager",
    "gcr-ssh-agent": "Manages SSH keys",
    "gvfsd": "Virtual filesystem service",
    "gvfsd-fuse": "FUSE layer for virtual filesystem",
    "gnome-shell": "Main GNOME desktop interface",
    "at-spi-bus-launcher": "Accessibility bus launcher",
    "at-spi2-registryd": "Accessibility registry daemon",
    "gnome-shell-calendar-server": "GNOME calendar server",
    "evolution-source-registry": "Stores online account sources",
    "gjs": "GNOME JavaScript runtime for extensions",
    "ibus-daemon": "Input method framework daemon",
    "gsd-color": "Color calibration for GNOME",
    "gsd-datetime": "Time/date settings management",
    "gsd-housekeeping": "Background system tasks",
    "gsd-media-keys": "Handles volume/brightness hotkeys",
    "gsd-power": "Power management and battery policies",
    "gsd-rfkill": "Wi-Fi/Bluetooth on/off manager",
    "gsd-screensaver-proxy": "Lock screen integration",
    "goa-daemon": "GNOME Online Accounts",
    "gsd-smartcard": "Smart card support",
    "gsd-sound": "Sound configuration",
    "gsd-wacom": "Wacom tablet configuration",
    "gsd-disk-utility-notify": "Disk notifications",
    "evolution-alarm-notify": "Calendar alarm notifications",
    "evolution-calendar-factory": "Calendar backend for GNOME",
    "gsd-printer": "Manages printers in GNOME",
    "gvfs-udisks2-volume-monitor": "Monitors USB/disk events",
    "goa-identity-service": "Handles account authentication",
    "ibus-dconf": "Loads IBus configuration from dconf",
    "ibus-extension-gtk3": "GTK3 input extension",
    "ibus-portal": "IBus flatpak portal interface",
    "gvfs-gphoto2-volume-monitor": "Monitors cameras via gphoto2",
    "gvfs-afc-volume-monitor": "Monitors iPhone/iPad connections",
    "gvfs-goa-volume-monitor": "Monitors online account storage",
    "gvfs-mtp-volume-monitor": "Monitors Android MTP devices",
    "evolution-addressbook-factory": "Contacts backend service",
    "ibus-engine-simple": "Simple IBus input engine",
    "gvfsd-trash": "Handles trash/recycle bin",
    "xdg-desktop-portal": "Desktop portal broker for sandbox apps",
    "tracker-miner-fs-3": "File indexing for GNOME search",
    "xdg-desktop-portal-gnome": "GNOME-specific portal backend",
    "xdg-desktop-portal-gtk": "GTK portal backend",
    "gvfsd-metadata": "Manages file metadata",
    "update-notifier": "Checks for system updates",
    "gvfsd-recent": "Manages recently used files",
    "code": "Visual Studio Code editor",
    "chrome_crashpad_handler": "Crash reporting for Chrome",
    "Xwayland": "X11 applications run on Wayland",
    "gsd-xsettings": "Manages UI theme and fonts",
    "ibus-x11": "X11 backend for IBus",
    "mutter-x11-frames": "Mutter window compositor frames",
    "fwupd": "Firmware update daemon",
    "kworker/u9:1-kvfree_rcu_reclaim": "Kernel worker reclaiming memory via RCU",
    "firefox": "Firefox browser",
    "crashhelper": "Crash reporting helper",
    "forkserver": "Python multiprocessing fork server",
    "Socket Process": "Network/socket operations for browser",
    "Privileged Cont": "Privileged content process for browser",
    "RDD Process": "Firefox remote data decoder",
    "Isolated Web Co": "Firefox site-isolated content",
    "snap": "Helper process for Snap packages",
    "WebExtensions": "Runs Firefox browser extensions",
    "Web Content": "Firefox tab rendering process",
    "Utility Process": "Firefox background utility worker",
    "kworker/u10:2-events_power_efficient": "Kernel worker for power-efficient events",
    "kworker/u10:0-kvfree_rcu_reclaim": "Kernel worker reclaiming memory via RCU",
    "gnome-terminal": "GNOME terminal emulator",
    "gnome-terminal.real": "GNOME terminal process",
    "gnome-terminal-server": "GNOME terminal server",
    "kworker/1:1-events": "Kernel worker handling events",
    "bash": "Command-line shell",
    "gvfsd-network": "Network virtual filesystem daemon",
    "gvfsd-dnssd": "DNS-SD virtual filesystem daemon",
    "kworker/0:0H-kblockd": "High-priority block device worker on CPU 0",
    "kworker/u10:1-events_power_efficient": "Kernel worker for power-efficient events",
    "kworker/u9:0-events_power_efficient": "Kernel worker for power-efficient events",
    "kworker/0:0-cgroup_destroy": "Kernel worker for cgroup destruction",
    "kworker/1:2-events": "Kernel worker handling events",
    "kworker/u9:2-kvfree_rcu_reclaim": "Kernel worker reclaiming memory via RCU",
    "kworker/0:1-mm_percpu_wq": "Kernel worker for per-CPU memory tasks",
    "python3": "Python interpreter",
}

def get_scheduling_info(pid, timeout_sec=1.0):
    
    chrt_path = shutil.which("chrt")
    if not chrt_path:
        return ("chrt not found", "Install 'util-linux' or run on system with chrt (/usr/bin/chrt)")

    try:
        result = subprocess.run([chrt_path, "-p", str(pid)],
                                capture_output=True, text=True, check=True, timeout=timeout_sec)
        out = result.stdout.strip()
     
        m = re.search(r"current scheduling policy: (SCHED_[A-Z0-9_]+)", out)
        if m:
            policy = m.group(1)
        else:
            policy = "Unknown (parsed-none)"

        if policy == "SCHED_OTHER":
            algo = "Completely Fair Scheduler (CFS) — normal user processes"
        elif policy in ("SCHED_FIFO", "SCHED_RR"):
            algo = "Real-time scheduling (FIFO or Round-Robin) — real-time priority"
        elif policy == "SCHED_BATCH":
            algo = "Batch scheduling (for background batch jobs)"
        elif policy == "SCHED_IDLE":
            algo = "Idle scheduling (very low priority)"
        else:
            algo = f"Custom/other policy ({policy})"

        return (policy, algo)

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if hasattr(e, 'stderr') else ""
        if "Operation not permitted" in stderr or "permission denied" in stderr.lower():
            return ("Access Denied", "Run with sudo to query real-time scheduling")
        return ("chrt failed", stderr or "chrt error")
    except subprocess.TimeoutExpired:
        return ("chrt timeout", "chrt call timed out")
    except Exception as e:
        return ("chrt error", str(e))

def inspect_processes():
    global Countprocesses
    Countprocesses = 0
    try:
        os.system('clear')
    except:
        pass

    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except Exception:
            pass
    all_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            pid = proc.info.get('pid')
            name = proc.info.get('name') or "<unknown>"
            user = proc.info.get('username') or "<unknown>"

            p = psutil.Process(pid)

            start_time = "N/A"
            try:
                st = datetime.datetime.fromtimestamp(p.create_time())
                start_time = st.isoformat()
            except Exception:
                pass

            try:
                cpu_percent = p.cpu_percent(interval=None)
            except Exception:
                cpu_percent = 0.0

            try:
                cpu_times = p.cpu_times()
                cpu_user = getattr(cpu_times, 'user', 0.0)
                cpu_system = getattr(cpu_times, 'system', 0.0)
                total_cpu_time = cpu_user + cpu_system
            except Exception:
                cpu_user = cpu_system = total_cpu_time = 0.0

            try:
                mem = p.memory_info()
                rss = getattr(mem, 'rss', 0)
                vms = getattr(mem, 'vms', 0)
            except Exception:
                rss = vms = 0

            try:
                threads = p.num_threads()
            except Exception:
                threads = 0
            try:
                handles = p.num_fds()
            except Exception:
                handles = 0
            try:
                ctx = p.num_ctx_switches()
                ctx_vol = getattr(ctx, 'voluntary', 0)
                ctx_invol = getattr(ctx, 'involuntary', 0)
            except Exception:
                ctx_vol = ctx_invol = 0

            try:
                io = p.io_counters()
                io_read = getattr(io, 'read_bytes', 0)
                io_write = getattr(io, 'write_bytes', 0)
                io_total = io_read + io_write
            except Exception:
                io_read = io_write = io_total = 0

            try:
                nice_value = p.nice()
            except Exception:
                nice_value = "N/A"

            policy, algorithm = get_scheduling_info(pid)

            description = LINUX_PROCESS_PURPOSE.get(name, "N/A")

            info = {
                'pid': pid,
                'name': name,
                'user': user,
                'description': description,
                'start_time': start_time,
                'cpu_percent': round(cpu_percent, 2),
                'total_cpu_time': round(total_cpu_time, 2),
                'cpu_user_time': round(cpu_user, 2),
                'cpu_system_time': round(cpu_system, 2),
                'memory_rss': format_bytes(rss),
                'memory_vms': format_bytes(vms),
                'threads': threads,
                'handles': handles,
                'ctx_voluntary': ctx_vol,
                'ctx_involuntary': ctx_invol,
                'ctx_total': ctx_vol + ctx_invol,
                'io_read': io_read,
                'io_write': io_write,
                'io_total': io_total,
                'nice': nice_value,
                'scheduling_policy': policy,
                'scheduler_algorithm': algorithm
            }

            all_processes.append(info)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception:
            continue

    return all_processes


if __name__ == "__main__":
    procs = inspect_processes()
    