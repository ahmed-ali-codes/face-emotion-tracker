import cv2
import mediapipe as mp
import numpy as np
from core.app_state import app_state

class BackgroundSegmenter:
    def __init__(self):
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.segmentation = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        
    def apply_filter(self, frame):
        current_filter = app_state.current_filter
        
        if current_filter == "Normal":
            return frame
            
        elif current_filter == "Black & White":
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
        elif current_filter == "Thermal":
            # Apply a colormap to simulate thermal vision
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            return thermal
            
        elif current_filter == "Background Blur":
            # Apply Virtual Green Screen (Blur background)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.segmentation.process(rgb_frame)
            
            # Create a mask where people are
            condition = np.stack((result.segmentation_mask,) * 3, axis=-1) > 0.1
            
            # Create a blurred version of the original frame
            blurred_bg = cv2.GaussianBlur(frame, (55, 55), 0)
            
            # Combine the sharp foreground and blurred background
            return np.where(condition, frame, blurred_bg)
            
        return frame
