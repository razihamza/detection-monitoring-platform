# fetchfirebase.py

import firebase_admin
from firebase_admin import credentials, db 
import requests
import json

#replace path to your firebase adminsdk.json file
cred = credentials.Certificate("F:/projects/detection-monitoring-platform/tester/mainproject-1ebb8-firebase-adminsdk-zsovn-dda1b70928.json")  # Path to your Firebase service account key
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mainproject-1ebb8-default-rtdb.firebaseio.com/'
})


def get_sensor_data():
    ref = db.reference("/")
    data = ref.get()

    sensor_data = {
        "DHT": {
            "humidity": data.get("DHT", {}).get("humidity", 0),
            "temperature": data.get("DHT", {}).get("temperature", 0)
        },
        "Hydrogen": {
            "concentration": data.get("Hydrogen", {}).get("concentration", 0)
        }
    }

    return sensor_data

if __name__ == "__main__":
    while True:
        sensor_data = get_sensor_data()
        requests.post("http://localhost:8000/sensor_data", json=sensor_data)
        print(sensor_data)
