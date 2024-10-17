import cv2
from ultralytics import YOLO
from gtts import gTTS
import os
import pygame
import time

# Function to speak text
def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("output.mp3")

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():  # Wait for the music to finish playing
        continue

    time.sleep(0.5)  # Small delay to ensure the file is not in use
    pygame.mixer.quit()  # Quit the mixer to release resources
    os.remove("output.mp3")  # Remove the file after playing

# Load YOLOv8 model (pre-trained on COCO dataset)
model = YOLO('yolov8n.pt')  # Load the YOLOv8 Nano model

# Open the laptop camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret or frame is None:  # Check if frame is not captured
        print("No image in frame. Please check the camera.")
        time.sleep(1)  # Delay before retrying
        continue  # Skip to the next iteration

    # Perform object detection on the frame
    results = model(frame)

    # Process the results
    for obj in results[0].boxes:  # Iterate over detected objects
        label = model.names[int(obj.cls[0])]  # Get label
        confidence = obj.conf[0].item()  # Get confidence score

        # Print detection information to the terminal
        print(f"Detected: {label} | Confidence: {confidence:.2f}")

        if confidence > 0.4:  # Adjust the threshold as needed
            # Speak the detected object
            speak(f"A {label} is in front of you")
            time.sleep(7)  # Delay for 7 seconds before the next response

    # Render the results on the frame
    result_frame = results[0].plot()

    # Display the frame with detection
    cv2.imshow('YOLOv8 Object Detection', result_frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
