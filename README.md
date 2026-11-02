# Face-Recognition

Face Recognition with Raspberry Pi and OpenCV for use in the CISE Independent Study Program.

![Python](https://shields.io)
![OpenCV](https://shields.io)
![Raspberry Pi](https://shields.io)

## Overview
This project balances AI identity tracking with practical cybersecurity hardening. It utilizes a Raspberry Pi 4 and a native `Picamera2` pipeline to perform real-time face recognition against an authorized signature database. To protect the biometric perimeter from physical presentation bypass attacks, the system runs an armored state machine that enforces micro-texture analysis and randomized challenge-response liveness tracking.

---

## Setup

### Create Virtual Environment
```bash
python3 -m venv --system-site-packages face_rec
```

### Activate Environment
```bash
source face_rec/bin/activate
```

### Update System
```bash
sudo apt update
sudo apt full-upgrade
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Project Structure
```text
Face-Recognition/
├── dataset/                           # Raw image folders used for user signature training
├── intruder_alert/                    # Legacy threat notification assets
├── intruder_photos/                   # Secure local directory for forensic audit logs
├── face_rec/                          # Main project virtual environment sandbox
├── face_app.py                        # Original eye-blink liveness validation script
├── face_app_secure.py                 # Core unified cybersecurity state machine app
├── challenge_response.py              # Isolated challenge-response testing sandbox
├── facial_recognition.py              # Independent identity check script
├── facial_recognition_discord.py      # Alert integration testing script
├── image_capture.py                   # Dataset collection tool for training images
├── model_training.py                  # Script to extract facial embeddings to a pickle
├── encodings.pickle                   # Serialized database of authorized face signatures
├── haarcascade_frontalface_default.xml # Cascade parameters for facial mapping
├── haarcascade_eye.xml                # Cascade parameters for tracking profile shifts
├── haarcascade_smile.xml              # Cascade parameters for mouth dimension tracking
└── requirements.txt                   # Project software dependencies
```

---

##  Usage

### 1. Capture Training Images
Run the capture tool to gather a high-quality dataset of your face shapes under different lighting:
```bash
python image_capture.py
```

### 2. Train the Model
Extract facial coordinates and serialize them into your signature database:
```bash
python model_training.py
```

### 3. Run the Armored Access Control Console
Launch your new unified anti-spoofing application using the environment's direct runner:
```bash
uv run face_app_secure.py
```

###  Defensive Guardrails in Operation:
* **Micro-Texture Pre-Check:** The app analyzes surface standard deviation via Laplacian variance. If you hold up a flat printed photo or a phone screen, it detects the screen glare or flat grid anomaly, prints `[SPOOF DETECTED]`, and locks down immediately under a **SPOOF ALERT**.
* **Randomized Interactive Challenge:** If the system recognizes you, it triggers a random challenge (`SMILE` or `TURN LEFT OR RIGHT`). You have **6.0 seconds** to complete the movement, or the screen locks.
* **Forensic Evidence Logging:** Any failed challenge or intruder attempt automatically dumps a timestamped, red-bounded target snapshot into the `intruder_photos/` folder for secure auditing.
* **Console Refresh:** Press the **'r'** key on your keyboard at any time to clear a lockdown or authorization screen and reset the biometric perimeter back to scanning mode. Press **'q'** to quit safely.
