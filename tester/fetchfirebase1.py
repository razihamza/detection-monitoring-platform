# fetchfirebase.py

import firebase_admin
from firebase_admin import credentials, db 
import requests
from datetime import datetime  # Import datetime module
import time  # Import time module for sleep function

# Replace path to your Firebase service account key
cred = credentials.Certificate("F:/projects/detection-monitoring-platform/tester/mainproject-1ebb8-firebase-adminsdk-zsovn-dda1b70928.json")  
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mainproject-1ebb8-default-rtdb.firebaseio.com/'
})

def get_sensor_data():
    ref = db.reference("/")
    data = ref.get()

    # Extract sensor data from Firebase
    humidity = data.get("DHT", {}).get("humidity", 0)
    temperature = data.get("DHT", {}).get("temperature", 0)
    concentration = data.get("Hydrogen", {}).get("concentration", 0)

    sensor_data = {
        "DHT": {
            "humidity": humidity,
            "temperature": temperature
        },
        "Hydrogen": {
            "concentration": concentration
        }
    }

    return sensor_data

def get_feature_vector():
    ref = db.reference("/")
    data = ref.get()

    # Extract sensor data from Firebase and construct feature vector
    feature_vector = [
        data.get("DHT", {}).get("temperature", 0),
        data.get("DHT", {}).get("humidity", 0),
        data.get("Hydrogen", {}).get("concentration", 0)
    ]

    return feature_vector

if __name__ == "__main__":
    while True:
        try:
            sensor_data = get_sensor_data()
            
            # Send sensor data to /sensor_data endpoint
            requests.post("http://localhost:8000/sensor_data", json=sensor_data)
            
            # Print sensor data
            print("Sensor data sent successfully:", sensor_data)

            # Get feature vector
            feature_vector = get_feature_vector()

            # Send feature vector to /prediction endpoint
            payload = {"feature_vector": feature_vector, "score": False}  # Set score to False
            response = requests.post("http://localhost:8000/prediction", json=payload)
            print("Response from /prediction endpoint:", response.json())
        
        except Exception as e:
            print("An error occurred:", e)
        
        # Sleep for 1 second before fetching data again
        time.sleep(1)
