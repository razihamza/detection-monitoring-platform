import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
import cv2
import time
import requests
import pygame

# Initialize pygame
pygame.mixer.init()

# Function to play the alarm sound
def play_alarm_sound():
    pygame.mixer.music.load("alarm-sound.mp3")  # Path to your alarm sound file
    pygame.mixer.music.play()  # Play the alarm sound indefinitely

# loading the stored model from file
model = load_model('Fire-64x64-color-v7-soft.h5')

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

IMG_SIZE = 64

def send_score_to_main(score):
    endpoint = "http://localhost:8000/detection_score"
    response = requests.post(endpoint, json={"score": score})
    print(response.json())

# Set the threshold probability
threshold_prob = 75

# Set the duration for which the probability must remain above the threshold to trigger the alarm
alarm_duration = 3  # seconds

# Initialize variables to keep track of alarm conditions
alarm_start_time = None
alarm_triggered = False

while True:
    rval, image = cap.read()

    if rval:
        orig = image.copy()

        # Preprocess image
        image_resized = cv2.resize(image, (IMG_SIZE, IMG_SIZE))  
        image_rescaled = image_resized.astype("float") / 255.0
        image_expanded = np.expand_dims(image_rescaled, axis=0)

        # Predict fire probability
        fire_prob = model.predict(image_expanded)[0][0] * 100

        # Send fire probability to main
        send_score_to_main(fire_prob)

        # Check if fire probability is above threshold
        if fire_prob >= threshold_prob:
            if not alarm_triggered:  # Start the alarm if it's not already playing
                alarm_start_time = time.time()  # Record the time when the alarm started
                alarm_triggered = True
        else:
            alarm_triggered = False  # Reset alarm state

        # Check if the alarm has been triggered for the specified duration
        if alarm_triggered and time.time() - alarm_start_time >= alarm_duration:
            play_alarm_sound()  # Play the alarm sound
            alarm_triggered = False  # Reset alarm state

        # Draw rectangle box around the fire area
        gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            # Find the largest contour and draw a rectangle around it
            c = max(contours, key=cv2.contourArea)
            (x, y, w, h) = cv2.boundingRect(c)
            if fire_prob >= threshold_prob:
                cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red color (BGR format)
            else:
                cv2.rectangle(orig, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue color (BGR format)

        # Display output
        label = "Fire Probability: " + str(fire_prob)
        cv2.putText(orig, label, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Output", orig)

        key = cv2.waitKey(1)
        if key == 27: # exit on ESC
            break
    else:
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
