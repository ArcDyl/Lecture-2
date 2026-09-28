import os
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI")) # Must match the variable in the .env file
db = client["ecse3038"]
devices = db["devices"]

class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool

app = FastAPI()

readings = []

@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))

@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")
    return new_device

@app.get("/rooms/{room}/devices")
def get_devices_by_room(room):
    devices = []
    for device in readings:
        if device["room"] == room:
            devices.append(device)
    if devices == []:
        raise HTTPException(status_code=404, detail="Room not found")
    return devices

# return the average temperature
@app.get("/devices/average")
def average_temp():
    sum_temp = 0
    for device in readings:
        sum_temp+= device['temp']
        avg_temp = sum_temp / len(readings)
    return avg_temp

@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device

@app.get("/devices/online")
def online():
    devices = []
    for device in readings:
        if device["online"] == True:
            devices.append(device)
    return devices

# return the whole dictionary of the hottest device
@app.get("/devices/hottest")
def hottest():
    hottest_temp = 0.0
    hottest_device = None
    for device in readings:
        if device['temp'] > hottest_temp:
            hottest_temp = device['temp']
            hottest_device = device
    return hottest_device

@app.put("/devices/{name}")
def update_device(name: str, updated_device: Device):
    for index, device in enumerate(readings):
        if device["name"] == name:
            readings[index] = updated_device.model_dump()
            return readings[index]
    raise HTTPException(status_code=404, detail="Device not found")

@app.delete("/devices/{name}")
def delete_device(name: str):
    for device in readings:
        if device["name"] == name:
            readings.remove(device)
            return {"Message": "it do"}
    raise HTTPException(status_code=404, detail="it nuh deh deh")
        