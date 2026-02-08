from fastapi import FastAPI
import time

app = FastAPI()

windows_data = {}
linux_data = {}
android_data = {}

windows_last_update = 0
linux_last_update = 0
android_last_update = 0

AGENT_TIMEOUT = 300 

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]  

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/push/windows")
def push_windows(payload: dict):
    global windows_data, windows_last_update
    windows_data = payload
    windows_last_update = time.time()  
    return {"status": "ok"}

@app.post("/push/linux")
def push_linux(payload: dict):
    global linux_data, linux_last_update
    linux_data = payload
    linux_last_update = time.time()
    return {"status": "ok"}

@app.post("/push/android")
def push_android(payload: dict):
    global android_data, android_last_update
    android_data = payload
    android_last_update = time.time()
    return {"status": "ok"}

@app.get("/windows")
def get_windows():
    if time.time() - windows_last_update > AGENT_TIMEOUT:
        return {}      
    return windows_data

@app.get("/linux")
def get_linux():
    if time.time() - linux_last_update > AGENT_TIMEOUT:
        return {}
    return linux_data

@app.get("/android")
def get_android():
    if time.time() - android_last_update > AGENT_TIMEOUT:
        return {}
    return android_data
