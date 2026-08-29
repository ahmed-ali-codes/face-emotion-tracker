import cv2
import threading
import os
import face_recognition
import tensorflow as tf
from deepface import DeepFace
from core.app_state import app_state
from integrations.security_notifier import trigger_security_alert

class FaceTracker:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self._load_reference_faces()
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.frame_count = 0
        self.last_emotion = "Neutral"
        self._emotion_thread = None

    def _load_reference_faces(self):
        # Create dir if not exists
        ref_dir = "reference_faces"
        os.makedirs(ref_dir, exist_ok=True)
        
        for filename in os.listdir(ref_dir):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                filepath = os.path.join(ref_dir, filename)
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    name = os.path.splitext(filename)[0]
                    self.known_face_names.append(name)
        print(f"Loaded {len(self.known_face_names)} reference faces.")

    def _analyze_emotion_thread(self, face_img):
        try:
            # Analyze emotion using DeepFace
            # enforce_detection=False to avoid crashing if it doesn't clearly see a face
            result = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False, silent=True)
            if isinstance(result, list):
                result = result[0]
            emotion = result.get('dominant_emotion', 'Neutral').capitalize()
            self.last_emotion = emotion
            app_state.update_emotion(emotion)
        except Exception as e:
            pass

    def process_frame(self, frame):
        self.frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Fast face detection using Haar Cascades
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

        # We will only run heavy Recognition/Emotion on every 30th frame or so
        run_heavy_ai = (self.frame_count % 30 == 0)

        for (x, y, w, h) in faces:
            # Draw box
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            face_img = frame[y:y+h, x:x+w]
            
            name = "Unknown"
            
            if run_heavy_ai:
                # 1. Face Recognition
                rgb_frame = cv2.cvtColor(frame, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                # optimize by using just the face box
                rgb_face = rgb_frame[y:y+h, x:x+w]
                face_encodings = face_recognition.face_encodings(rgb_frame, [(y, x+w, y+h, x)])
                
                if face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encodings[0])
                    if True in matches:
                        first_match_index = matches.index(True)
                        name = self.known_face_names[first_match_index]
                    else:
                        name = "Unknown"
                        if app_state.security_mode:
                            # Trigger alert in background
                            trigger_security_alert(frame.copy())
                            
                # 2. Emotion Detection in background thread to avoid freezing UI
                if self._emotion_thread is None or not self._emotion_thread.is_alive():
                    self._emotion_thread = threading.Thread(target=self._analyze_emotion_thread, args=(face_img.copy(),))
                    self._emotion_thread.start()

            # Display text
            display_text = f"{name} - {self.last_emotion}"
            cv2.putText(frame, display_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        return frame
