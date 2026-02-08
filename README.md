**Multi-OS Process Monitoring Scheduling Analysis System**

This project is a cross-platform process monitoring and analysis system designed to observe and evaluate running processes across Windows, Linux, and Android operating systems. The system provides a unified interface for retrieving real-time process information, resource utilization, and scheduling-related data, enabling better visibility into operating system behavior.

The application allows users to select a target operating system and displays a live list of active processes. For each process, detailed information is presented, including process name, Process ID (PID), CPU usage, memory consumption, execution status, and system-level statistics. The system continuously updates process data in real time, allowing users to monitor dynamic changes in resource usage.

A key feature of this project is Process Purpose Identification. Each running process is mapped to its functional role to help users understand why a process exists and what task it performs. On Windows, process purposes are partially retrieved directly from the operating system and enhanced using internal mappings. On Linux and Android, process purposes are fully mapped within the system. Android process information is collected using Android Debug Bridge (ADB) from connected physical devices.

The system is designed with a modular architecture, enabling platform-specific monitoring while maintaining a shared backend for data processing and communication. A Python-based backend API handles process retrieval, analysis, and structured data exchange with the Flutter frontend.

**Features**

- Cross-platform support for Windows, Linux, and Android

- Real-time process monitoring

- Display of process name and PID

- CPU and memory usage tracking

- Execution status and system-level details

- Scheduling-related statistics

- Process purpose mapping

- Unified interface for multiple operating systems

- Backend API communication

- Android integration via ADB

**Technology Stack**

- Python (Backend and system monitoring)

- FastAPI (REST API)

- Flutter (Frontend interface)

- psutil (Windows and Linux process monitoring)

- wmi and ctypes (Windows system information)

- subprocess (ADB command execution)

- requests (Backend communication)

- Android Debug Bridge (ADB)

**Purpose**

The project focuses on practical exploration of operating system concepts such as process management, scheduling, and resource utilization. It also demonstrates how monitoring tools can improve system transparency and assist in identifying abnormal or suspicious activity. The system serves as an educational prototype and provides a foundation for future scalable monitoring solutions.
