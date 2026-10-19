import cv2
import time
from picamera2 import Picamera2

def test_pi_camera():
    print("Loading OpenCV Anti-Spoofing Cascades...")
    # Load built-in pre-trained Haar Cascades
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    print("Initializing camera pipeline...")
    picam2 = Picamera2()
    picam2.start()
    
    print("Camera pipeline Successfully initialized! press 'q' to exit.")
    
    # Anti-spoofing tracking variables
    blink_detected = False
    eyes_were_visible = False
    last_blink_time = 0
    
    while True:
        # Capture raw frame array (Native RGB)
        frame = picam2.capture_array()
        
        # OpenCV cascades require grayscale images for rapid scanning
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # 1. Detect faces first to narrow down the eye search area
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        eyes_found_this_frame = False
        
        for (x, y, w, h) in faces:
            # Draw a box around the face boundary
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
            
            # Slice out the face region of interest (ROI) specifically for eyes
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # 2. Scan for eyes inside the face region
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=10, minSize=(15, 15))
            
            if len(eyes) >= 2:
                eyes_found_this_frame = True
                # Draw boxes around the detected eyes
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 255), 2)
        
        # 3. Dynamic Liveness Logic: Look for the rapid open -> closed -> open state transitions
        if eyes_found_this_frame:
            eyes_were_visible = True
        else:
            # If eyes were open on previous frames but suddenly disappeared, a blink is occurring
            if eyes_were_visible and len(faces) > 0:
                blink_detected = True
                last_blink_time = time.time()
                eyes_were_visible = False
        
        # Expire the verified state status after 4 seconds to require ongoing interaction
        if blink_detected and (time.time() - last_blink_time > 4.0):
            blink_detected = False
            
        # Convert raw frame to clean BGR format for display output
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Render the visual anti-spoofing banner text onto the screen window
        status_text = "Liveness: VERIFIED (Human)" if blink_detected else "Liveness: PENDING (Blink Your Eyes)"
        color = (0, 255, 0) if blink_detected else (0, 0, 255)
        cv2.putText(display_frame, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Display live camera stream view
        cv2.imshow("Pi Camera Feed", display_frame)
        
        # Clear out safely if 'q' is pressed on keyboard
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_pi_camera()
import numpy as np
from picamera2 import Picamera2
import mediapipe as mp


#  Bypass the top-level namespace by importing the sub-module path directly
from mediapipe.python.solutions import face_mesh as mp_face_mesh

#  Instantiate the model object using the direct sub-module
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Specific landmark indexes for the left eye in MediaPipe
LEFT_EYE_TOP_BOTTOM = [159, 145, 158, 153]  # Vertical tracking pairs
LEFT_EYE_LEFT_RIGHT = [33, 133]             # Horizontal corners tracking

def calculate_ear(landmarks, vertical_idx, horizontal_idx, width, height):
    # Convert normalized landmarks to physical pixel coordinates
    v_coords = [(int(landmarks[i].x * width), int(landmarks[i].y * height)) for i in vertical_idx]
    h_coords = [(int(landmarks[i].x * width), int(landmarks[i].y * height)) for i in horizontal_idx]
    
    # Calculate vertical eye distance
    v1 = np.linalg.norm(np.array(v_coords[0]) - np.array(v_coords[1]))
    v2 = np.linalg.norm(np.array(v_coords[2]) - np.array(v_coords[3]))
    
    # Calculate horizontal eye distance
    h = np.linalg.norm(np.array(h_coords[0]) - np.array(h_coords[1]))
    
    # Eye Aspect Ratio formula
    ear = (v1 + v2) / (2.0 * h)
    return ear

def test_pi_camera():
    print("Initializing camera pipeline with Anti-Spoofing...")
    picam2 = Picamera2()
    picam2.start()
    
    print("Camera pipeline Successfully initialized! press 'q' to exit.")
    
    # Tracking states
    blink_counter = 0
    liveness_verified = False
    EAR_THRESHOLD = 0.21  # Anything below this is registered as an eye blink
    
    while True:
        # Capture raw frame array (Native RGB)
        frame = picam2.capture_array()
        h, w, _ = frame.shape
        
        # Process frame with MediaPipe (requires RGB)
        results = face_mesh.process(frame)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Calculate EAR value
            left_ear = calculate_ear(landmarks, LEFT_EYE_TOP_BOTTOM, LEFT_EYE_LEFT_RIGHT, w, h)
            
            # Run eye blink verification logic
            if left_ear < EAR_THRESHOLD:
                blink_counter += 1
            else:
                if blink_counter >= 1:  # Register the quick blink drop
                    liveness_verified = True
                    blink_counter = 0
        
        # Convert RGB to BGR for clean OpenCV window colors
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Render visual status banner onto screen
        status_text = "Liveness: VERIFIED (Human)" if liveness_verified else "Liveness: PENDING (Blink Needed)"
        color = (0, 255, 0) if liveness_verified else (0, 0, 255)
        cv2.putText(display_frame, status_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Display live camera frame window
        cv2.imshow("Pi Camera Feed", display_frame)
        
        # Quit window safely if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_pi_camera()
