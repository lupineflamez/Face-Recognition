import cv2
import numpy as np
import random
import time
from picamera2 import Picamera2

# Use the exact system cascades that face_app.py uses
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

# Define Challenges
CHALLENGES = ["TURN LEFT OR RIGHT", "SMILE"]
current_challenge = random.choice(CHALLENGES)

# Challenge Parameters
CHALLENGE_TIMEOUT = 6.0  # seconds
start_time = time.time()
challenge_status = "PENDING"

print("Initializing PiCamera2 pipeline...")
picam2 = Picamera2()
picam2.start()
print("Camera pipeline successfully initialized!")

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        elapsed_time = time.time() - start_time
        
        if len(faces) > 0 and challenge_status == "PENDING":
            for (x, y, fw, fh) in faces:
                roi_gray = gray[y:y+fh, x:x+fw]
                
                if current_challenge == "TURN LEFT OR RIGHT":
                    eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10, minSize=(20, 20))
                    if len(eyes) <= 1:
                        challenge_status = "VERIFIED"
                        
                elif current_challenge == "SMILE":
                    mouth_roi_gray = roi_gray[int(fh/2):fh, :]
                    smiles = smile_cascade.detectMultiScale(mouth_roi_gray, 1.7, 22, minSize=(15, 15))
                    if len(smiles) > 0:
                        challenge_status = "VERIFIED"
                break
                    
        if challenge_status == "PENDING" and elapsed_time > CHALLENGE_TIMEOUT:
            challenge_status = "SPOOF DETECTED"

        # --- UI Graphics Overlays ---
        cv2.rectangle(frame, (0, 0), (w, 80), (30, 30, 30), -1)
        
        if challenge_status == "PENDING":
            timer_text = f"Time Left: {max(0.0, CHALLENGE_TIMEOUT - elapsed_time):.1f}s"
            cv2.putText(frame, f"CHALLENGE: {current_challenge}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2)
            cv2.putText(frame, timer_text, (w - 200, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2)
        elif challenge_status == "VERIFIED":
            cv2.putText(frame, "ACCESS GRANTED: REAL FACE", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "ACCESS DENIED: SPOOF ALERT", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
        cv2.imshow('Face Anti-Spoofing Challenge Engine', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            current_challenge = random.choice(CHALLENGES)
            start_time = time.time()
            challenge_status = "PENDING"
        elif key == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
