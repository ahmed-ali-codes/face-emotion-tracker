import cv2
import threading
import time
from core.app_state import app_state

class Camera:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"❌ Camera {camera_index} not detected!")
        
        self.current_frame = None
        self._lock = threading.Lock()
        
        # Start a thread to continuously read frames
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        while app_state.is_running():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            # Flip horizontally for selfie-view
            frame = cv2.flip(frame, 1)

            with self._lock:
                self.current_frame = frame
                
            time.sleep(0.01)

    def get_frame(self):
        with self._lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
            return None

    def release(self):
        app_state.set_running(False)
        self.thread.join(timeout=2.0)
        self.cap.release()
