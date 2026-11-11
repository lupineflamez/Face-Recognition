# Face-Recognition Framework with Anti-Spoofing and Active Challenge-Response

Face Recognition with Raspberry Pi and OpenCV for use in the CISE Independent Study Program.

![Python](https://shields.io)
![OpenCV](https://shields.io)
![Raspberry Pi](https://shields.io)

## Project Genesis and Architectural Evolution
The structural codebase utilized in this framework was originally forked from a collaborative, multi-authored repository developed as part of a group project phase. The initial prototype focused strictly on baseline 1:1 facial matching routines without environmental auditing or operational vulnerability parameters.

This repository completely re-engineers that shared baseline into an independent, secure endpoint application. Key individual expansions include the implementation of a dedicated finite state machine (`SCANNING`, `CHALLENGE`, `ACCESS_GRANTED`, `INTRUDER_BREACH`, `SPOOF_ALERT`), automated passive surface texture filtering, randomized active behavioral challenge checks, dynamic user identification mapping, and a millisecond-accurate event-driven performance tracking engine.

---

## The DAR Framework Design
The pipeline organizes the biometric authentication lifecycle into three distinct, auditing execution pillars:

1. **Detect (Spatial Allocation):** Isolates the primary facial region coordinates to define a tight bounding canvas as a Region of Interest (ROI):
   \[R_{face} = \{x, y, w, h\}\]
2. **Analyze (Liveness Validation):** Executes a two-tiered anti-spoofing workflow:
   * **Passive Verification:** Monitors the spatial variance of a discrete Laplacian kernel response (σ²) to identify flat surface configurations, instantly blocking printed photograph or digital screen presentation attacks (PAs).
   * **Active Verification:** Enforces a time-bounded challenge-response verification sequence (\(T_{timeout} = 6.0\text{ s}\)) that randomly requires the user to perform an interactive physical action (e.g., turning away or smiling), validated via localized eye and mouth sub-cascades.
3. **Recognize (Identity Resolution):** Performs dynamic profile lookup against an isolated local storage matrix (`encodings.pickle`) to authorize verified users while running isolated forensic handlers for system breaches.

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
├── intruder_photos/                   # Secure local directory for forensic audit logs (lossless .png)
├── face_rec/                          # Main project virtual environment sandbox
├── face_app.py                        # Original eye-blink liveness validation script
├── face_app_secure.py                 # Core unified cybersecurity state machine and metric engine
├── challenge_response.py              # Isolated challenge-response testing sandbox
├── facial_recognition.py              # Independent identity check script
├── facial_recognition_discord.py      # Alert integration testing script
├── image_capture.py                   # Dataset collection tool for training images
├── model_training.py                  # Script to extract facial embeddings to a pickle
├── encodings.pickle                   # Serialized database of authorized face signatures
├── haarcascade_frontalface_default.xml # Cascade parameters for facial mapping
├── haarcascade_eye.xml                # Cascade parameters for tracking profile shifts
├── haarcascade_smile.xml              # Cascade parameters for mouth dimension tracking
├── performance_log.csv                # Granular, event-driven benchmark performance dataset
└── requirements.txt                   # Project software dependencies
```

---

## Usage

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
Launch your unified anti-spoofing application using the environment's direct runner:
```bash
python3 face_app_secure.py
```

---

## Defensive Guardrails and Auditing in Operation
* **Micro-Texture Pre-Check:** The app analyzes surface standard deviation via Laplacian variance. If a flat printed photo or a phone screen is held up, it detects the uniform variance anomaly, prints `[SPOOF DETECTED]`, logs a `TEXTURE_SPOOF_BLOCKED` event, and locks down the environment immediately.
* **Randomized Interactive Challenge:** If the system recognizes an authorized user, it triggers a random challenge (`SMILE` or `TURN LEFT OR RIGHT`). The user has **6.0 seconds** to complete the action, or the system registers a `TIMEOUT_EXPIRATION` event and initiates lockdown.
* **Granular Performance Metrics:** An event-driven data logger tracks processing efficiency by capturing microsecond timestamps and instantaneous frame rates (`Recorded FPS`) at every key switch, outputting metrics directly to `performance_log.csv`.
* **Lossless Forensic Snapshots:** Any failed challenge, timeout bypass, or intruder breach automatically flags the frame, paints a pure red boundary box `(0, 0, 255)` around the target, and writes a crisp, high-fidelity capture in **PNG format** to the `intruder_photos/` folder to prevent lossy JPEG artifact compression from damaging texture evidence.
* **Console Control:** Press the **'r'** key on your keyboard at any time to clear a lockdown or authorization screen and reset the system back to scanning mode. Press **'q'** to save all logs and quit safely.
