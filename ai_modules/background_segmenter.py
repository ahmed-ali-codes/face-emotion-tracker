import cv2
import mediapipe as mp
import numpy as np
import os
from core.app_state import app_state

class BackgroundSegmenter:
    def __init__(self):
        BaseOptions = mp.tasks.BaseOptions
        ImageSegmenter = mp.tasks.vision.ImageSegmenter
        ImageSegmenterOptions = mp.tasks.vision.ImageSegmenterOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selfie_segmenter.tflite')

        options = ImageSegmenterOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.IMAGE,
            output_category_mask=True
        )
        self.segmenter = ImageSegmenter.create_from_options(options)
        
    def apply_filter(self, frame, original_frame=None):
        detect_frame = original_frame if original_frame is not None else frame
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
            rgb_frame = cv2.cvtColor(detect_frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            try:
                result = self.segmenter.segment(mp_image)
            except Exception as e:
                print("Segmentation error:", e)
                return frame
            
            # The category_mask contains 0 for background and 1 for person
            mask = result.category_mask.numpy_view()
            mask = np.squeeze(mask) # Ensure mask is (H, W) and not (H, W, 1)
            
            # Create a condition (some segmenter models output 0 for person, >0 for background)
            condition = np.stack((mask,) * 3, axis=-1) > 0.1
            
            # Create a blurred version of the original frame
            blurred_bg = cv2.GaussianBlur(frame, (55, 55), 0)
            
            # Combine the sharp foreground and blurred background
            # If condition is True (background), use blurred_bg. Otherwise (person), use frame.
            return np.where(condition, blurred_bg, frame)
            
        return frame
