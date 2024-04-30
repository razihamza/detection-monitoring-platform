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

while True:
    rval, image = cap.read()

    if rval:
        orig = image.copy()

        image = cv2.resize(image, (IMG_SIZE, IMG_SIZE))  
        image = image.astype("float") / 255.0
        image = img_to_array(image)
        image = np.expand_dims(image, axis=0)

        tic = time.time()
        fire_prob = model.predict(image)[0][0] * 100
        toc = time.time()
        print("Time taken = ", toc - tic)
        print("FPS: ", 1 / np.float64(toc - tic))
        print("Fire Probability: ", fire_prob)
        print("Predictions: ", model.predict(image))
        print(image.shape)

        send_score_to_main(fire_prob)

        if fire_prob > 75:  # Change the threshold to 75%
            # Play alarm sound when threshold is met
            play_alarm_sound()

            # Draw a rectangle box around the fire area in red
            # Find the contours of the fire area
            gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)
            thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                # Find the largest contour and draw a rectangle around it in red
                c = max(contours, key=cv2.contourArea)
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red color (BGR format)

        else:  # Draw rectangle in blue for other probabilities
            # Draw a rectangle box around the fire area in blue
            # Find the contours of the fire area
            gray = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (11, 11), 0)
            thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]
            contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) > 0:
                # Find the largest contour and draw a rectangle around it in blue
                c = max(contours, key=cv2.contourArea)
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(orig, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue color (BGR format)

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
