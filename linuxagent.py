import linux_pcb_scheduler_inspector
import requests
import socket
import time

SERVER = "https://encouraged-ambient-overseas-thousand.trycloudflare.com"

def collect():
    processes =linux_pcb_scheduler_inspector.inspect_processes()
    return {
        "device": socket.gethostname(),
        "os":"linux",
        "processes": processes
    }
while True:
    try:
        requests.post(f"{SERVER}/push/linux", json=collect())
        print("Data pushed successfully!")
    except Exception as e:
        print("Error:", e)
    time.sleep(5)  