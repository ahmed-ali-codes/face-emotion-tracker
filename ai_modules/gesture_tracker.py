import cv2
import mediapipe as mp
import time
import os
from core.app_state import app_state

class GestureTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.last_swipe_time = 0
        self.last_x = None
        self.last_peace_time = 0

    def is_peace_sign(self, hand_landmarks):
        # Index and middle finger tips are above their respective PIP joints
        index_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        
        middle_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        middle_pip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        
        ring_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP].y
        ring_pip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_PIP].y
        
        pinky_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP].y
        pinky_pip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_PIP].y

        if (index_tip_y < index_pip_y and middle_tip_y < middle_pip_y and 
            ring_tip_y > ring_pip_y and pinky_tip_y > pinky_pip_y):
            return True
        return False

    def take_screenshot(self, frame):
        os.makedirs("screenshots", exist_ok=True)
        filename = f"screenshots/screenshot_{int(time.time())}.png"
        cv2.imwrite(filename, frame)
        print(f"📸 Screenshot saved to {filename}")

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                # Check for Peace Sign
                if self.is_peace_sign(hand_landmarks):
                    current_time = time.time()
                    if current_time - self.last_peace_time > 2.0:  # 2 second cooldown
                        self.take_screenshot(frame)
                        self.last_peace_time = current_time
                        cv2.putText(frame, "SCREENSHOT SAVED", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                # Check for Swipe Gesture (track index finger tip X position)
                index_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x
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
