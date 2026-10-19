import cv2
import os
from datetime import datetime
from picamera2 import Picamera2
import time

# Change this to the name of the person you're photographing
PERSON_NAME = "amanda"  

def create_folder(name):
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)
    
    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photos(name):
    folder = create_folder(name)
    
    picam2 = Picamera2()
    config =picam2.create_preview_configuration(
       main={"format": "RGB888", "size": (640,480)}
       )
    picam2.configure(config)
    picam2.start()
    t       ime.sleep(2) #warm up
    photo_count = 0
    
    print(f"Taking photos for {name}. Press SPACE to capture, 'q' to quit.")
    
    while True:
        # Capture frame from Pi Camera
        frame = picam2.capture_array()
        
        # Display the frame
        cv2.imshow('Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space key
            photo_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            cv2.imwrite(filepath, frame)
            print(f"Photo {photo_count} saved: {filepath}")
        
        elif key == ord('q'):  # Q key
            break
    
    # Clean up
    cv2.destroyAllWindows()
    picam2.stop()
    print(f"Photo capture completed. {photo_count} photos saved for {name}.")

if __name__ == "__main__":
    capture_photos(PERSON_NAME)
    