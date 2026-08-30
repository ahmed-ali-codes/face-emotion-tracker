import cv2
import mediapipe as mp
import time
import os
from core.app_state import app_state

class GestureTracker:
    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # Determine path to the downloaded model
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        
        self.last_swipe_time = 0
        self.last_x = None
        self.last_peace_time = 0

    def is_peace_sign(self, hand_landmarks):
        # Index and middle finger tips are above their respective PIP joints
        # MediaPipe Task API landmarks are indexed 0-20
        index_tip_y = hand_landmarks[8].y
        index_pip_y = hand_landmarks[6].y
        
        middle_tip_y = hand_landmarks[12].y
        middle_pip_y = hand_landmarks[10].y
        
        ring_tip_y = hand_landmarks[16].y
        ring_pip_y = hand_landmarks[14].y
        
        pinky_tip_y = hand_landmarks[20].y
        pinky_pip_y = hand_landmarks[18].y

        if (index_tip_y < index_pip_y and middle_tip_y < middle_pip_y and 
            ring_tip_y > ring_pip_y and pinky_tip_y > pinky_pip_y):
            return True
        return False

    def take_screenshot(self, frame):
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/screenshot_{int(time.time())}.png"
        cv2.imwrite(filename, frame)
        print(f"📸 Screenshot saved to {filename}")

    def process_frame(self, frame, original_frame=None):
        detect_frame = original_frame if original_frame is not None else frame
        # MediaPipe tasks requires mp.Image
        rgb_frame = cv2.cvtColor(detect_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        try:
            result = self.landmarker.detect(mp_image)
        except Exception as e:
            print("Gesture tracking error:", e)
            return frame

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                # Draw landmarks manually since we don't have mp.solutions.drawing_utils
                for lm in hand_landmarks:
                    x = int(lm.x * frame.shape[1])
                    y = int(lm.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                
                # Check for Peace Sign
                if self.is_peace_sign(hand_landmarks):
                    current_time = time.time()
                    if current_time - self.last_peace_time > 2.0:  # 2 second cooldown
                        self.take_screenshot(frame)
                        self.last_peace_time = current_time
                        cv2.putText(frame, "SCREENSHOT SAVED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Check for Swipe Gesture (track index finger tip X position)
                index_x = hand_landmarks[8].x
                current_time = time.time()
                
                if self.last_x is not None:
                    delta_x = index_x - self.last_x
                    if current_time - self.last_swipe_time > 1.0: # 1 sec cooldown
                        if delta_x > 0.15: # Swiped right
                            app_state.next_filter()
                            self.last_swipe_time = current_time
                        elif delta_x < -0.15: # Swiped left
                            app_state.prev_filter()
                            self.last_swipe_time = current_time
                self.last_x = index_x
        else:
            self.last_x = None

        return frame
