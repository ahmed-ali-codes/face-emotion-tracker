import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.camera import Camera
from ai_modules.face_tracker import FaceTracker
from ai_modules.gesture_tracker import GestureTracker
from ai_modules.background_segmenter import BackgroundSegmenter
from ui.window import SmartCameraWindow
from core.app_state import app_state

def main():
    print("🚀 Starting Advanced Smart Camera...")
    
    # Initialize Camera
    camera = Camera(0)
    
    # Initialize AI Modules
    face_tracker = FaceTracker()
    gesture_tracker = GestureTracker()
    background_segmenter = BackgroundSegmenter()
    
    # Initialize GUI
    window = SmartCameraWindow(camera, face_tracker, gesture_tracker, background_segmenter)
    
    # Start app loop
    window.start()

if __name__ == "__main__":
    main()
