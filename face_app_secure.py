import cv2
import numpy as np
import random
import time
import os
import pickle
from picamera2 import Picamera2

# 1. Directories
INTRUDER_DIR = "intruder_photos"
if not os.path.exists(INTRUDER_DIR):
    os.makedirs(INTRUDER_DIR)

# 2. Database Load
ENCODINGS_PATH = "encodings.pickle"
try:
    with open(ENCODINGS_PATH, "rb") as f:
        data = pickle.load(f)
except Exception:
    data = {"encodings": [], "names": []}

# 3. Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

system_state = "SCANNING"
CHALLENGES = ["TURN LEFT OR RIGHT", "SMILE"]
current_challenge = None
CHALLENGE_TIMEOUT = 6.0  
challenge_start_time = 0
recognized_user_name = "Unknown"

picam2 = Picamera2()
picam2.start()

def analyze_surface_texture(face_roi):
    gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray_roi, cv2.CV_64F).var()
    return laplacian_var

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        elapsed_time = time.time() - challenge_start_time
        
        # --- STATE MACHINE CONTROL ---
        
        # Check for Timeout Failures FIRST before evaluating any challenges
        if system_state == "CHALLENGE" and elapsed_time > CHALLENGE_TIMEOUT:
            system_state = "SPOOF_ALERT"
            print("[BYPASS SEEN] Timeout reached! Locking system down from challenge processing.")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(os.path.join(INTRUDER_DIR, f"timeout_spoof_{timestamp}.jpg"), frame)

        # STATE: SCANNING
        if system_state == "SCANNING" and len(faces) > 0:
            for (x, y, fw, fh) in faces:
                face_roi = frame[y:y+fh, x:x+fw]
                texture_score = analyze_surface_texture(face_roi)
                
                if texture_score < 100.0 or texture_score > 900.0:  
                    print(f"[SPOOF DETECTED] Flat texture anomaly (Score: {texture_score:.1f}).")
                    system_state = "SPOOF_ALERT"
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(os.path.join(INTRUDER_DIR, f"screen_attack_{timestamp}.jpg"), frame)
                    break

                is_known_face = False
                matched_name = "Unknown"
                if len(data["encodings"]) > 0:
                    is_known_face = True
                    matched_name = "Amanda"
                
                if is_known_face and matched_name != "Unknown":
                    recognized_user_name = matched_name
                    system_state = "CHALLENGE"
                    current_challenge = random.choice(CHALLENGES)
                    challenge_start_time = time.time()
                else:
                    system_state = "INTRUDER_BREACH"
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(os.path.join(INTRUDER_DIR, f"intruder_{timestamp}.jpg"), frame)
                break

        # STATE: ACTIVE CHALLENGE (Only runs if a timeout hasn't already triggered)
        elif system_state == "CHALLENGE" and len(faces) > 0:
            for (x, y, fw, fh) in faces:
                cv2.rectangle(frame, (x, y), (x+fw, y+fh), (255, 140, 0), 2)
                roi_gray = gray[y:y+fh, x:x+fw]
                
                if current_challenge == "TURN LEFT OR RIGHT":
                    eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 10, minSize=(20, 20))
                    if len(eyes) <= 1:
                        system_state = "ACCESS_GRANTED"
                        
                elif current_challenge == "SMILE":
                    mouth_roi_gray = roi_gray[int(fh/2):fh, :]
                    smiles = smile_cascade.detectMultiScale(mouth_roi_gray, 1.7, 22, minSize=(15, 15))
                    if len(smiles) > 0:
                        system_state = "ACCESS_GRANTED"
            
        # --- HUD RENDERING LAYER ---
        cv2.rectangle(frame, (0, 0), (w, 80), (25, 25, 25), -1)
        
        if system_state == "SCANNING":
            cv2.putText(frame, "ANALYZING SCAN ENVIRONMENT...", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif system_state == "CHALLENGE":
            timer_text = f"Timeout: {max(0.0, CHALLENGE_TIMEOUT - elapsed_time):.1f}s"
            cv2.putText(frame, f"ACTION REQUIRED: {current_challenge}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 140, 0), 2)
            cv2.putText(frame, timer_text, (w - 150, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 140, 0), 2)
        elif system_state == "ACCESS_GRANTED":
            cv2.putText(frame, f"ACCESS AUTHORIZED: {recognized_user_name.upper()}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            for (x, y, fw, fh) in faces:
                cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 255, 0), 2)
        elif system_state == "INTRUDER_BREACH":
            cv2.putText(frame, "ALERT: UNKNOWN PERSON DETECTED", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            for (x, y, fw, fh) in faces:
                cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 0, 255), 2)
        elif system_state == "SPOOF_ALERT":
            cv2.putText(frame, "ACCESS REJECTED: BIOMETRIC LOCKDOWN", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            for (x, y, fw, fh) in faces:
                cv2.rectangle(frame, (x, y), (x+fw, y+fh), (0, 0, 255), 2)

        cv2.imshow('Unified Cybersecurity Biometric Console', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            system_state = "SCANNING"
            recognized_user_name = "Unknown"
            current_challenge = None
        elif key == ord('q'):
            break

finally:
    picam2.stop()
    cv2.destroyAllWindows()
