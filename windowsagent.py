import getwindowsprocess
import requests
import socket
import time

SERVER = "http://localhost:8000"
def collect():
    processes =getwindowsprocess.inspect_processes()
    return {
        "device": socket.gethostname(),
        "os":"windows",
        "processes": processes
    }
while True:
    try:
        requests.post(f"{SERVER}/push/windows", json=collect())
        print("Data pushed successfully!")
    except Exception as e:
        print("Error:", e)
    time.sleep(5)  